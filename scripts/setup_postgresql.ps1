# Setup PostgreSQL and create database for transfer-assistant
# Run as Administrator

param(
    [string]$DBName = "transfer_assistant_db",
    [string]$DBUser = "transfer_user",
    [string]$PostgressUser = "postgres",
    [string]$DBHost = "localhost",
    [int]$Port = 5432
)

# Set full path to psql
$psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

Write-Host "=== Transfer Assistant PostgreSQL Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify PostgreSQL is installed
Write-Host "[Step 1] Checking PostgreSQL installation..." -ForegroundColor Yellow
if (Test-Path $psqlPath) {
    Write-Host "[OK] Found psql at $psqlPath"
} else {
    Write-Host "[FAIL] psql not found at $psqlPath" -ForegroundColor Red
    exit 1
}

# Step 2: Verify service is running
Write-Host ""
Write-Host "[Step 2] Checking PostgreSQL service..." -ForegroundColor Yellow
$service = Get-Service postgresql-x64-17 -ErrorAction SilentlyContinue
if ($service -and $service.Status -eq "Running") {
    Write-Host "[OK] Service is running"
} elseif ($service) {
    Write-Host "[WARN] Service found but stopped. Starting..."
    Start-Service postgresql-x64-17
    Start-Sleep -Seconds 2
    Write-Host "[OK] Service started"
} else {
    Write-Host "[WARN] Service 'postgresql-x64-17' not found. Continuing..." -ForegroundColor Yellow
}

# Step 3: Test superuser connection
Write-Host ""
Write-Host "[Step 3] Testing superuser connection..." -ForegroundColor Yellow
& $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -c "SELECT 1;" *>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Connected as $PostgressUser"
} else {
    Write-Host "[FAIL] Cannot connect as $PostgressUser. Ensure password is set." -ForegroundColor Red
    Write-Host "  Run: & '$psqlPath' -U $PostgressUser -h $DBHost -p $Port -d postgres"
    exit 1
}

# Step 4: Create database if it doesn't exist
Write-Host ""
Write-Host "[Step 4] Creating database $DBName..." -ForegroundColor Yellow
& $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname = '$DBName';" *>&1 | Out-Null
$dbOutput = & $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname = '$DBName';" 2>&1
if ($dbOutput -match "1") {
    Write-Host "[OK] Database already exists"
} else {
    & $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -c "CREATE DATABASE $DBName;" *>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database created"
    } else {
        Write-Host "[FAIL] Could not create database" -ForegroundColor Red
        exit 1
    }
}

# Step 5: Create user role if it doesn't exist
Write-Host ""
Write-Host "[Step 5] Creating user role $DBUser..." -ForegroundColor Yellow
$userOutput = & $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -t -c "SELECT 1 FROM pg_user WHERE usename = '$DBUser';" 2>&1
if ($userOutput -match "1") {
    Write-Host "[OK] User already exists"
} else {
    $password = Read-Host "Enter password for $DBUser" -AsSecureString
    $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($password))
    $escapedPassword = $plainPassword -replace "'", "''"
    
    & $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -c "CREATE ROLE $DBUser WITH LOGIN PASSWORD '$escapedPassword' CREATEDB;" *>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] User created with password"
    } else {
        Write-Host "[FAIL] Could not create user" -ForegroundColor Red
        exit 1
    }
}

# Step 6: Grant privileges
Write-Host ""
Write-Host "[Step 6] Granting privileges..." -ForegroundColor Yellow
$grantSQL = @"
GRANT CONNECT ON DATABASE $DBName TO $DBUser;
GRANT CREATE ON DATABASE $DBName TO $DBUser;
ALTER DATABASE $DBName OWNER TO $DBUser;
"@
& $psqlPath -U $PostgressUser -h $DBHost -p $Port -d postgres -c $grantSQL *>&1 | Out-Null
Write-Host "[OK] Privileges granted"

# Step 7: Test user connection
Write-Host ""
Write-Host "[Step 7] Testing user connection..." -ForegroundColor Yellow
Write-Host "Enter the password you just set for $DBUser when prompted"
& $psqlPath -U $DBUser -h $DBHost -p $Port -d $DBName -c "SELECT 1;" *>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] User connection successful"
} else {
    Write-Host "[WARN] Could not verify user connection. Manual test: & '$psqlPath' -U $DBUser -h $DBHost -p $Port -d $DBName" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Connection details:"
Write-Host "  Host: $DBHost"
Write-Host "  Port: $Port"
Write-Host "  Database: $DBName"
Write-Host "  User: $DBUser"
Write-Host ""
Write-Host "Add to .env file:"
Write-Host "  DATABASE_URL=postgresql://$($DBUser):YOUR_PASSWORD@$($DBHost):$($Port)/$($DBName)"
Write-Host ""

