import os
import sys
import json
import time
import requests
from pathlib import Path

# -------------------
# CONFIG - UPDATE
# -------------------
NODE_REST = "https://127.0.0.1:8081"  # Polar REST host
TLS_CERT = r"C:\Users\Khotso Meje\.polar\networks\1\volumes\lnd\alice\tls.cert"
MACAROON = r"C:\Users\Khotso Meje\.polar\networks\1\volumes\lnd\alice\data\chain\bitcoin\regtest\admin.macaroon"

ESCROW_DB = "escrows.json"

# -------------------
# SESSION
# -------------------
session = requests.Session()
session.verify = TLS_CERT
with open(MACAROON, "rb") as f:
    macaroon_hex = f.read().hex()
session.headers.update({"Grpc-Metadata-macaroon": macaroon_hex})

# -------------------
# DB
# -------------------
def load_db():
    if not Path(ESCROW_DB).exists():
        return {}
    with open(ESCROW_DB, "r") as f:
        return json.load(f)

def save_db(data):
    with open(ESCROW_DB, "w") as f:
        json.dump(data, f, indent=4)

# -------------------
# ESCROW LOGIC
# -------------------
def create_escrow(amount_sat, memo):
    url = f"{NODE_REST}/v1/invoices"
    payload = {"value": amount_sat, "memo": memo, "expiry": 3600, "private": True, "cltv_expiry": 40, "settle_blocking": False}
    res = session.post(url, json=payload, verify=TLS_CERT)
    data = res.json()
    db = load_db()
    db[data["r_hash"]] = {"amount": amount_sat, "memo": memo, "payment_request": data["payment_request"], "state": "LOCKED", "created_at": int(time.time())}
    save_db(db)
    print("Escrow created!")
    print("Payment Request:", data["payment_request"])

def list_escrows():
    db = load_db()
    if not db:
        print("No escrows found.")
        return
    for h, d in db.items():
        print("\n------------------")
        print("Payment Hash:", h)
        print("Amount:", d["amount"])
        print("Memo:", d["memo"])
        print("State:", d["state"])

def release_escrow(r_hash):
    url = f"{NODE_REST}/v1/invoice/settle"
    payload = {"preimage": r_hash}  # In REST, you normally provide the preimage here
    res = session.post(url, json=payload, verify=TLS_CERT)
    db = load_db()
    if r_hash in db:
        db[r_hash]["state"] = "RELEASED"
        save_db(db)
        print("Escrow released!")
    else:
        print("Escrow not found.")

def refund_escrow(r_hash):
    url = f"{NODE_REST}/v1/invoice/cancel"
    payload = {"payment_hash": r_hash}
    res = session.post(url, json=payload, verify=TLS_CERT)
    db = load_db()
    if r_hash in db:
        db[r_hash]["state"] = "REFUNDED"
        save_db(db)
        print("Escrow refunded!")
    else:
        print("Escrow not found.")

# -------------------
# CLI
# -------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: create/list/release/refund")
        return
    cmd = sys.argv[1]
    if cmd == "create":
        create_escrow(int(sys.argv[2]), sys.argv[3])
    elif cmd == "list":
        list_escrows()
    elif cmd == "release":
        release_escrow(sys.argv[2])
    elif cmd == "refund":
        refund_escrow(sys.argv[2])
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
