# F03 synthetic audio fixtures

These are generated project test inputs, not call recordings. They contain no contact name, private content, copied third-party recording, or live audio.

| File | Generator and exact source | Generated | SHA-256 |
|---|---|---|---|
| `english.wav` | Windows `System.Speech` voice `Microsoft Zira Desktop`, rate `-1`; exact text is in `manifest.json`; converted with FFmpeg 8.0 to mono 16 kHz PCM16 | 2026-08-19 | `7f7ca0b47207d9ea0cf5f2617d7ffb5e8400100ffe20725ed9bc354be068b509` |
| `long-english.wav` | Windows `System.Speech` voice `Microsoft Zira Desktop`, rate `-1`; exact text is in `manifest.json`; converted with FFmpeg 8.0 to mono 16 kHz PCM16 | 2026-08-19 | `a92e8975fb44fc53be93a5a77197733fd0167cddc97f2ca47ca34a09da662e98` |
| `hebrew.wav` | Installed AI Voice Generator connector, `crisp` voice, context `294666c04bab4c319d10153c1d4d1402`; exact non-private Hebrew text is in `manifest.json`; complete generated preview converted with FFmpeg 8.0 to mono 16 kHz PCM16 | 2026-08-19 | `8ac632e91478cf5b5bd7b64cc37e49d01c8fdd3fbe6c0cc45f57fd42de55f82a` |

The English files were generated locally with Microsoft Windows voices. The Hebrew file was generated on the user's behalf from project-authored text through the installed voice-generation connector; no existing speaker recording or call audio was supplied. These fixtures are retained solely as project-owned evaluation inputs.
