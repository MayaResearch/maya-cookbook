# LiveKit voice agent with Maya

[Cookbook home](../../README.md) · [Choose another guide](../README.md) · [All docs](../../docs/README.md)

> **What you will build:** Run a local terminal voice agent. Needs Maya, Soniox and OpenRouter keys.

[Requirements](#1-check-requirements) → [Configure](#2-configure) → [Run](#3-run) → [Check the result](#4-check-the-result) → [Stop](#5-stop)

## 1. Check requirements

Python 3.12–3.14, uv, Git, microphone/headphones. Keys for Maya, Soniox and OpenRouter. Local `console` needs no LiveKit Cloud account.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## 2. Configure

Populate this folder's ignored `.env` from the blank `.env.example` or use a secret manager. Existing process environment wins. The STT model is Soniox `stt-rt-v5`; the LLM defaults explicitly to `openai/gpt-4o-mini` through OpenRouter and can be selected with `OPENROUTER_MODEL`. A Maya key alone is not the full agent stack.

For a known Hindi call set `MAYA_LANGUAGE=hi`; for Telugu use `te`, and English `en`. The example sends the same strict language hint to Soniox to reduce wrong-script transcriptions. Leave it blank for mixed-language calls; strict hints are not appropriate for unrestricted language switching.

## 3. Run

From `integrations/livekit/` in the complete cookbook checkout:

```sh
uv sync --locked --no-sources
uv run --locked --no-sources -m livekit.agents download-files
uv run --locked --no-sources agent.py console
```

## 4. Check the result

A local microphone conversation: speak, wait for one short reply and interrupt it. Check that playback stops and the next turn does not contain old audio. `download-files` retrieves the VAD asset; it is a setup network download, not a speech API request.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## 5. Stop

Ctrl+C stops the worker and local microphone session. Console mode does not deploy or provision anything. For rooms only, set `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` and run `uv run --locked --no-sources agent.py dev`; review costs and transport setup first.

## Limits and help

Maya-maintained plugin at public commit `a2333554`, submitted as the independent [LiveKit PR 7175](https://github.com/livekit/agents/pull/7175), not an upstream release. Its `maya-research-tts` branch starts from upstream main and does not depend on another pending contribution. Released LiveKit is pinned to 1.8.0. `--no-sources` is important: the Maya fork's uv workspace redirects dependencies to its development workspace packages. The direct Git dependency still installs with this option. The plugin supports Maya Research voice models; this cookbook release currently tests Calyx with Aarav. Human microphone/browser quality checks are separate from imports and provider tests; changing settings is not evidence of support in every path.

For custom TTS usage, create one `stream()` per LiveKit segment, push incremental text, then call `end_input()`. Do not push new text after `flush()`. The plugin shares one Maya context across that segment's sentences and sends one final closer.

On a Maya TTS instance, `update_options(language=None)` restores automatic/mixed-language handling for the next turn without interrupting an active turn. Omitting the argument leaves the current setting unchanged. This only updates TTS, not Soniox's separate language hints.

Custom Maya URLs must use HTTPS/WSS; plaintext HTTP/WS is rejected before any request. The plugin tolerates a pause awaiting more LLM input after audio has arrived, then re-arms the response timeout on new text or the final closer. There is no per-sentence completion acknowledgement in v2, so applications must also bound the LLM/overall turn and always end or cancel abandoned input. This is not a guarantee that every word was spoken.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and integrations/livekit/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
