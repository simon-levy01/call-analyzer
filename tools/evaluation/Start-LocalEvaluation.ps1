# Run from the project root. This starts a separate local-only test server.
param([switch]$Cpu)
$ErrorActionPreference = 'Stop'
$taskOllama = Join-Path $env:LOCALAPPDATA 'Programs/Ollama/ollama.exe'
if (-not (Test-Path -LiteralPath $taskOllama)) { throw 'Ollama is not installed at its standard user path.' }
$taskOutput = Join-Path (Get-Location) $(if ($Cpu) {'build/local-model-cpu-server'} else {'build/local-model-server'})
New-Item -ItemType Directory -Force -Path $taskOutput | Out-Null
$env:OLLAMA_NO_CLOUD = '1'
$env:OLLAMA_HOST = if ($Cpu) {'127.0.0.1:11435'} else {'127.0.0.1:11436'}
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
# The tested Windows installation needed an explicit backend DLL for GPU discovery.
$taskCuda = Join-Path (Split-Path $taskOllama) 'lib/ollama/cuda_v12'
if ($Cpu) {
    $env:CUDA_VISIBLE_DEVICES = '-1'
    $env:OLLAMA_VULKAN = '0'
} elseif (Test-Path -LiteralPath (Join-Path $taskCuda 'ggml-cuda.dll')) {
    $env:PATH = "$taskCuda;$env:PATH"
    $env:GGML_BACKEND_PATH = Join-Path $taskCuda 'ggml-cuda.dll'
}
Start-Process -FilePath $taskOllama -ArgumentList 'serve' -WindowStyle Hidden -PassThru -RedirectStandardOutput "$taskOutput/stdout.log" -RedirectStandardError "$taskOutput/stderr.log"
