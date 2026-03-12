$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $repoRoot "frontend"

function Stop-PortListeners {
    param(
        [int[]]$Ports
    )

    foreach ($port in $Ports) {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if (-not $connections) {
            Write-Host "Port $port is already free."
            continue
        }

        $owningPids = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
        foreach ($owningPid in $owningPids) {
            Write-Host "Stopping process on port $port (PID $owningPid)..."
            taskkill /PID $owningPid /T /F | Out-Null
        }
    }
}

Stop-PortListeners -Ports @(5000, 5173)

Write-Host ""
Write-Host "Backend port 5000 stopped."
Write-Host "Frontend port 5173 stopped."
