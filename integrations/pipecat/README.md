# Pipecat voice agent with Maya

## Before you start

Python 3.12+, uv, Git, a browser with microphone permission and headphones. Keys for Maya, Soniox and OpenRouter. Local WebRTC needs no Daily or LiveKit account.

Read [current validation](../../docs/validation.md) and the [API reference](../../docs/api-reference/README.md). Use synthetic text first. Running speech/agent commands makes billable provider calls.

## Configure

Use this folder's ignored `.env` or your process environment. See blank `.env.example`. Process values win. STT is Soniox `stt-rt-v5`; LLM is explicitly selected with `OPENROUTER_MODEL` through OpenRouter; Maya model/voice/language are configured independently.

For known-language calls set `MAYA_LANGUAGE=hi`, `te` or `en`. Soniox receives the same strict language hint. Leave it blank for mixed-language calls.

The example waits one second after VAD reports a pause, and requires a transcript before replying. This deliberately tolerates brief pauses between sentences, at the cost of more response delay. Longer pauses can still become separate turns. Tune and test this policy with your callers; it is not a universal end-of-turn detector. It uses Pipecat's [speech-timeout strategy](https://docs.pipecat.ai/api-reference/server/utilities/turn-management/user-turn-strategies), not the implicit Smart Turn model.

## Run

From `integrations/pipecat/` in the complete cookbook checkout:

```sh
uv sync --locked
uv run --locked bot.py --host 127.0.0.1 --port 7860 --transport webrtc
```

## Expected result and verification

Open http://127.0.0.1:7860 in your chosen browser, connect, and say one short sentence. You should hear a Maya reply. Interrupt and start another turn, then disconnect. The packaged Pipecat development UI is an external pinned dependency.

Run the repository keyless suite from the root as described in [AGENTS.md](../../AGENTS.md). An install or an HTTP 200 alone is not a passed audio check. Verify the saved file, the audible final word and any interruption behavior independently.

## Stop and clean up

Disconnect in the browser, then Ctrl+C the server. It binds only to loopback in the documented command and has a five-minute per-bot ceiling. Do not expose the development runner publicly or leave billable sessions running.

## Limits and troubleshooting

Pin: Pipecat 1.8.1 plus Maya community package commit `2c3b569`. The package accepts 19 Calyx voices, not the 31 in current HTTP docs. Inspect exported `pipecat_maya.MODELS`; newer names such as Diya fail locally. Do not bypass validation or silently substitute voices. There is no claim that Pipecat upstream maintains this package.

See [troubleshooting](../../docs/troubleshooting.md) and [production requirements](../../docs/production-checklist.md). Tested version/date and any unverified steps are in the validation report; don't infer a universal quality or latency guarantee.

## Ask your coding agent

> Read the root AGENTS.md and integrations/pipecat/AGENTS.md. Run this example using this README's pinned setup. Report missing credential names without printing secrets. Run the relevant keyless checks first. Ask before billable calls or using my microphone. Preserve existing files and the selected providers/model/voice. Verify the documented output and report passed, failed and unverified checks separately. Do not publish, deploy or provision resources.
