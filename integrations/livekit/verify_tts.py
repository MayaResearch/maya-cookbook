"""One billable Maya request through the actual LiveKit plugin, without a microphone."""

import argparse
import asyncio
import json
import os
import wave
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from livekit.plugins import maya

load_dotenv(override=False)
CALYX_VOICES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)["models"]["Maya Calyx"]


async def main(args):
    if args.model != "Maya Calyx":
        raise ValueError("This cookbook release currently supports Maya Calyx")
    if args.voice not in CALYX_VOICES:
        raise ValueError("Choose a selected Calyx speaker from the cookbook catalog")
    if args.output.exists():
        raise ValueError("Choose a new output path")
    key = os.getenv("MAYA_API_KEY", "").strip()
    if not key:
        raise ValueError("Set MAYA_API_KEY")
    pcm, rate, channels, count = bytearray(), None, None, 0
    async with aiohttp.ClientSession() as session:
        engine = maya.TTS(api_key=key, voice=args.voice, model=args.model, http_session=session)
        try:
            async with asyncio.timeout(90):
                async with engine.synthesize(args.text) as stream:
                    async for event in stream:
                        frame = event.frame
                        if rate is not None and (rate, channels) != (
                            frame.sample_rate,
                            frame.num_channels,
                        ):
                            raise ValueError("Format changed mid-response")
                        rate, channels = frame.sample_rate, frame.num_channels
                        pcm.extend(bytes(frame.data))
                        count += 1
                        if len(pcm) > 24_000 * 2 * 120:
                            raise ValueError("Example audio budget exceeded")
        finally:
            await engine.aclose()
    if not pcm or len(pcm) % 2 or channels != 1 or rate not in (8000, 16000, 24000):
        raise ValueError("No complete supported PCM audio")
    with args.output.open("xb") as target, wave.open(target, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm)
    print(f"LiveKit plugin: {count} frames, {len(pcm)} PCM bytes, {rate} Hz; {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="नमस्ते! आपका ऑर्डर कल पहुँच जाएगा।")
    parser.add_argument("--model", choices=["Maya Calyx"], default="Maya Calyx")
    parser.add_argument("--voice", default="Aarav")
    parser.add_argument("--output", type=Path, default=Path("livekit.wav"))
    try:
        asyncio.run(main(parser.parse_args()))
    except (Exception, KeyboardInterrupt):
        parser.exit(1, "LiveKit synthesis failed or stopped. No completion claimed.\n")
