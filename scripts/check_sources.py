"""Read-only current-source drift checks. No provider key or paid API call."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads((ROOT / "docs/sources.json").read_text())


def get(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "maya-cookbook-source-check/0.1",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"HTTP {response.status}")
        return response.read(3 * 1024 * 1024)


def main():
    failed = False
    try:
        digest = hashlib.sha256(get(SOURCES["maya_docs"]["url"])).hexdigest()
        ok = digest == SOURCES["maya_docs"]["sha256"]
        print(f"Maya contract: {'unchanged' if ok else 'CHANGED, REVIEW REQUIRED'}")
        failed |= not ok
    except Exception:
        print("Maya contract: UNVERIFIED, source request failed")
        failed = True
    for integration in SOURCES["integrations"]:
        try:
            url = f"https://api.github.com/repos/{integration['repo']}/commits/{integration['ref']}"
            current = json.loads(get(url))["sha"]
            ok = current == integration["sha"]
            print(f"{integration['repo']}: {'unchanged' if ok else 'NEW COMMIT, REVIEW REQUIRED'}")
            failed |= not ok
        except Exception:
            print(f"{integration['repo']}: UNVERIFIED, source request failed")
            failed = True
    for url in SOURCES["references"]:
        try:
            get(url)
            print(f"Reachable: {url}")
        except Exception:
            print(f"UNVERIFIED reference: {url}")
            failed = True
    return failed


if __name__ == "__main__":
    sys.exit(main())
