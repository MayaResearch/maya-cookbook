# Maya Research Cookbook

Build with Maya Research voice models. **Pick one task below. You do not need to install the whole cookbook.**

> **Public beta:** examples use a tested, pinned setup. Read [what is tested](docs/validation.md) before production use. Keep API keys on your server, never in browser code or agent prompts.

## 1 · Generate your first audio

Turn one sentence into a playable WAV file. **Needs: a Maya API key.**

**[Start with Python →](quickstarts/python/README.md)** · [TypeScript / Node](quickstarts/typescript/README.md) · [curl](quickstarts/curl/README.md)

New to Maya? Choose Python. It needs no extra Python packages.

---

## 2 · Receive streaming audio

Learn how to receive audio chunks, cancel a turn and reuse a connection. **Needs: a Maya API key.**

**[Open the streaming example →](examples/streaming-tts/README.md)**

The example CLI saves a WAV. Your application supplies the real-time playback.

---

## 3 · Add Maya to a voice agent

Already using a framework? Choose your guide.

| Your framework | Start here | What you run |
| --- | --- | --- |
| LiveKit | **[LiveKit guide →](integrations/livekit/README.md)** | A local terminal voice agent |
| Pipecat | **[Pipecat guide →](integrations/pipecat/README.md)** | A local browser voice agent |

These complete examples need **Maya + Soniox + OpenRouter** keys. Maya speaks, Soniox transcribes, and the LLM answers. The local modes do not need a LiveKit Cloud or Daily account. Each provider has separate billing.

[Compare the integrations and their limits →](integrations/README.md)

---

## 4 · Understand the pipeline

Want to see how speech recognition, an LLM and Maya fit together without a voice-agent framework?

**[Build a voice agent from scratch →](examples/voice-agent-from-scratch/README.md)**

This is a one-turn teaching example: record, transcribe, generate an answer, then speak. It is not a full-duplex production agent.

---

## 5 · Find a voice or API detail

| I need… | Open |
| --- | --- |
| Voices, languages and sample coverage | [Speaker guide](docs/speakers.md) |
| A request body or response format | [HTTP API](docs/api-reference/http.md) |
| Streaming messages and lifecycle | [WebSocket API](docs/api-reference/websocket.md) |
| Help with an error or audio problem | [Troubleshooting](docs/troubleshooting.md) |
| Testing and production requirements | [Validation](docs/validation.md) · [Production checklist](docs/production-checklist.md) |

[Browse all documentation →](docs/README.md)

## Get started in three steps

1. **Get a key** through [Maya Research](https://www.mayaresearch.ai/) or [email support](mailto:charan@mayaresearch.ai).
2. **Download the cookbook** into a new directory:

   ```sh
   git clone https://github.com/MayaResearch/maya-cookbook.git
   cd maya-cookbook
   ```

3. **Open one guide above.** It tells you what to install, where to configure keys, what to run and how to stop.

Speech requests are billable. Use synthetic text first. Do not share keys or customer recordings in issues.

## Using a coding agent?

Give your agent the repository link and this prompt:

> Read AGENTS.md. Help me choose the smallest example for my task. Read that example's README and AGENTS.md, follow its pinned setup, and run its keyless checks first. Ask before paid calls or microphone use. Report missing credential names, never values. Preserve my files and report passed, failed and unverified checks separately. Do not publish or deploy.

[Agent instructions](AGENTS.md) · [Compact agent index](llms.txt)

## Model and integration versions

The cookbook's dated catalog uses **Maya Calyx**, **24 selected voices** and **11 languages**, including Indian English. Starter examples select **Aarav** explicitly. See [the catalog](docs/api-reference/catalog.json) for the snapshot, not a promise about every future model.

Framework integrations have separate compatibility limits. The cookbook pins tested commits; a newer PR is not automatically included. Check the [integration guide](integrations/README.md) and [validation record](docs/validation.md).

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Maintenance](docs/maintenance.md) · [License](LICENSE)
