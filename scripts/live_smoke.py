"""Opt-in bounded synthetic Maya test. Exactly 8 synthesis turns, no STT/LLM/GPU."""

import argparse
import asyncio
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


async def main(args):
    if not args.allow_paid:
        raise ValueError("Explicit --allow-paid is required. This makes 8 billable synthesis turns")
    key = os.getenv("MAYA_API_KEY", "")
    if not key.strip():
        raise ValueError("Set MAYA_API_KEY in the process environment")
    args.output.mkdir(parents=True, exist_ok=False)
    http = load("smoke_http", "quickstarts/python/tts.py")
    stream = load("smoke_stream", "examples/streaming-tts/stream.py")
    prompts = {
        "hi": "नमस्ते! आपका ऑर्डर कल पहुँच जाएगा। धन्यवाद।",
        "te": "నమస్కారం! మీ ఆర్డర్ రేపు వస్తుంది. ధన్యవాదాలు.",
        "en": "Hello! Your order will arrive tomorrow. Thank you.",
    }
    results = []
    try:
        for language, text in prompts.items():
            pcm, rate, info = await asyncio.to_thread(
                http.synthesize, http.payload(text, language=language), key
            )
            http.save_wav(args.output / f"http-{language}.wav", pcm, rate)
            results.append({"test": f"http-{language}", "passed": any(pcm), **info})
        async with stream.MayaSocket(key) as client:
            for language, text in prompts.items():
                pcm = b"".join([chunk async for chunk in client.speak([text])])
                http.save_wav(args.output / f"ws-{language}.wav", pcm, client.rate)
                results.append(
                    {
                        "test": f"ws-{language}",
                        "passed": any(pcm),
                        "first_pcm_ms": client.first_audio_ms,
                        "chunks": client.chunks,
                    }
                )
            async for _ in client.speak([prompts["en"] * 4]):
                await client.interrupt()
            results.append({"test": "cancel-without-waiting-for-ack", "passed": client.cancelled})
            pcm = b"".join([chunk async for chunk in client.speak([prompts["hi"]])])
            http.save_wav(args.output / "after-cancel.wav", pcm, client.rate)
            results.append({"test": "new-turn-after-cancel", "passed": any(pcm)})
    except Exception as exc:
        results.append({"test": "suite", "passed": False, "error_class": type(exc).__name__})
    report = {
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "perceptual_quality": "Not scored; requires human listening",
        "device_playback": "Not tested by this script",
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2))
    if len(results) != 8 or not all(result["passed"] for result in results):
        raise RuntimeError("Live checks failed; inspect the sanitized report")
    print(f"8/8 live checks passed. Audio and report: {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/live-smoke")
    try:
        asyncio.run(main(parser.parse_args()))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")
