from pathlib import Path
from importlib.metadata import distributions
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs, copy_metadata

root = Path(SPECPATH).parent
datas = collect_data_files('conversation_copilot', includes=['assets/**', 'demo/*.txt'],
    excludes=['**/*.sqlite*', '**/*.db', '**/.env*'])
binaries, hiddenimports = [], []
for package in ('mediapipe', 'fastembed', 'faster_whisper', 'ctranslate2', 'winrt'):
    data, binary, hidden = collect_all(package)
    datas += data
    binaries += binary
    hiddenimports += hidden
for package in ('nvidia.cublas', 'nvidia.cuda_nvrtc', 'nvidia.cudnn'):
    binaries += collect_dynamic_libs(package)
datas += copy_metadata('fastembed')
for distribution in distributions():
    for file in distribution.files or ():
        if any(part.lower().startswith(('license', 'copying', 'notice')) for part in file.parts):
            path = distribution.locate_file(file)
            if path.is_file():
                datas.append((str(path), str(Path('third-party-licenses') / distribution.metadata['Name'] / file.parent)))

a = Analysis([str(root / 'packaging' / 'launcher.py')], pathex=[str(root)],
    binaries=binaries, datas=datas, hiddenimports=hiddenimports,
    excludes=['torch', 'tensorflow', 'jax', 'pytest', 'IPython'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='ConversationCopilot',
    debug=False, strip=False, upx=False, console=False,
    icon=str(root / 'conversation_copilot' / 'assets' / 'conversation-copilot-icon.png'))
