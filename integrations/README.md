# Choose your voice-agent integration

[Cookbook home](../README.md) · [All docs](../docs/README.md)

Choose one framework. You do not need both.

### [Maya + LiveKit · open setup →](livekit/README.md)

### [Maya + Pipecat · open setup →](pipecat/README.md)

Both links go straight to the complete setup instructions. Read on only if you want to compare requirements.

## LiveKit · terminal first

**[Open the LiveKit guide →](livekit/README.md)**

- **You get:** a local microphone conversation in your terminal.
- **You need:** Python, uv, Git, headphones, and Maya/Soniox/OpenRouter keys.
- **Cloud account:** not needed for local console mode; needed configuration is different for rooms.
- **Before relying on it:** this cookbook pins Maya plugin `a2333554` with LiveKit 1.8.0. It does not automatically install newer changes from [PR #7175](https://github.com/livekit/agents/pull/7175).

## Pipecat · browser first

**[Open the Pipecat guide →](pipecat/README.md)**

- **You get:** a local browser voice agent using WebRTC.
- **You need:** Python, uv, Git, headphones, microphone permission, and Maya/Soniox/OpenRouter keys.
- **Cloud account:** local WebRTC needs neither Daily nor LiveKit.
- **Before relying on it:** the pinned Maya community package accepts 19 Calyx voices, fewer than the direct API. Follow the guide's voice limits.

## Only need speech, not a full agent?

**[Start with a simple TTS call →](../quickstarts/README.md)**

It needs only a Maya key. Both framework folders also include a `verify_tts.py` smoke test; see the [test instructions](../docs/validation.md#reproduce-bounded-live-speech-checks).

## Before your first call

Speech and agent calls are billable. Microphone audio goes to Soniox, transcripts to OpenRouter, and reply text to Maya. Read [validation](../docs/validation.md) and keep the demo local.

**Coding agent:** read [root AGENTS.md](../AGENTS.md), then the chosen folder's README and AGENTS.md. Do not install the other framework or change pins to get around errors.
