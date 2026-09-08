"""Keyless local documentation, release-file and credential-pattern checks."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "artifacts",
    "dist",
}


def files(root=ROOT):
    for directory, folders, names in os.walk(root):
        folders[:] = [name for name in folders if name not in IGNORED]
        for name in names:
            if name.startswith(".env") and name != ".env.example":
                continue  # Deliberately never read a secret file.
            yield Path(directory) / name


def check():
    errors, count = [], 0
    for path in files():
        relative = path.relative_to(ROOT)
        if path.suffix in (".wav", ".pcm", ".mulaw", ".pem", ".key"):
            errors.append(f"Do not release private/generated data: {relative}")
            continue
        try:
            text = path.read_text()
        except UnicodeError:
            errors.append(f"Unexpected binary release file: {relative}")
            continue
        if re.search(r"maya_sk_live_[A-Za-z0-9_-]{20,}", text) or re.search(
            r"(?:sk-or-v1-|ghp_|xoxb-)[A-Za-z0-9_-]{20,}", text
        ):
            errors.append(f"Credential-shaped value in {relative}")
        if re.search(r"/Users/[A-Za-z0-9_.-]+/|/home/[A-Za-z0-9_.-]+/", text):
            errors.append(f"Machine-local absolute path in {relative}")
        if path.name == ".env.example":
            for line in text.splitlines():
                if "=" not in line or line.startswith("#"):
                    continue
                name, value = line.split("=", 1)
                if re.search(r"KEY|SECRET|TOKEN", name) and value.strip(" '\""):
                    errors.append(f"Nonempty credential placeholder in {relative}")
        if path.suffix == ".md" or path.name == "llms.txt":
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                target = target.split(' "')[0].strip("<>")
                parsed = urlparse(target)
                if parsed.scheme or target.startswith("#"):
                    continue
                resolved = (path.parent / unquote(parsed.path)).resolve()
                count += 1
                if not resolved.is_relative_to(ROOT) or not resolved.exists():
                    errors.append(f"Broken local link: {relative} -> {target}")
    examples = [
        "quickstarts/python",
        "quickstarts/typescript",
        "quickstarts/curl",
        "integrations/livekit",
        "integrations/pipecat",
        "examples/streaming-tts",
        "examples/voice-agent-from-scratch",
    ]
    for relative in examples:
        for name in ("README.md", "AGENTS.md", ".env.example"):
            if not (ROOT / relative / name).is_file():
                errors.append(f"Missing {relative}/{name}")
    catalog = json.loads((ROOT / "docs/api-reference/catalog.json").read_text())
    if (
        set(catalog["models"]) != {"Maya Calyx"}
        or len(catalog["languages"]) != 11
        or len(catalog["models"]["Maya Calyx"]) != 24
        or set(catalog["models"]["Maya Calyx"]) & set(catalog["excluded_calyx_voices"])
    ):
        errors.append("Catalog changed; review contract and expectations together")
    return errors, count


if __name__ == "__main__":
    errors, count = check()
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {count} relative links and release-file hygiene; {len(errors)} errors")
    sys.exit(bool(errors))
