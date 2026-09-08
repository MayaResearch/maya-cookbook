import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


http_recipe = load("http_recipe", "quickstarts/python/tts.py")
stream_recipe = load("stream_recipe", "examples/streaming-tts/stream.py")
scratch_recipe = load("scratch_recipe", "examples/voice-agent-from-scratch/agent.py")
