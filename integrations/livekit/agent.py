"""Local microphone LiveKit agent. Maya owns this plugin; upstream PR is pending."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, cli
from livekit.plugins import maya, openai, silero, soniox

load_dotenv(override=False)
CALYX_VOICES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)["models"]["Maya Calyx"]


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Set {name} in your environment or this folder's ignored .env")
    return value


def build_session():
    model = os.getenv("MAYA_MODEL", "Maya Calyx")
    if model != "Maya Calyx":
        raise ValueError("This cookbook release currently supports Maya Calyx")
    voice = os.getenv("MAYA_VOICE", "Aarav")
    if voice not in CALYX_VOICES:
        raise ValueError("Choose a selected Calyx speaker from the cookbook catalog")
    language = os.getenv("MAYA_LANGUAGE") or None
    maya_options = {
        "api_key": required("MAYA_API_KEY"),
        "model": model,
        "voice": voice,
    }
    if language:
        maya_options["language"] = language
    return AgentSession(
        vad=silero.VAD.load(),
        stt=soniox.STT(
            api_key=required("SONIOX_API_KEY"),
            params=soniox.STTOptions(
                model="stt-rt-v5",
                language_hints=[language] if language else None,
                language_hints_strict=bool(language),
            ),
        ),
        llm=openai.LLM(
            api_key=required("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            max_completion_tokens=1024,
            store=False,
        ),
        tts=maya.TTS(**maya_options),
        # Explicit VAD mode also works outside LiveKit Cloud.
        turn_handling={"interruption": {"mode": "vad"}},
    )


server = AgentServer(host="127.0.0.1", port=8089)


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    session = build_session()
    await session.start(
        room=ctx.room,
        agent=Agent(
            instructions=(
                "You are a helpful voice assistant demonstrating Maya Research speech. "
                "Reply in the user's language in one or two short plain-text sentences. "
                "Do not use markdown, SSML, emojis or claim access to tools you do not have."
            )
        ),
    )


if __name__ == "__main__":
    cli.run_app(server)
