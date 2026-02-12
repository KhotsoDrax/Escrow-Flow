# ---------------------------------------------
# setup_auto.ps1 - Fully Automated Lightning Escrow Setup
# ---------------------------------------------

Write-Host "⚡ Lightning REST Escrow Setup - Fully Automated" -ForegroundColor Cyan

# ----------------------------
# Step 1: Check Python
# ----------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Please install Python 3.11+ and retry." -ForegroundColor Red
    exit
}

# ----------------------------
# Step 2: Create virtual environment
# ----------------------------
if (-Not (Test-Path ".\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# ----------------------------
# Step 3: Install dependencies
# ----------------------------
Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install requests

# ----------------------------
# Step 4: Locate Polar network folders
# ----------------------------
$polarNetworks = Join-Path $env:USERPROFILE ".polar\networks"
$networkFolders = Get-ChildItem $polarNetworks -Directory | Sort-Object Name -Descending

if ($networkFolders.Count -eq 0) {
    Write-Host "No Polar networks found. Please create one first." -ForegroundColor Red
    exit
}

# Pick the most recent network folder
$latestNetwork = $networkFolders[0].FullName
$lnFolders = Get-ChildItem (Join-Path $latestNetwork "volumes\lnd") -Directory

if ($lnFolders.Count -eq 0) {
    Write-Host "No LND nodes found inside Polar network." -ForegroundColor Red
    exit
}

# Pick the first node folder (you can change if needed)
$nodeFolder = $lnFolders[0].FullName
Write-Host "Using node folder:" $nodeFolder -ForegroundColor Green

# ----------------------------
# Step 5: Detect TLS cert and Admin macaroon
# ----------------------------
$tlsCert = Join-Path $nodeFolder "tls.cert"
$adminMacaroon = Join-Path $nodeFolder "data\chain\bitcoin\regtest\admin.macaroon"

if (-not (Test-Path $tlsCert) -or -not (Test-Path $adminMacaroon)) {
    Write-Host "TLS cert or admin macaroon not found." -ForegroundColor Red
    exit
}

Write-Host "TLS cert found:" $tlsCert
Write-Host "Admin macaroon found:" $adminMacaroon

# ----------------------------
# Step 6: Detect REST host from Polar
# Default REST port is usually 8081
# ----------------------------
$nodeRest = "https://127.0.0.1:8081"
Write-Host "Assuming REST host:" $nodeRest

# ----------------------------
# Step 7: Update escrow.py
# ----------------------------
$escrowFile = ".\escrow.py"
if (-not (Test-Path $escrowFile)) {
    Write-Host "escrow.py not found in current folder." -ForegroundColor Red
    exit
}

(Get-Content $escrowFile) -replace 'NODE_REST = ".*"', "NODE_REST = `"$nodeRest`"" |
    Set-Content $escrowFile
(Get-Content $escrowFile) -replace 'TLS_CERT = r".*"', "TLS_CERT = r`"$tlsCert`"" |
    Set-Content $escrowFile
(Get-Content $escrowFile) -replace 'MACAROON = r".*"', "MACAROON = r`"$adminMacaroon`"" |
    Set-Content $escrowFile

Write-Host "`nConfiguration updated in escrow.py successfully!" -ForegroundColor Green

# ----------------------------
# Step 8: Run CLI app
# ----------------------------
Write-Host "`nSetup complete! You can now run your escrow CLI commands:" -ForegroundColor Cyan
Write-Host "  python escrow.py create 5000 'Website Design'"
Write-Host "  python escrow.py list"
Write-Host "  python escrow.py release <r_hash>"
Write-Host "  python escrow.py refund <r_hash>"

# Optional: launch CLI list view
Write-Host "`nListing current escrows..."
python escrow.py list
