# Basic generated call fixture

These are project-owned synthetic test assets. They contain fictional people,
locally generated voices, project-authored dialogue, and no call recording or
private contact content.

| File | Source | SHA-256 |
|---|---|---|
| `basic-video-chat.mp4` | Fictional portrait sheets generated with OpenAI's built-in image generator; deterministic local video-call composition and mouth-state animation; Windows `System.Speech` dialogue; encoded with FFmpeg 8.0 | `082a066268dd033b5fb3ec1b6c50cf7fe165be41f894da3dd653076e2f6eb6d9` |
| `basic-video-chat-user.wav` | Project-authored Alex lines generated locally with `Microsoft David Desktop`, mono 16 kHz PCM16; silence during Maya turns | `422f0446c66b012eada3d84119c98d52986ce2395630a9d3e9f66b1ab8138a0a` |
| `basic-video-chat-contact.wav` | Project-authored Maya lines generated locally with `Microsoft Zira Desktop`, varied rate/energy by authored pose, mono 16 kHz PCM16; silence during Alex turns | `e6e7e0410bbe3e5dbb2933c3e75da5581db893d331e901f07d667e9937b6a096` |
| `heygen-video-chat.mp4` | HeyGen Video Agent rendering of the project-authored Maya/Alex test scenario; 1280x720 H.264 with AAC audio | `c8c9308f836dc854c5b9ae29df9b31f53b1eefcc9154adcc98f30ae642b948d6` |

The user approved this as a **basic** test fixture on 2026-08-25. Validation
detected the selected remote face and produced landmarks/blendshapes for all six
authored poses. Speaker stems had zero crossover. The accepted English model
produced 1.01% mean word error and 10.53% maximum per-line word error.

This fixture supports repeatable F02-F05 integration checks. It does not replace
the controlled F04 scenario comparison, a real WhatsApp call, or subjective user
acceptance. Pose labels are generation metadata, not true-emotion labels.

The user approved the HeyGen render as an additional realistic integration
fixture on 2026-08-25. It provides neural lip sync, naturalistic motion, and
cleaner speech, but the free-tier render has visible watermarks and supports
only Maya as the animated narrator; Alex remains a static self-view. It tests
realistic compression, face tracking, expression variation, and semantic audio
coverage. It does not replace the basic fixture's exact turns, separate speaker
stems, or indirect `the event` memory-retrieval case.
