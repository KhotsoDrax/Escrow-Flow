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
- Clients to pay freelancers into a **HOLD invoice**
- Funds are locked in the Lightning Network (HTLC)
- Escrow can **release** funds to freelancer or **refund** client

This version uses **REST API** for simplicity — no proto files or gRPC required.

---

## How It Works

1. **Client requests a job**
2. **Freelancer accepts**
3. **Escrow Service generates a HOLD invoice**
4. **Client pays the invoice** → Funds are locked in HTLC
5. **Work completed?**
  - YES → Escrow releases → Freelancer paid
  - NO → Escrow cancels → Client refunded

The escrow state is saved in `escrows.json` so you can track all locked funds.

---

## Features

- Create escrow (HOLD invoice)
- List current escrows
- Release escrow (settle invoice)
- Refund escrow (cancel invoice)
- CLI-only interface, works on Windows, Linux, MacOS

---

## Requirements

- Python 3.11+
- Docker Desktop
- Polar (LND + Bitcoin regtest network)
- PowerShell (Windows) or Terminal (Linux/MacOS)

---

## File Structure

---

LightningEscrow/
│

├── venv/ # Python virtual environment

├── escrow.py # Main CLI app

├── setup.ps1 # One-command setup script

├── escrows.json # Escrow database (auto-created)

└── README.md # This file

---

## 🛠 Tech Stack

- Python venv
- LND (Polar / Regtest)
- RestAPI's
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

## Setup

### 1️⃣ Clone Project

```powershell
git clone https://github.com/KhotsoDrax/Escrow-Flow.git
cd LightningEscrow

cd Escrow-Flow

2️⃣ Run Setup Script (Windows)

This script will:

Create and activate a Python virtual environment

Install required dependencies (requests)

Prompt you for your node REST host, TLS cert path, and admin macaroon path

Update escrow.py with correct paths

.\setup.ps1