# Coding-agent instructions: curl: a safe first speech request

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: A playable `hindi.wav`. The shell checks HTTP status before conversion; the Python helper checks Content-Type, sample rate, nonempty/aligned PCM and preserves existing files.
- Configuration: Set `MAYA_API_KEY` in your environment. Edit `request.json` for text/model/voice/language. Validation reuses the Python recipe in this checkout. Do not add keys to JSON. Curl receives Authorization via stdin, not its command-line arguments.
- Boundaries: Default PCM only. Do not invoke under a tracing shell or log the environment. It intentionally does not follow redirects or retry. The small Python helper is needed: curl alone cannot safely create a WAV from arbitrary response metadata.
- Cleanup: The script removes only its own temporary body/header files and exits. Ctrl+C triggers cleanup. Use a new output name for another run.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
