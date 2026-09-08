"""One HTTP request to a verified WAV. Standard library only, no automatic retries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from email.message import Message
from pathlib import Path

ENDPOINT = "https://tts.mayaresearch.ai/v1/tts"
CATALOG = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)
MAX_BYTES = 24_000 * 2 * 120  # Tutorial guard, NOT a provider limit.


def payload(text, model="Maya Calyx", voice="Aarav", language=None, speed=None):
    if not isinstance(text, str) or not text.strip() or len(text) > 5000:
        raise ValueError("Use 1-5000 characters of plain text for this example")
    if model not in CATALOG["models"] or voice not in CATALOG["models"][model]:
        raise ValueError("Choose an exact model/voice pair from docs/api-reference/catalog.json")
    if language is not None and language not in CATALOG["languages"]:
        raise ValueError("Unsupported language. Use en for Indian English; omit for mixed text")
    body = {"text": text, "model": model, "voice": voice}
    if language is not None:
        body["language"] = language
    if speed is not None:
        raise ValueError("Maya Calyx does not accept speed; omit this field")
    return body


def pcm_rate(content_type: str) -> int:
    """Maya documents little-endian PCM despite the audio/L16 media-type label."""
    msg = Message()
    msg["content-type"] = content_type
    if msg.get_content_type().lower() != "audio/l16":
        raise ValueError("Expected Maya PCM audio/L16, not JSON, WAV or mu-law")
    try:
        rate = int(msg.get_param("rate", "0"))
        channels = int(msg.get_param("channels", "1"))
    except (ValueError, TypeError):
        raise ValueError("Invalid audio format metadata") from None
    if rate not in (8000, 16000, 24000) or channels != 1:
        raise ValueError("Expected documented mono PCM sample rate")
    return rate


def save_wav(path: Path, pcm: bytes, rate: int) -> None:
    if not pcm or len(pcm) % 2:
        raise ValueError("Empty or truncated 16-bit audio; no WAV written")
    if rate not in (8000, 16000, 24000):
        raise ValueError("Unsupported sample rate")
    # Exclusive creation preserves the user's existing recordings.
    with path.open("xb") as target:
        with wave.open(target, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(rate)
            wav.writeframes(pcm)


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Refusing redirect with a bearer credential")


def synthesize(body: dict, api_key: str, *, opener=None, timeout=60):
    if not api_key.strip() or "\r" in api_key or "\n" in api_key:
        raise ValueError("Set a nonempty MAYA_API_KEY in the process environment")
    opener = opener or urllib.request.build_opener(NoRedirects())
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, ensure_ascii=False).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "maya-cookbook/0.1",
        },
    )
    started = time.monotonic()
    try:
        with opener.open(req, timeout=timeout) as res:
            if res.status != 200:
                raise ValueError(f"Maya HTTP {res.status}; response is not audio")
            rate = pcm_rate(res.headers.get("Content-Type", ""))
            pcm = bytearray()
            first = None
            while True:
                if time.monotonic() - started > timeout:
                    raise TimeoutError("Audio transfer exceeded the example deadline")
                chunk = res.read(4096)
                if not chunk:
                    break
                first = first or time.monotonic()
                pcm.extend(chunk)
                if len(pcm) > MAX_BYTES:
                    raise ValueError("Audio exceeds this example's 120-second byte budget")
            if not pcm or len(pcm) % 2:
                raise ValueError("Empty or truncated 16-bit audio")
            return (
                bytes(pcm),
                rate,
                {
                    "pcm_bytes": len(pcm),
                    "sample_rate": rate,
                    "duration_seconds": len(pcm) / (rate * 2),
                    "first_read_ms": round((first - started) * 1000, 2),
                    "request_id": res.headers.get("x-request-id"),
                },
            )
    except urllib.error.HTTPError as exc:
        # Do not print provider body, request headers or credentials.
        raise RuntimeError(f"Maya HTTP {exc.code}. See docs/troubleshooting.md") from None
    except urllib.error.URLError:
        raise RuntimeError("Maya network request failed; no automatic replay") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="नमस्ते! आपका ऑर्डर कल पहुँच जाएगा।")
    parser.add_argument(
        "--model", choices=["Maya Calyx"], default=os.getenv("MAYA_MODEL", "Maya Calyx")
    )
    parser.add_argument("--voice", default=os.getenv("MAYA_VOICE", "Aarav"))
    parser.add_argument("--language", default=os.getenv("MAYA_LANGUAGE") or None)
    parser.add_argument("--output", type=Path, default=Path("output.wav"))
    parser.add_argument("--check", action="store_true", help="Validate config, no network")
    args = parser.parse_args()
    try:
        body = payload(args.text, args.model, args.voice, args.language)
        if args.check:
            print("Configuration valid. No API call made.")
            return
        if args.output.exists():
            raise ValueError("Output already exists; choose a new --output path")
        pcm, rate, report = synthesize(body, os.environ.get("MAYA_API_KEY", ""))
        save_wav(args.output, pcm, rate)
        print(json.dumps({"output": str(args.output), **report}, ensure_ascii=False))
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
