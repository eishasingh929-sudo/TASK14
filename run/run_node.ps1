$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

if (-not $env:PORT) { $env:PORT = "3000" }
if (-not $env:NODE_BACKEND_PORT) { $env:NODE_BACKEND_PORT = $env:PORT }
if (-not $env:ASK_URL) { $env:ASK_URL = "http://localhost:8000/ask" }
if (-not $env:UNIGURU_ASK_URL) { $env:UNIGURU_ASK_URL = $env:ASK_URL }

Set-Location "$RootDir\node-backend"
npm.cmd start
