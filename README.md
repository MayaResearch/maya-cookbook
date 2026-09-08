# Maya Research Cookbook

Build speech and voice agents with **Maya Calyx**. This cookbook offers 24 selected Calyx speakers and 11 documented languages, including Indian English. Every starter example selects `Maya Calyx` and `Aarav` explicitly. Start with one example, not a large framework installation.

**Public beta.** See [validation status](docs/validation.md) before relying on a path. A passing unit test is not proof that a microphone call, every voice, or every accent has been checked.

## Start here

| I want to… | Start with | Accounts needed |
| --- | --- | --- |
| Turn text into a playable WAV | [Python](quickstarts/python/README.md), [TypeScript](quickstarts/typescript/README.md), or [curl](quickstarts/curl/README.md) | Maya |
| Add Maya to LiveKit | [LiveKit voice agent](integrations/livekit/README.md) | Maya, Soniox, OpenRouter; LiveKit only for rooms |
| Add Maya to Pipecat | [Pipecat voice agent](integrations/pipecat/README.md) | Maya, Soniox, OpenRouter |

Then explore [streaming and cancellation](examples/streaming-tts/README.md) or [build a voice agent from scratch](examples/voice-agent-from-scratch/README.md).

## Your first speech file

Get a Maya API key through [Maya Research](https://www.mayaresearch.ai/) or email [charan@mayaresearch.ai](mailto:charan@mayaresearch.ai). Keep it in your shell environment or secret manager as `MAYA_API_KEY`. Never put it in a browser, source code, issue, screenshot or agent conversation.

From the repository root, with Python 3.12 or newer:

```sh
python3 quickstarts/python/tts.py --text 'नमस्ते! आपका ऑर्डर कल पहुँच जाएगा।' --language hi --output hello.wav
```

Open `hello.wav` in your audio player. The script checks the response, reads its real sample rate, adds the WAV header and refuses to overwrite an existing recording. It needs no Python packages. This first example saves a complete file; it does not promise low-latency playback. For progressive audio delivery use the streaming example.

## Bring your coding agent

Copy this prompt along with the repository link:

> Read AGENTS.md. Help me choose and run the smallest example for my task. Read that example's README and AGENTS.md. Install its pinned dependencies, identify missing credential names without asking me to paste secrets into chat, run the keyless tests, and report exactly what works. Ask before billable API calls. Preserve my files. Do not publish, deploy or rent compute.

Every runnable folder has a more specific prompt. [llms.txt](llms.txt) is the compact index for agents; [AGENTS.md](AGENTS.md) describes safe execution.

## Find the details

- [API contract](docs/api-reference/README.md), [HTTP](docs/api-reference/http.md), [WebSocket v2](docs/api-reference/websocket.md), [voices and languages](docs/api-reference/catalog.json).
- [The 24 selected Calyx speakers and sample coverage](docs/speakers.md).
- [Troubleshooting](docs/troubleshooting.md): noisy audio, empty files, slow replies, missing endings and failed calls.
- [Production checklist](docs/production-checklist.md): credentials, costs, interruptions, monitoring and deployment boundaries.
- [Testing and current evidence](docs/validation.md), [maintenance](docs/maintenance.md), [source versions](docs/sources.json).

Maya provides text-to-speech, not the entire conversational stack. The complete agents use Soniox for speech recognition and OpenRouter for the LLM. Those services have separate accounts, billing, terms and language coverage. No hidden fallback swaps your selected provider or voice.

## Compatibility and support

These examples use [Maya's public API reference](https://www.mayaresearch.ai/llm.txt), checked on 8 September 2026. Dependencies and Git integrations are pinned in per-example lockfiles. Installing one example does not install all of them.

The [Pipecat package](https://github.com/MayaResearch/pipecat-maya) is Maya-maintained. The [LiveKit plugin PR](https://github.com/livekit/agents/pull/6899) is not yet merged upstream. Integration-specific limitations are listed before each run command.

Report reproducible API problems to the public support contacts in the API reference. Include versions and request/session identifiers, not keys or customer recordings. See [contributing](CONTRIBUTING.md), [security](SECURITY.md) and the [code license](LICENSE). Example code does not grant model-weight, voice or customer-data rights.
