# Python: one sentence to a WAV

[Cookbook home](../../README.md) · [Choose another guide](../README.md) · [All docs](../../docs/README.md)

> **What you will build:** Generate one playable WAV. Only a Maya key is needed.

[Requirements](#1-check-requirements) → [Configure](#2-configure) → [Run](#3-run) → [Check the result](#4-check-the-result) → [Stop](#5-stop)

## 1. Check requirements

Python 3.12+; Maya API key. No Python packages.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## 2. Configure

The script reads process environment variables, not `.env` automatically. Set `MAYA_API_KEY` through your shell/secret manager. Optional `MAYA_MODEL`, `MAYA_VOICE`, `MAYA_LANGUAGE` are documented in `.env.example`.

## 3. Run

From `quickstarts/python/` in the complete cookbook checkout:

```sh
python3 tts.py --check
python3 tts.py --text 'नमस्ते! आपका ऑर्डर कल पहुँच जाएगा।' --language hi --output hindi.wav
```

## 4. Check the result

A nonempty `hindi.wav`. Open it in your audio player. JSON output contains the actual sample rate, duration and request ID. `first_read_ms` includes connection setup and buffering of the first read; it is not end-user TTFA.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## 5. Stop

Run once and the process exits. Ctrl+C stops it; use a new output filename for each run.

## Limits and help

Saves the complete clip before playback. Default mono PCM only, no auto-retry, 5000-character/120-second example guards. No automatic normalization. Test synthetic Hindi, Telugu and Indian English separately.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and quickstarts/python/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
