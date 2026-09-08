# Coding-agent instructions: Build a voice agent from scratch

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: Press Enter when prompted, speak for six seconds, then hear the reply. The output shows recognized text and the answer, and writes `reply.wav`. The file-input alternative requires you to create/select a synthetic WAV first; the tutorial never silently records a microphone.
- Configuration: Use the local ignored `.env` or process environment as listed in `.env.example`. Microphone audio goes to Soniox, the transcript to OpenRouter, and the reply text to Maya. These are three providers with separate billing and terms. Use synthetic inputs for automated testing.
- Boundaries: This is an intentionally half-duplex teaching loop, not a low-latency full-duplex agent. Recording finishes before STT/LLM/TTS run. No conversation memory, tools, automatic VAD, interruption detector or silent provider fallback. For conversational production behavior use the framework examples.
- Cleanup: Ctrl+C stops recording/playback and the operation. The app handles one turn and exits, keeping only the explicitly requested local output file. A cancelled threaded HTTP request may finish until its bounded network timeout; never describe this as instant server-side barge-in.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
