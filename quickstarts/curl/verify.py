"""Validate curl input/output using the same checked Python HTTP recipe."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from tts import payload, pcm_rate, save_wav  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--request", type=Path)
parser.add_argument("--headers", type=Path)
parser.add_argument("--pcm", type=Path)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
try:
    if args.request:
        body = json.loads(args.request.read_text())
        payload(**body)
    else:
        lines = args.headers.read_text().splitlines()
        types = [
            line.split(":", 1)[1].strip()
            for line in lines
            if line.lower().startswith("content-type:")
        ]
        if not types:
            raise ValueError("Missing audio Content-Type")
        rate = pcm_rate(types[-1])
        data = args.pcm.read_bytes()
        if len(data) > 24_000 * 2 * 120:
            raise ValueError("Example audio budget exceeded")
        save_wav(args.output, data, rate)
        print(f"Saved {args.output}: {len(data)} PCM bytes, {rate} Hz")
except (ValueError, TypeError, OSError) as exc:
    print(f"Invalid request or audio: {exc}", file=sys.stderr)
    sys.exit(1)
