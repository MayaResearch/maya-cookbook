# Pipecat voice bot — Soniox + OpenRouter + Maya

A minimal voice agent: you talk, it talks back.

| Stage | Service | Config |
| ----- | ------- | ------ |
| Speech-to-text | Soniox | `stt-rt-preview`, self-endpointing |
| LLM | OpenRouter | `google/gemma-3-27b-it`, reasoning off |
| Text-to-speech | Maya | `Maya Calyx` / `Tarini` |
| Transport | SmallWebRTC | browser mic, Silero VAD |

## Setup

One time only.

```bash
uv venv --python 3.12
uv pip install -r requirements.txt
```

Then put three keys in `.env` (copy `.env.example`):

```bash
SONIOX_API_KEY=...
OPENROUTER_API_KEY=...
MAYA_API_KEY=...
```

`.env` and `logs/` are gitignored. Keep the keys out of anything you commit.

## Start the server

```bash
.venv/bin/python bot.py
```

It prints `→ Open: http://localhost:7860` once ready — about 10 seconds, most of
it loading the Silero VAD model.

To run it in the background with a timestamped log per session:

```bash
LOG="logs/call-$(date +%Y%m%d-%H%M%S).log"
.venv/bin/python bot.py > "$LOG" 2>&1 &
ln -sf "$(basename $LOG)" logs/latest.log
```

`logs/latest.log` always points at the most recent run.

## Talk to it

1. Open **http://localhost:7860** in Chrome.
2. Click **Connect** and allow microphone access when prompted.
3. The bot greets you first. Start talking — it replies in whatever language you
   speak, in that language's own script.

To end, click **Disconnect**.

> **Reconnecting:** if Connect hangs after a Disconnect, hard-reload the page
> (`Cmd+Shift+R`) instead. The browser sometimes fails to re-acquire a mic that
> was released mid-session, and the handshake then never completes. A reload
> forces a fresh `getUserMedia`. If reload also fails, another app is holding the
> mic — close Zoom, Meet, or any other Chrome tab using it.

## Checking request IDs

Every Maya synthesis is traceable at three levels, all written to the log:

| ID | Scope | Meaning |
| -- | ----- | ------- |
| `session_id` | whole conversation | one Maya WebSocket |
| `context_id` | one turn | one bot response |
| `request_id` | one sentence | one provider synthesis call |

Pull them out of a log:

```bash
grep request_id logs/latest.log
```

You get a line per sentence as it is synthesized, then one summary per turn:

```
Maya request_id=52e6dee9-… , context_id=04e0429a-… , session_id=dc009753-…
Maya request_id=d7939a15-… , context_id=04e0429a-… , session_id=dc009753-…
Maya turn complete context_id=04e0429a-… , session_id=dc009753-… ,
  request_ids=['52e6dee9-…', 'd7939a15-…', 'a804bfe6-…']
```

Several request IDs per turn is normal — Pipecat splits streamed LLM output into
sentences and each sentence is its own synthesis call.

**Always trust the `request_ids` list on the `turn complete` line.** It is what
the server reports, and it can include IDs that never appeared on their own line
above (frames that arrived before the turn opened locally). Use those IDs to
match against gateway-side logs.

Other useful greps:

```bash
grep -E "Generating chat|Generating TTS" logs/latest.log   # conversation flow
grep -iE "error|warning"                logs/latest.log    # problems only
grep "TTFB"                             logs/latest.log    # latency per stage
tail -f logs/latest.log                                    # watch live
```

Request-ID logging needs `pipecat-maya` from `main`; the `v0.1.0` tag predates
it. `requirements.txt` already tracks `main`.
