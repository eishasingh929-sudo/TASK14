$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

if (-not $env:PYTHONPATH) {
  $env:PYTHONPATH = "$RootDir\backend"
} else {
  $env:PYTHONPATH = "$RootDir\backend;$env:PYTHONPATH"
}
if (-not $env:UNIGURU_HOST) { $env:UNIGURU_HOST = "0.0.0.0" }
if (-not $env:UNIGURU_PORT) { $env:UNIGURU_PORT = "8000" }
if (-not $env:AUTH_ENABLED) { $env:AUTH_ENABLED = "false" }
if (-not $env:UNIGURU_API_AUTH_REQUIRED) { $env:UNIGURU_API_AUTH_REQUIRED = "false" }
if (-not $env:UNIGURU_LLM_URL) { $env:UNIGURU_LLM_URL = "http://localhost:11434/api/generate" }
if (-not $env:UNIGURU_LLM_MODEL) { $env:UNIGURU_LLM_MODEL = "gpt-oss:120b-cloud" }
if (-not $env:UNIGURU_LLM_TIMEOUT_SECONDS) { $env:UNIGURU_LLM_TIMEOUT_SECONDS = "12" }

python "$RootDir\backend\main.py"
