"""Windows executable entry point; ordinary app startup stays in __main__."""
import multiprocessing
import sys

if __name__ == '__main__':
    multiprocessing.freeze_support()
    # Windowed executables have no console streams; native libraries may log to them.
    if sys.stdout is None or sys.stderr is None:
        from pathlib import Path
        import os
        log_dir = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local')) / 'ConversationCopilot'
        log_dir.mkdir(parents=True, exist_ok=True)
        stream = (log_dir / 'launcher.log').open('a', encoding='utf-8', buffering=1)
        sys.stdout = sys.stdout or stream
        sys.stderr = sys.stderr or stream
    if '--profile-check' in sys.argv:
        from package_check import profile_check as main
    elif '--package-check' in sys.argv:
        from package_check import main
    else:
        from conversation_copilot.__main__ import main
    try:
        raise SystemExit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        if len(sys.argv) == 1:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,
                'Conversation Copilot could not start. See launcher.log in your '
                'Windows account under AppData\\Local\\ConversationCopilot for details.',
                'Conversation Copilot', 0x10)
        raise SystemExit(1)
