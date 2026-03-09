# UniGuru deterministic production-style startup
Write-Host "--- UniGuru Live Reasoning Service ---" -ForegroundColor Green

if (-not $env:UNIGURU_HOST) { $env:UNIGURU_HOST = "0.0.0.0" }
if (-not $env:UNIGURU_PORT) { $env:UNIGURU_PORT = "8000" }
if (-not $env:UNIGURU_WORKERS) { $env:UNIGURU_WORKERS = "2" }
if (-not $env:PYTHONPATH) { $env:PYTHONPATH = "c:\Users\Yass0\OneDrive\Desktop\TASK14" }

python -m uvicorn uniguru.service.api:app --host $env:UNIGURU_HOST --port $env:UNIGURU_PORT --workers $env:UNIGURU_WORKERS
