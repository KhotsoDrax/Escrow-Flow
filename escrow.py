import sys
import sqlite3
import grpc
import codecs
import hashlib
import os
import threading
import time

import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc


# ---------------- CONFIG ---------------- #

LND_HOST = "localhost:10001"
TLS_CERT_PATH = "tls.cert"
MACAROON_PATH = "admin.macaroon"

# ---------------------------------------- #


# ---------- DATABASE ---------- #

conn = sqlite3.connect("db.sqlite", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS jobs (
                                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   description TEXT,
                                                   amount INTEGER,
                                                   payment_request TEXT,
                                                   r_hash TEXT,
                                                   preimage TEXT,
                                                   status TEXT
               )
               """)
conn.commit()


# ---------- LND CONNECTION ---------- #

def get_stub():
    with open(TLS_CERT_PATH, 'rb') as f:
        cert = f.read()

    ssl_creds = grpc.ssl_channel_credentials(cert)

    with open(MACAROON_PATH, 'rb') as f:
        macaroon = codecs.encode(f.read(), 'hex')

    def metadata_callback(context, callback):
        callback([('macaroon', macaroon.decode())], None)

    auth_creds = grpc.metadata_call_credentials(metadata_callback)
    creds = grpc.composite_channel_credentials(ssl_creds, auth_creds)

    channel = grpc.secure_channel(LND_HOST, creds)
    return lnrpc.LightningStub(channel)


# ---------- INVOICE MONITOR ---------- #

def monitor_invoices():
    stub = get_stub()
    request = ln.InvoiceSubscription()

    print("🔎 Listening for invoice updates...")

    for invoice in stub.SubscribeInvoices(request):
        r_hash_hex = invoice.r_hash.hex()

        job = cursor.execute(
            "SELECT id, status FROM jobs WHERE r_hash = ?",
            (r_hash_hex,)
        ).fetchone()

        if not job:
            continue

        job_id, current_status = job

        # ACCEPTED = HTLC locked (funded but not settled)
        if invoice.state == ln.Invoice.ACCEPTED and current_status == "PENDING":
            cursor.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                ("FUNDED", job_id)
            )
            conn.commit()
            print(f"💰 Job {job_id} funded. HTLC locked.")

        # SETTLED = released
        if invoice.state == ln.Invoice.SETTLED:
            cursor.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                ("RELEASED", job_id)
            )
            conn.commit()
            print(f"✅ Job {job_id} settled.")

        # CANCELED = refunded
        if invoice.state == ln.Invoice.CANCELED:
            cursor.execute(
                "UPDATE jobs SET status = ? WHERE id = ?",
                ("REFUNDED", job_id)
            )
            conn.commit()
            print(f"↩ Job {job_id} refunded.")


# ---------- ESCROW FUNCTIONS ---------- #

def create_job(description, amount):
    stub = get_stub()

    preimage = os.urandom(32)
    r_hash = hashlib.sha256(preimage).digest()

    invoice = ln.Invoice(
        memo=description,
        value=int(amount),
        r_hash=r_hash
    )

    response = stub.AddHoldInvoice(invoice)

    cursor.execute("""
                   INSERT INTO jobs (description, amount, payment_request, r_hash, preimage, status)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """, (
                       description,
                       amount,
                       response.payment_request,
                       r_hash.hex(),
                       preimage.hex(),
                       "PENDING"
                   ))

    conn.commit()

    print("\n📝 Escrow Created")
    print("Invoice:\n", response.payment_request)
    print("\nShare this invoice with the client.\n")


def list_jobs():
    rows = cursor.execute("SELECT * FROM jobs").fetchall()

    print("\n📋 Escrow Jobs:")
    for row in rows:
        print(f"""
ID: {row[0]}
Description: {row[1]}
Amount: {row[2]} sats
Status: {row[6]}
""")


def release_job(job_id):
    stub = get_stub()

    job = cursor.execute(
        "SELECT preimage, status FROM jobs WHERE id = ?",
        (job_id,)
    ).fetchone()

    if not job:
        print("❌ Job not found.")
        return

    if job[1] != "FUNDED":
        print("⚠ Job not funded yet.")
        return

    stub.SettleInvoice(
        ln.SettleInvoiceMsg(preimage=bytes.fromhex(job[0]))
    )

    print("🚀 Release initiated.")


def refund_job(job_id):
    stub = get_stub()

    job = cursor.execute(
        "SELECT r_hash, status FROM jobs WHERE id = ?",
        (job_id,)
    ).fetchone()

    if not job:
        print("❌ Job not found.")
        return

    if job[1] != "FUNDED":
        print("⚠ Job not funded yet.")
        return

    stub.CancelInvoice(
        ln.CancelInvoiceMsg(
            payment_hash=bytes.fromhex(job[0])
        )
    )

    print("↩ Refund initiated.")


# ---------- CLI ---------- #

if __name__ == "__main__":

    # Start background invoice listener
    monitor_thread = threading.Thread(target=monitor_invoices, daemon=True)
    monitor_thread.start()

    time.sleep(1)

    if len(sys.argv) < 2:
        print("""
Usage:
  python escrow.py create "Description" amount_sats
  python escrow.py list
  python escrow.py release job_id
  python escrow.py refund job_id
""")
        sys.exit(0)

    command = sys.argv[1]

    if command == "create":
        create_job(sys.argv[2], int(sys.argv[3]))

    elif command == "list":
        list_jobs()

    elif command == "release":
        release_job(int(sys.argv[2]))

    elif command == "refund":
        refund_job(int(sys.argv[2]))

    else:
        print("Unknown command.")

    # Keep process alive so invoice monitor runs
    while True:
        time.sleep(5)
