"""A teaching voice loop without LiveKit or Pipecat. Deliberately half-duplex."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import wave
from pathlib import Path

import httpx
from dotenv import load_dotenv
from websockets.asyncio.client import connect

# Reuse the cookbook's small HTTP recipe rather than duplicating its contract.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "quickstarts/python"))
from tts import payload, save_wav, synthesize  # noqa: E402

load_dotenv(override=False)


def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Set {name} in your environment or ignored .env")
    return value


def read_input(path):
    with wave.open(str(path), "rb") as wav:
        if (
            wav.getnchannels() != 1
            or wav.getsampwidth() != 2
            or wav.getframerate() not in (16000, 24000)
            or wav.getcomptype() != "NONE"
            or wav.getnframes() > wav.getframerate() * 30
        ):
            raise ValueError("Input must be mono 16-bit PCM WAV at 16/24 kHz, at most 30 seconds")
        pcm, rate = wav.readframes(wav.getnframes()), wav.getframerate()
        if not pcm or len(pcm) != wav.getnframes() * 2:
            raise ValueError("Empty or truncated input WAV")
        return pcm, rate


async def transcribe(pcm, rate, key, *, language=None, connector=connect):
    """Send one bounded utterance, retain FINAL tokens, require finished acknowledgement."""
    if not pcm or len(pcm) % 2 or rate not in (16000, 24000) or len(pcm) > rate * 2 * 30:
        raise ValueError("Invalid or oversized input PCM")
    async with asyncio.timeout(45):
        async with connector(
            "wss://stt-rt.soniox.com/transcribe-websocket",
            open_timeout=15,
            close_timeout=3,
            max_size=1024 * 1024,
        ) as ws:
            await ws.send(
                json.dumps(
                    {
                        "api_key": key,
                        "model": "stt-rt-v5",
                        "audio_format": "pcm_s16le",
                        "sample_rate": rate,
                        "num_channels": 1,
                        **(
                            {"language_hints": [language], "language_hints_strict": True}
                            if language
                            else {}
                        ),
                    }
                )
            )

            async def send_audio():
                for start in range(0, len(pcm), 4096):
                    await ws.send(pcm[start : start + 4096])
                await ws.send("")  # Explicit TEXT end marker; await the finished response.

            async def receive_text():
                final = []
                async for raw in ws:
                    message = json.loads(raw)
                    if message.get("error_code") or message.get("error_type"):
                        code = message.get("error_code")
                        code = code if type(code) is int else "error"
                        kind = message.get("error_type", "unknown")
                        kind = (
                            kind
                            if isinstance(kind, str) and re.fullmatch(r"[a-z_]{1,80}", kind)
                            else "unknown"
                        )
                        raise RuntimeError(f"Soniox {code} ({kind}); check account and input")
                    final.extend(
                        t["text"]
                        for t in message.get("tokens", [])
                        if t.get("is_final") and t.get("text") not in ("<end>", "<fin>")
                    )
                    if message.get("finished"):
                        text = "".join(final).strip()
                        if not text or len(text) > 5000:
                            raise ValueError("No usable final speech transcript")
                        return text
                raise RuntimeError("Soniox closed before finished; no result claimed")

            async with asyncio.TaskGroup() as tasks:
                tasks.create_task(send_audio())
                result = tasks.create_task(receive_text())
            return result.result()


async def reply(text, key, model, *, client=None):
    body = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {
                "role": "system",
                "content": "Reply to the user in the same language, in one short "
                "plain-text sentence suitable for speech. No markdown, SSML or emojis. "
                "Do not claim you performed actions or accessed tools.",
            },
            {"role": "user", "content": text},
        ],
    }
    owned = client is None
    client = client or httpx.AsyncClient(timeout=30, follow_redirects=False)
    try:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json=body,
        )
        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter HTTP {response.status_code}; no provider substitution")
        data = response.json()
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ValueError("LLM response had no choices")
        if choices[0].get("finish_reason") != "stop":
            raise ValueError("LLM did not finish normally; refusing to speak a truncated reply")
        message = choices[0].get("message")
        if not isinstance(message, dict):
            raise ValueError("LLM response had no message")
        answer = message.get("content")
        if not isinstance(answer, str) or not answer.strip() or len(answer) > 5000:
            raise ValueError("LLM did not return a usable text reply")
        return answer.strip()
    finally:
        if owned:
            await client.aclose()


async def run(pcm, rate, language=None):
    text = await transcribe(pcm, rate, required("SONIOX_API_KEY"), language=language)
    answer = await reply(
        text, required("OPENROUTER_API_KEY"), os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    )
    body = payload(
        answer,
        os.getenv("MAYA_MODEL", "Maya Calyx"),
        os.getenv("MAYA_VOICE", "Aarav"),
        language,
    )
    audio, output_rate, _ = await asyncio.to_thread(synthesize, body, required("MAYA_API_KEY"))
    return text, answer, audio, output_rate


async def main(args):
    for name in ("SONIOX_API_KEY", "OPENROUTER_API_KEY", "MAYA_API_KEY"):
        required(name)
    if args.output.exists():
        raise ValueError("Choose a new --output path, existing files are never overwritten")
    if args.input:
        pcm, rate = read_input(args.input)
    else:
        import sounddevice as sd

        if not 1 <= args.seconds <= 15:
            raise ValueError("Record between 1 and 15 seconds")
        input(f"Press Enter to record {args.seconds} seconds. Audio will go to Soniox: ")
        print("Recording now. Use headphones.")
        recording = sd.rec(args.seconds * 16000, samplerate=16000, channels=1, dtype="int16")
        await asyncio.to_thread(sd.wait)
        pcm, rate = recording.astype("<i2").tobytes(), 16000
    async with asyncio.timeout(150):
        text, answer, audio, output_rate = await run(pcm, rate, args.language)
    save_wav(args.output, audio, output_rate)
    print(f"You said: {text}\nAssistant: {answer}\nSaved: {args.output}")
    if not args.no_play:
        import numpy as np
        import sounddevice as sd

        sd.play(np.frombuffer(audio, dtype="<i2"), output_rate)
        await asyncio.to_thread(sd.wait)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Use a synthetic WAV instead of a microphone")
    parser.add_argument("--output", type=Path, default=Path("reply.wav"))
    parser.add_argument("--seconds", type=int, default=6)
    parser.add_argument("--no-play", action="store_true")
    parser.add_argument(
        "--language",
        choices=("hi", "te", "en"),
        default=os.getenv("MAYA_LANGUAGE") or None,
        help="Optional strict STT hint and Maya language",
    )
    try:
        asyncio.run(main(parser.parse_args()))
    except (Exception, KeyboardInterrupt):
        print(
            "Voice turn failed or stopped. Check credentials and troubleshooting. "
            "No fallback used.",
            file=sys.stderr,
        )
        sys.exit(1)
    finally:
        if "sounddevice" in sys.modules:
            sys.modules["sounddevice"].stop()
