$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcherExe = Join-Path $repoRoot "dist\dev_server_launcher.exe"
$expectedPorts = @(8150, 8151)

if (-not (Test-Path $launcherExe)) {
    throw "Launcher not found: $launcherExe"
}

Write-Host "Starting launcher: $launcherExe"
$launcherProc = Start-Process -FilePath $launcherExe -WorkingDirectory $repoRoot -PassThru

Start-Sleep -Seconds 6

$missingPorts = @()
foreach ($port in $expectedPorts) {
    $listening = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $listening) {
        $missingPorts += $port
    }
}

if ($missingPorts.Count -gt 0) {
    throw "Launcher started (PID $($launcherProc.Id)) but ports not ready: $($missingPorts -join ', ')."
}

Write-Host ""
Write-Host "Launcher running: PID $($launcherProc.Id)"
Write-Host "Backend: http://localhost:8151"
Write-Host "Frontend: http://localhost:8150"
Write-Host "Logs: $repoRoot\logs\dev_server_launcher\"
