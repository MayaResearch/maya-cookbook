# curl: a safe first speech request

[Cookbook home](../../README.md) · [Choose another guide](../README.md) · [All docs](../../docs/README.md)

> **What you will build:** Make an HTTP speech request and save a validated WAV. Only a Maya key is needed.

[Requirements](#1-check-requirements) → [Configure](#2-configure) → [Run](#3-run) → [Check the result](#4-check-the-result) → [Stop](#5-stop)

## 1. Check requirements

Bash, curl and Python 3.12+ for validation/WAV wrapping; Maya API key.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## 2. Configure

Set `MAYA_API_KEY` in your environment. Edit `request.json` for text/model/voice/language. Validation reuses the Python recipe in this checkout. Do not add keys to JSON. Curl receives Authorization via stdin, not its command-line arguments.

## 3. Run

From `quickstarts/curl/` in the complete cookbook checkout:

```sh
python3 verify.py --request request.json
bash tts.sh hindi.wav
```

## 4. Check the result

A playable `hindi.wav`. The shell checks HTTP status before conversion; the Python helper checks Content-Type, sample rate, nonempty/aligned PCM and preserves existing files.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## 5. Stop

The script removes only its own temporary body/header files and exits. Ctrl+C triggers cleanup. Use a new output name for another run.

## Limits and help

Default PCM only. Do not invoke under a tracing shell or log the environment. It intentionally does not follow redirects or retry. The small Python helper is needed: curl alone cannot safely create a WAV from arbitrary response metadata.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and quickstarts/curl/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
