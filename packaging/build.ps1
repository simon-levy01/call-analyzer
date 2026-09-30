$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
Push-Location $projectRoot
try {
    & $python -m PyInstaller --noconfirm --distpath dist --workpath build\pyinstaller packaging\ConversationCopilot.spec
    if ($LASTEXITCODE -ne 0) { throw 'Executable build failed.' }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'README.txt') -Destination 'dist\README.txt'
} finally {
    Pop-Location
}
