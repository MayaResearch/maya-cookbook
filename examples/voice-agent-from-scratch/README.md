# Build a voice agent from scratch

[Cookbook home](../../README.md) · [Choose another guide](../README.md) · [All docs](../../docs/README.md)

> **What you will build:** Learn a one-turn voice pipeline. Needs Maya, Soniox and OpenRouter keys.

[Requirements](#1-check-requirements) → [Configure](#2-configure) → [Run](#3-run) → [Check the result](#4-check-the-result) → [Stop](#5-stop)

## 1. Check requirements

Python 3.12+, uv, microphone/headphones or a synthetic WAV. Maya, Soniox and OpenRouter keys. Linux microphone playback may also need PortAudio from your OS package manager.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## 2. Configure

Use the local ignored `.env` or process environment as listed in `.env.example`. Microphone audio goes to Soniox, the transcript to OpenRouter, and the reply text to Maya. These are three providers with separate billing and terms. Use synthetic inputs for automated testing.

## 3. Run

From `examples/voice-agent-from-scratch/` in the complete cookbook checkout:

```sh
uv sync --locked
uv run --locked agent.py --seconds 6 --output reply.wav
# Or test the provider chain using an existing synthetic mono 16-bit WAV:
uv run --locked agent.py --input ../../artifacts/synthetic-input.wav --output file-reply.wav --no-play
```

## 4. Check the result

The complete loop is in `agent.py`, deliberately without a framework:

| Step | Responsible code |
| --- | --- |
| Microphone or WAV | `main()` records only after Enter, or `read_input()` validates the selected file. |
| Speech to text | `transcribe()` sends bounded PCM to Soniox and waits for final tokens and `finished`. |
| Language-model reply | `reply()` calls the exact OpenRouter model with a 1024-token ceiling and refuses truncated/non-final replies. |
| Text to speech | `run()` reuses `quickstarts/python/tts.py`, including status and audio-format checks. |
| Speaker / WAV | `main()` saves the selected output and optionally plays it locally. |
| Stop | Ctrl+C stops local playback. This HTTP teaching path is not instant streaming cancellation; see the streaming example for that protocol. |

Press Enter when prompted, speak for six seconds, then hear the reply. The output shows recognized text and the answer, and writes `reply.wav`. The file-input alternative requires you to create/select a synthetic WAV first; the tutorial never silently records a microphone.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## 5. Stop

Ctrl+C stops recording/playback and the operation. The app handles one turn and exits, keeping only the explicitly requested local output file. A cancelled threaded HTTP request may finish until its bounded network timeout; never describe this as instant server-side barge-in.

## Limits and help

For a known single-language call add `--language hi`, `--language te` or `--language en`. This applies a strict Soniox hint and the same Maya language. In testing, unconstrained STT confused some short greetings across Indic scripts; do not silently count a wrong-script transcript as correct. Leave the option unset only when automatic/mixed-language handling is intended and evaluate the transcript. Larger reasoning models may need their own reviewed token budget; this example fails rather than speaking a cut-off answer.

This is an intentionally half-duplex teaching loop, not a low-latency full-duplex agent. Recording finishes before STT/LLM/TTS run. No conversation memory, tools, automatic VAD, interruption detector or silent provider fallback. For conversational production behavior use the framework examples.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and examples/voice-agent-from-scratch/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
