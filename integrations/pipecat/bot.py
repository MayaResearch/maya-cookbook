"""Maya through Pipecat's local WebRTC runner. No cloud transport account needed."""

import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker, ProcessorUnusablePolicy
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import SmallWebRTCRunnerArguments
from pipecat.services.openrouter.llm import OpenRouterLLMService
from pipecat.services.soniox.stt import SonioxSTTService
from pipecat.transcriptions.language import Language
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.turns.user_stop import SpeechTimeoutUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies
from pipecat.workers.runner import WorkerRunner
from pipecat_maya import MayaTTSService

load_dotenv(override=False)
CALYX_VOICES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)["models"]["Maya Calyx"]


def required(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Set {name} in the environment or ignored .env")
    return value


def services():
    model = os.getenv("MAYA_MODEL", "Maya Calyx")
    if model != "Maya Calyx":
        raise ValueError("This cookbook supports Maya Calyx only")
    voice = os.getenv("MAYA_VOICE", "Aarav")
    if voice not in CALYX_VOICES:
        raise ValueError("Choose a selected Calyx speaker from the cookbook catalog")
    language = os.getenv("MAYA_LANGUAGE") or None
    return (
        SonioxSTTService(
            api_key=required("SONIOX_API_KEY"),
            settings=SonioxSTTService.Settings(
                model="stt-rt-v5",
                language_hints=[Language(language)] if language else None,
                language_hints_strict=bool(language),
            ),
        ),
        OpenRouterLLMService(
            api_key=required("OPENROUTER_API_KEY"),
            settings=OpenRouterLLMService.Settings(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                max_tokens=1024,
                system_instruction=(
                    "You are a helpful Maya Research voice assistant. "
                    "Reply in the user's language in one or two short sentences. "
                    "Plain text only, no markdown or SSML. No tools are available."
                ),
            ),
        ),
        MayaTTSService(
            api_key=required("MAYA_API_KEY"),
            sample_rate=24000,
            settings=MayaTTSService.Settings(
                model=model,
                voice=voice,
                language=os.getenv("MAYA_LANGUAGE") or None,
                speed=None,
            ),
        ),
    )


async def bot(runner_args: SmallWebRTCRunnerArguments):
    transport = SmallWebRTCTransport(
        webrtc_connection=runner_args.webrtc_connection,
        params=TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
        ),
    )
    stt, llm, tts = services()
    user, assistant = LLMContextAggregatorPair(
        LLMContext(),
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
            # Explicit pause policy, no implicit turn-model download or CPU inference.
            # Final STT text is still required before a response is requested.
            user_turn_strategies=UserTurnStrategies(
                stop=[SpeechTimeoutUserTurnStopStrategy(user_speech_timeout=1.0)]
            ),
        ),
    )
    worker = PipelineWorker(
        Pipeline([transport.input(), stt, user, llm, tts, transport.output(), assistant]),
        params=PipelineParams(
            audio_in_sample_rate=16000,
            audio_out_sample_rate=24000,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        processor_unusable_policy=ProcessorUnusablePolicy.END,
        idle_timeout_secs=60,
    )

    @transport.event_handler("on_client_disconnected")
    async def on_disconnected(transport, client):
        await worker.cancel()

    runner = WorkerRunner(handle_sigint=False)
    await runner.add_workers(worker)
    try:
        # Five-minute tutorial ceiling, not a production session-limit policy.
        await asyncio.wait_for(runner.run(), timeout=300)
    finally:
        await worker.cancel()


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
