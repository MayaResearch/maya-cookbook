# Coding-agent instructions: TypeScript: server-side text to speech

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: A playable `english.wav`. The output reports sample rate and PCM byte count. Test files exercise status failures, redirects, timeouts, format validation and exact WAV bytes.
- Configuration: Set `MAYA_API_KEY` in the process environment. Optional `MAYA_MODEL`, `MAYA_VOICE` and `MAYA_LANGUAGE`. `.env.example` is a template, not automatically loaded. No key belongs in `VITE_*`, `NEXT_PUBLIC_*` or browser JavaScript.
- Boundaries: The quickstart buffers a complete bounded clip, not real-time playback. No automatic retry or fallback. The catalog comes from the shared dated JSON, not a second handwritten voice list.
- Cleanup: The process exits after one request. Ctrl+C stops it. Existing output files are never overwritten.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
