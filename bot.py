import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.openrouter.llm import OpenRouterLLMService
from pipecat.services.soniox.stt import SonioxSTTService
from pipecat.transports.base_transport import BaseTransport, TransportParams

from pipecat_maya import MayaTTSService

load_dotenv(override=True)

SYSTEM_PROMPT = (
    "You are a helpful voice agent. You are a general-purpose agent: you answer "
    "anything you are asked and you do what the user tells you to do. "
    "Never mention the company, organization, or model behind you, and never "
    "name any company or model such as Gemma, Google, OpenAI or Anthropic. "
    "If asked who or what you are, say only that you are a voice agent, a "
    "helpful assistant. Keep replies short and conversational. "
    "Reply in the same language the user speaks, written only in that language's "
    "own script. Never romanize or transliterate, and never repeat the same "
    "thing twice in different forms. Do not add translations, pronunciations, "
    "or parentheses explaining what you just said. Say it once. "
    "Your output is spoken aloud, so use plain text only: no markdown, no emoji, "
    "no bullet points, and no special characters."
)

transport_params = {
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        vad_analyzer=SileroVADAnalyzer(),
    ),
}


async def run_bot(transport: BaseTransport):
    stt = SonioxSTTService(
        api_key=os.environ["SONIOX_API_KEY"],
        # Soniox detects its own endpoints and proposes turn start/stop. Without
        # this it only finalizes when VAD reports speech ended, and if VAD never
        # fires the transcript stays interim forever and the LLM never runs.
        vad_force_turn_endpoint=False,
    )

    llm = OpenRouterLLMService(
        api_key=os.environ["OPENROUTER_API_KEY"],
        settings=OpenRouterLLMService.Settings(
            model="google/gemma-3-27b-it",
            extra={"extra_body": {"reasoning": {"enabled": False}}},
        ),
    )

    tts = MayaTTSService(
        api_key=os.environ["MAYA_API_KEY"],
        settings=MayaTTSService.Settings(model="Maya Calyx", voice="Tarini"),
    )

    context = LLMContext([{"role": "system", "content": SYSTEM_PROMPT}])
    aggregators = LLMContextAggregatorPair(context)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            aggregators.user(),
            llm,
            tts,
            transport.output(),
            aggregators.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(enable_metrics=True, enable_usage_metrics=True),
        idle_timeout_secs=120,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        context.add_message({"role": "user", "content": "Say hello and introduce yourself briefly."})
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    await PipelineRunner().run(task)


async def bot(runner_args: RunnerArguments):
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
