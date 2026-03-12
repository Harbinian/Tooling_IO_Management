$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $repoRoot "frontend"
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"
$backendStdout = Join-Path $repoRoot ".backend.stdout.log"
$backendStderr = Join-Path $repoRoot ".backend.stderr.log"
$frontendStdout = Join-Path $frontendDir ".devserver.5173.stdout.log"
$frontendStderr = Join-Path $frontendDir ".devserver.5173.stderr.log"

function Stop-PortListeners {
    param(
        [int[]]$Ports
    )

    foreach ($port in $Ports) {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if (-not $connections) {
            continue
        }

        $owningPids = @($connections | Select-Object -ExpandProperty OwningProcess -Unique)
        foreach ($owningPid in $owningPids) {
            Write-Host "Stopping process on port $port (PID $owningPid)..."
            taskkill /PID $owningPid /T /F | Out-Null
        }
    }
}

function Remove-LogFile {
    param(
        [string]$Path
    )

    if (Test-Path $Path) {
        Remove-Item $Path -Force -ErrorAction SilentlyContinue
    }
}

if (-not (Test-Path $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

if (Test-Path $venvPython) {
    $pythonCmd = $venvPython
} else {
    $pythonCmd = "python"
}

Stop-PortListeners -Ports @(5000, 5173)

Remove-LogFile -Path $backendStdout
Remove-LogFile -Path $backendStderr
Remove-LogFile -Path $frontendStdout
Remove-LogFile -Path $frontendStderr

Write-Host "Starting backend on http://127.0.0.1:5000 ..."
$backendProc = Start-Process -FilePath $pythonCmd `
    -ArgumentList "web_server.py" `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $backendStdout `
    -RedirectStandardError $backendStderr `
    -PassThru

Start-Sleep -Seconds 4

$backendListening = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if (-not $backendListening) {
    throw "Backend failed to bind to port 5000. Check $backendStderr"
}

Write-Host "Starting frontend on http://localhost:5173 ..."
$frontendProc = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort" `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput $frontendStdout `
    -RedirectStandardError $frontendStderr `
    -PassThru

Start-Sleep -Seconds 5

$frontendListening = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if (-not $frontendListening) {
    throw "Frontend failed to bind to port 5173. Check $frontendStderr"
}

Write-Host ""
Write-Host "Backend running:  http://127.0.0.1:5000  (PID $($backendProc.Id))"
Write-Host "Frontend running: http://localhost:5173   (PID $($frontendProc.Id))"
Write-Host "Backend logs:     $backendStdout"
Write-Host "Frontend logs:    $frontendStdout"
