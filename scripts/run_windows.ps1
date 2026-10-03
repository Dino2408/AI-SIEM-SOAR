$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
if (-not (Test-Path .venv\Scripts\python.exe)) { throw "Virtual environment not found. Run .\scripts\setup_windows.ps1 first." }
& .\.venv\Scripts\python.exe -m orchestrator.main @args
