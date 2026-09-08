# Coding-agent instructions: Streaming: receive audio, cancel, reuse the connection

Read [root AGENTS.md](../../AGENTS.md) first. The [README](README.md) is the single source for exact install, configure, run, verification and stop commands. Execute from this folder; retain the full checkout for shared references/helpers.

- Outcome: The first command writes `streaming.wav`. The cancellation command reports cancellation and does **not** write a completed WAV. `MayaSocket.speak()` yields PCM progressively; its caller supplies a playback sink. Tests demonstrate repeated turns and cancellation without acknowledgement.
- Configuration: Set `MAYA_API_KEY` in the process environment, plus optional `MAYA_VOICE` and `MAYA_LANGUAGE`. The model is `Maya Calyx`, with `Aarav` as the starter voice. If set, `MAYA_MODEL` must also be `Maya Calyx`. The socket reads real readiness metadata. An explicit language must match the text. The client omits unsupported speed and uses default PCM.
- Boundaries: The CLI saves audio rather than playing it in real time. No automatic reconnect/replay. One active turn per connection in this teaching client; unique IDs and filtered late frames protect later turns. First PCM receipt excludes connection setup and is not speaker latency.
- Cleanup: Ctrl+C closes the socket. If adding playback, mute and empty its queue before `await client.interrupt()`. Close the async context manager when the session ends.

Read [validation](../../docs/validation.md) before promising this is verified. Use keyless tests from the repository root first; request names/locations of missing credentials, never their values in chat. No automatic paid calls, microphone activation, provider substitution, package-cache edits, publication or deployment. Preserve existing outputs. Record versions, commands, failures and unverified device/listening steps.
