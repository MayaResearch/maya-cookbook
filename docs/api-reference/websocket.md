# WebSocket v2: one conversation, many turns

Source: [Maya contract](https://www.mayaresearch.ai/llm.txt). Code: [stream.py](../../examples/streaming-tts/stream.py). Checks: [streaming tests](../../tests/test_streaming.py). Read [AGENTS.md](../../AGENTS.md) before modifying it.

Connect server-side to `wss://tts.mayaresearch.ai/v1/tts/stream` with the bearer key in upgrade headers. Never expose the key through browser JavaScript or a query string.

```text
Connect -> start(v2=true) -> metadata -> text(context_id) -> audio* -> end
                                               |
                          stop local playback + cancel -> cancelled
```

| Send | Fields / action |
| --- | --- |
| `start` | First message, `v2:true`, exact `model` and `voice`, optional `language`. Wait for valid `metadata` before text. |
| `text` | Fresh single-use `context_id`, nonempty text, `continue:true` while more text is coming. Final segment uses `continue:false`. |
| turn closer | For an already open turn only: `text` frame with same ID and `continue:false`; text may be empty or absent. |
| `cancel` | Name the active context. Discard queued playback immediately. Do not wait to mute. |
| `ping` | Optional application keepalive; server returns `pong`. |

| Receive | Meaning |
| --- | --- |
| `metadata` | Successful v2 readiness, actual `sample_rate`, `channels`, `encoding` and `session_id`. |
| `audio` | Base64 raw PCM with `context_id`. Decode strictly and preserve sequence and partial sample bytes. |
| `end` | Normal completion of one context. Flush its valid audio tail. |
| `cancelled` | Interrupted completion; do not wait for an additional `end`. |
| `error` | Fail the affected turn; `context_id` is not guaranteed. Startup errors do not establish readiness. |
| `pong` | Not audio or completion. |

Each turn gets one terminal event, end **or** cancelled. Ignore late audio and terminators belonging to retired contexts. An unknown/already-finished cancel may get **no acknowledgement**. Use timeouts and make local cancellation independent of that acknowledgement.

Model/voice/language are connection settings. The cookbook explicitly selects `Maya Calyx` and defaults to `Aarav`. Open a new socket when changing speaker or language. Calyx does not accept `speed`; the client omits it from both startup and every text frame. It requests the default PCM format and validates the server's readiness metadata.

Feed text segments as the LLM produces usable text, sharing one context ID. Do not open a new synthesis context for each audio packet. A complete known paragraph belongs in one request; provider audio packetization is a separate concern.

On disconnect, fail the current turn. Reconnect with bounded backoff for a **new** turn; do not replay speech that may have been heard. This small client surfaces the error and closes rather than implementing a general reconnect manager.

Streaming bytes successfully is not proof that a browser jitter buffer, speaker, telephone or framework played them without gaps. Verify the last receiver as well. The teaching client's `first_audio_ms` measures receipt of first usable PCM after submission, excluding connection setup; it is not microphone-to-speaker latency.
