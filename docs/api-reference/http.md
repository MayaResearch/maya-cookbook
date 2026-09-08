# HTTP: text to audio

Source: [Maya contract](https://www.mayaresearch.ai/llm.txt), checked 2026-09-08. Runnable code: [Python](../../quickstarts/python/tts.py), [TypeScript](../../quickstarts/typescript/tts.ts), [curl](../../quickstarts/curl/tts.sh). Agent instructions: [root](../../AGENTS.md).

`POST https://tts.mayaresearch.ai/v1/tts`

Send `Authorization: Bearer <key>`, `Content-Type: application/json`, and a nonempty `User-Agent`. Use a server-side environment variable, never a URL query or browser bundle.

| Field | Meaning |
| --- | --- |
| `text` | Required nonempty plain text. No SSML, HTML or Markdown interpretation. |
| `model` | Always send `Maya Calyx` explicitly. This is the cookbook choice, not a claim about the server's default. |
| `voice` | Exact Calyx speaker name. The examples explicitly send `Aarav` unless you select another documented speaker. |
| `language` | Optional documented code. Omit for mixed-language text. `en` means Indian English, not `en-US` or `en-GB`. |
| `speed` | Not supported by Calyx. Omit it; the Python payload helper rejects it. |
| `sample_rate` | 8000, 16000 or 24000. |
| `encoding` | `pcm_s16le` or `mulaw`. |

The beginner recipes intentionally expose default PCM rather than every telephony control. Do not add unknown fields, seed, pitch or region selectors. An accepted/ignored field is not a working feature.

## Decode what arrived

Check HTTP status first. On a non-200, do not produce an audio file. Then check `Content-Type`:

- `audio/L16; rate=24000; channels=1`: Maya's raw signed 16-bit **little-endian**, mono PCM. Parse the rate rather than assuming your request was honored.
- `audio/basic; rate=8000`: G.711 mu-law, **not PCM**. These beginner WAV recipes reject it. Decode or pass to a compatible carrier using a telephony-specific implementation.

The body is not a WAV. Preserve byte order across network chunks. Chunk boundaries can split a two-byte PCM sample; carry that byte into the next chunk and reject a dangling byte at completion. Add a WAV header only when saving. PCM duration is `bytes / (sample_rate * 2)` for mono 16-bit PCM. An empty or malformed 200 is a failure.

The Python/TypeScript quickstarts buffer one bounded clip to save a complete WAV. They are not real-time playback clients. The [streaming recipe](../../examples/streaming-tts/README.md) yields packets as they arrive.

## Failures, timing and limits

400/401 are not fixed by retrying unchanged. 429/5xx and connection failures may be transient, but never blindly replay a request after audio has already been delivered. These short recipes use no automatic retry. A production implementation needs bounded backoff and `Retry-After` handling before playback begins.

Read `x-request-id` for support. Do not log Authorization or raw request dumps. Keep payloads and generated audio private unless deliberately using synthetic public samples.

The examples cap input at 5000 characters and buffered audio at 120 seconds. These are tutorial safety guards, **not provider limits**. Do not cite source latency measurements as a customer SLA. First HTTP read, first PCM packet, and first sound at the listener are different timings.
