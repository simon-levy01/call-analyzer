Conversation Copilot for Windows

Download ConversationCopilot.exe from the GitHub release and double-click it.
No Python installation or terminal commands are needed. Opening it can take a
little time while the libraries unpack into a temporary directory.

Requires 64-bit Windows and a compatible NVIDIA GPU/driver for transcription.
Python is bundled. Contacts and downloaded models remain in
%LOCALAPPDATA%\ConversationCopilot. No contacts or API keys are shipped here.
Enter your OpenAI API key in Settings. Executable settings save it in
%LOCALAPPDATA%\ConversationCopilot\.env.local; OPENAI_API_KEY also works.

On first run, enter your own OpenAI API key and choose Prepare models and save key.
The app downloads and checks the local models. Setup needs internet and several
GB of free space. If a download fails, use Retry setup. Setup is also available
in Settings > Local model setup.
Calls do not download models. Your saved data stays when the exe is replaced.
Each Windows account has separate data. Copying the exe does not copy that data.
Read diagnostics in %LOCALAPPDATA%\ConversationCopilot\launcher.log.
Normal calls and AI features use your API account and incur usage charges.

Fresh-profile verification (uses synthetic data and mocked downloads):
(Start-Process .\ConversationCopilot.exe -ArgumentList '--profile-check' -Wait -PassThru).ExitCode

Offline package verification (requires both models already installed):
(Start-Process .\ConversationCopilot.exe -ArgumentList '--package-check' -Wait -PassThru).ExitCode

Exit code 0 means success. The success result is written to launcher.log above.
An unhandled failure during ordinary app startup shows a Windows error dialog.
Diagnostic checks report failures in the log and return a nonzero exit code.

The check blocks network access, loads the local models, processes fictional
vision fixtures, and opens an offscreen Qt window using a temporary database.
It does not start a call, capture microphone/video, or invoke a paid API.

This build has development-PC verification; testing on a fresh Windows PC and
a full physical call remain separate checks. This is a self-contained executable.
