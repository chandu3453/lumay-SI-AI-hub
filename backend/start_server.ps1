$env:OPENBLAS_NUM_THREADS="1"
$venv = Join-Path $PSScriptRoot ".venv"
& "$venv\Scripts\python.exe" -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8001, log_level='info')"
