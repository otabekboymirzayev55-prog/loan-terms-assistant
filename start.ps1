$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (!(Test-Path -LiteralPath $python)) { throw 'Create .venv and install requirements.txt first.' }
if (Get-NetTCPConnection -LocalPort 7860 -State Listen -ErrorAction SilentlyContinue) { Write-Output 'Loan Assistant is already listening: http://127.0.0.1:7860/'; exit 0 }
$logs = Join-Path $PSScriptRoot '.run'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
Start-Process -FilePath $python -ArgumentList 'app.py' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'app.log') -RedirectStandardError (Join-Path $logs 'app-error.log') | Out-Null
Write-Output 'Starting Loan Assistant: http://127.0.0.1:7860/ (logs: .run)'
