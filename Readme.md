# ⚡ Self-Custodial Lightning Escrow

A non-custodial escrow system built on the Bitcoin Lightning Network using **LND Hold Invoices**.

This project enables trust-minimized payments between clients and freelancers by locking funds in an HTLC until work is completed or refunded.

---

## 🧩 Problem

Freelancers and clients often lack trust:

- Clients fear paying before work is delivered.
- Freelancers fear completing work without guaranteed payment.
- Traditional escrow services are custodial and expensive.

This project solves that using native Lightning primitives.

---

## 🚀 Solution

We implement an escrow mechanism using **LND Hold Invoices**.

Funds are:

- Locked in an HTLC
- Not immediately settled
- Released only when conditions are met
- Refundable if the agreement fails

No multisig scripts.  
No custodial wallets.  
No third-party fund seizure.

Pure Lightning.

---

## 🔄 Escrow Flow

Client → Requests job  
Freelancer → Accepts  
Escrow Service → Generates HOLD invoice  
Client → Pays invoice  
Funds locked in HTLC

Work completed?  
YES → Escrow settles → Freelancer paid  
NO  → Escrow cancels → Client refunded

---

## ⚙️ How It Works

### 1️⃣ Job Creation

Client submits:
- Job description
- Payment amount (in sats)

Escrow service generates a **Hold Invoice** using LND.

---

### 2️⃣ Funding Escrow

Client pays the invoice.

The invoice enters:
- `ACCEPTED` state
- Funds locked in HTLC
- Not yet settled

At this stage:
- Funds cannot be claimed
- Funds are not released
- Timeout refund is still possible

---

### 3️⃣ Work Completion (Release Funds)

If the freelancer completes the job:

Escrow Service calls:

SettleInvoice(preimage)

Result:
- HTLC resolves
- Funds transferred to freelancer

---

### 4️⃣ Refund

If the agreement fails:

Escrow Service calls:

CancelInvoice(payment_hash)

Result:
- HTLC canceled
- Funds returned to client

---

## 🏗 Architecture

Frontend (Client + Freelancer UI)
↓
Flask Backend
↓
LND gRPC (Hold Invoice API)
↓
Lightning Network (HTLC Lock)

---

## 🛠 Tech Stack

- Python (Flask)
- LND (Polar / Regtest)
- gRPC
- SQLite (Job tracking)
- Docker (via Polar)

---

## 🎯 MVP Features

- Create escrow job
- Generate hold invoice
- Detect invoice funded
- Release payment
- Refund payment
- Track job status

---

## 🏆 Why This Matters

This demonstrates:

- Real Lightning primitives (HTLC control)
- Trust-minimized escrow
- Non-custodial payment flow
- Practical freelance use case

Built for hackathon demonstration in a regtest environment.

---

# 🛠 Setup & Installation

Follow these steps to run the Lightning Escrow CLI locally.

---

## 1️⃣ Prerequisites

- Python 3.10+
- Polar (running in Regtest)
- LND node running inside Polar
- Access to:
    - `tls.cert`
    - `admin.macaroon`
- gRPC port exposed (typically `10001`)

---

## 2️⃣ Clone Project

```bash
git clone <your-repo-url>
cd Escrow-Flow