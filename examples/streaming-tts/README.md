# Streaming: receive audio, cancel, reuse the connection

[Cookbook home](../../README.md) · [Choose another guide](../README.md) · [All docs](../../docs/README.md)

> **What you will build:** Receive audio chunks and learn cancellation. Only a Maya key is needed.

[Requirements](#1-check-requirements) → [Configure](#2-configure) → [Run](#3-run) → [Check the result](#4-check-the-result) → [Stop](#5-stop)

## 1. Check requirements

Python 3.12+, uv, a Maya key; no STT/LLM account.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## 2. Configure

Set `MAYA_API_KEY` in the process environment, plus optional `MAYA_VOICE` and `MAYA_LANGUAGE`. The model is `Maya Calyx`, with `Aarav` as the starter voice. If set, `MAYA_MODEL` must also be `Maya Calyx`. The socket reads real readiness metadata. An explicit language must match the text. The client omits unsupported speed and uses default PCM.

## 3. Run

From `examples/streaming-tts/` in the complete cookbook checkout:

```sh
uv sync --locked
uv run --locked stream.py --text 'नमस्ते।' --text 'आज आपका दिन कैसा है?' --output streaming.wav
uv run --locked stream.py --text 'This is a synthetic cancellation test with several sentences.' --cancel-after-chunks 1 --output cancelled.wav
```

## 4. Check the result

The first command writes `streaming.wav`. The cancellation command reports cancellation and does **not** write a completed WAV. `MayaSocket.speak()` yields PCM progressively; its caller supplies a playback sink. Tests demonstrate repeated turns and cancellation without acknowledgement.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## 5. Stop

Ctrl+C closes the socket. If adding playback, mute and empty its queue before `await client.interrupt()`. Close the async context manager when the session ends.

## Limits and help

The CLI saves audio rather than playing it in real time. No automatic reconnect/replay. One active turn per connection in this teaching client; unique IDs and filtered late frames protect later turns. First PCM receipt excludes connection setup and is not speaker latency.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and examples/streaming-tts/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
