$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$specPath = Join-Path $repoRoot "dev_server_launcher.spec"
$warnPath = Join-Path $repoRoot "build\dev_server_launcher\warn-dev_server_launcher.txt"
$exePath = Join-Path $repoRoot "dist\dev_server_launcher.exe"
$launcherReq = Join-Path $repoRoot "requirements_launcher.txt"

function Test-Python313 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonExe
    )
    try {
        & $PythonExe -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 13) else 1)"
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Resolve-Python313 {
    if ($env:DEV_LAUNCHER_PYTHON -and (Test-Python313 -PythonExe $env:DEV_LAUNCHER_PYTHON)) {
        return $env:DEV_LAUNCHER_PYTHON
    }

    try {
        $pyList = & py -0p 2>$null
        if ($LASTEXITCODE -eq 0 -and $pyList) {
            foreach ($line in $pyList) {
                if ($line -match "3\.13" -and $line -match "([A-Za-z]:\\.*python(?:3\.13)?\.exe)") {
                    $candidate = $Matches[1]
                    if (Test-Python313 -PythonExe $candidate) {
                        return $candidate
                    }
                }
            }
        }
    } catch {}

    $common = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.13.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    foreach ($candidate in $common) {
        if (Test-Python313 -PythonExe $candidate) {
            return $candidate
        }
    }

    throw "Python 3.13 executable not found or not runnable. Set DEV_LAUNCHER_PYTHON to a valid python.exe."
}

function Invoke-Py {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonExe,
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    & $PythonExe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "$PythonExe failed with exit code $LASTEXITCODE. Args: $($Args -join ' ')"
    }
}

function Release-LauncherExeLock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ExePath
    )

    $name = [System.IO.Path]::GetFileNameWithoutExtension($ExePath)
    Get-Process -Name $name -ErrorAction SilentlyContinue | ForEach-Object {
        try { Stop-Process -Id $_.Id -Force -ErrorAction Stop } catch {}
    }

    if (-not (Test-Path $ExePath)) {
        return
    }

    for ($i = 0; $i -lt 5; $i++) {
        try {
            Remove-Item -Path $ExePath -Force -ErrorAction Stop
            return
        } catch {
            Start-Sleep -Milliseconds 400
        }
    }

    if (Test-Path $ExePath) {
        throw "Unable to release executable lock: $ExePath"
    }
}

$python313 = Resolve-Python313

Write-Host "[1/6] Validate Python 3.13 runtime..."
Invoke-Py -PythonExe $python313 -Args @("-c", "import sys; print(sys.version)")

Write-Host "[2/6] Validate tkinter runtime..."
Invoke-Py -PythonExe $python313 -Args @("-c", "import tkinter as tk; root=tk.Tk(); root.destroy(); print('tkinter-ok')")

Write-Host "[3/6] Ensure build dependencies..."
Invoke-Py -PythonExe $python313 -Args @("-m", "pip", "install", "-q", "pyinstaller")
if (Test-Path $launcherReq) {
    Invoke-Py -PythonExe $python313 -Args @("-m", "pip", "install", "-q", "-r", $launcherReq)
}

Write-Host "[4/6] Build launcher exe..."
Release-LauncherExeLock -ExePath $exePath
Invoke-Py -PythonExe $python313 -Args @("-m", "PyInstaller", "--clean", "--noconfirm", $specPath)

Write-Host "[5/6] Validate build warnings..."
if (-not (Test-Path $warnPath)) {
    throw "Build warning file not found: $warnPath"
}
$warnText = Get-Content -Path $warnPath -Raw
if ($warnText -match "tkinter installation is broken") {
    throw "Build failed quality gate: tkinter is broken in PyInstaller warnings."
}
if ($warnText -match "missing module named tkinter") {
    throw "Build failed quality gate: tkinter missing in PyInstaller warnings."
}

Write-Host "[6/6] Smoke test executable..."
if (-not (Test-Path $exePath)) {
    throw "Build output not found: $exePath"
}
$proc = Start-Process -FilePath $exePath -PassThru
Start-Sleep -Seconds 4
if ($proc.HasExited) {
    throw "Smoke test failed: launcher exited early with code $($proc.ExitCode)."
}
Stop-Process -Id $proc.Id -Force

Write-Host ""
Write-Host "Launcher build succeeded."
Write-Host "EXE: $exePath"
Write-Host "WARN: $warnPath"
