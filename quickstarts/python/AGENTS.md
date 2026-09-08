# Coding-agent instructions: Python: one sentence to a WAV

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: A nonempty `hindi.wav`. Open it in your audio player. JSON output contains the actual sample rate, duration and request ID. `first_read_ms` includes connection setup and buffering of the first read; it is not end-user TTFA.
- Configuration: The script reads process environment variables, not `.env` automatically. Set `MAYA_API_KEY` through your shell/secret manager. Optional `MAYA_MODEL`, `MAYA_VOICE`, `MAYA_LANGUAGE` are documented in `.env.example`.
- Boundaries: Saves the complete clip before playback. Default mono PCM only, no auto-retry, 5000-character/120-second example guards. No automatic normalization. Test synthetic Hindi, Telugu and Indian English separately.
- Cleanup: Run once and the process exits. Ctrl+C stops it; use a new output filename for each run.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
