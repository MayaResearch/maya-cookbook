"""One billable Maya request through a real Pipecat worker, recorded to WAV."""

import argparse
import asyncio
import json
import os
import wave
from pathlib import Path

from dotenv import load_dotenv
from pipecat.frames.frames import EndFrame, TTSAudioRawFrame, TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.workers.runner import WorkerRunner
from pipecat_maya import MayaTTSService

load_dotenv(override=False)
CALYX_VOICES = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)["models"]["Maya Calyx"]


class AudioSink(FrameProcessor):
    def __init__(self):
        super().__init__()
        self.pcm = bytearray()
        self.count = 0

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)
        if isinstance(frame, TTSAudioRawFrame):
            if (frame.sample_rate, frame.num_channels) != (24000, 1):
                raise ValueError("Unexpected output PCM format")
            self.pcm.extend(frame.audio)
            self.count += 1
            if len(self.pcm) > 24_000 * 2 * 120:
                raise ValueError("Example audio budget exceeded")
        await self.push_frame(frame, direction)


async def main(args):
    if args.model != "Maya Calyx":
        raise ValueError("This cookbook release currently supports Maya Calyx")
    if args.voice not in CALYX_VOICES:
        raise ValueError("Choose a selected Calyx speaker from the cookbook catalog")
    if args.output.exists():
        raise ValueError("Choose another output path")
    key = os.getenv("MAYA_API_KEY", "").strip()
    if not key:
        raise ValueError("Set MAYA_API_KEY")
    tts = MayaTTSService(
        api_key=key,
        sample_rate=24000,
        settings=MayaTTSService.Settings(
            model=args.model, voice=args.voice, language=None, speed=None
        ),
    )
    sink = AudioSink()
    worker = PipelineWorker(
        Pipeline([tts, sink]), params=PipelineParams(audio_out_sample_rate=24000), enable_rtvi=False
    )
    errors = []

    @worker.event_handler("on_pipeline_error")
    async def on_error(worker, frame):
        errors.append(True)  # Do not dump provider exception payloads.

    @worker.event_handler("on_pipeline_started")
    async def on_started(worker, frame):
        await worker.queue_frames([TTSSpeakFrame(args.text), EndFrame()])

    runner = WorkerRunner()
    await runner.add_workers(worker)
    try:
        await asyncio.wait_for(runner.run(), timeout=90)
    finally:
        await worker.cancel()
    if errors or not sink.pcm or len(sink.pcm) % 2:
        raise ValueError("No complete supported PCM audio")
    with args.output.open("xb") as target, wave.open(target, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(sink.pcm)
    print(f"Pipecat worker: {sink.count} frames, {len(sink.pcm)} PCM bytes; {args.output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="నమస్కారం! మీ ఆర్డర్ రేపు వస్తుంది. ధన్యవాదాలు.")
    parser.add_argument("--model", choices=["Maya Calyx"], default="Maya Calyx")
    parser.add_argument("--voice", default="Aarav")
    parser.add_argument("--output", type=Path, default=Path("pipecat.wav"))
    try:
        asyncio.run(main(parser.parse_args()))
    except (Exception, KeyboardInterrupt):
        parser.exit(1, "Pipecat synthesis failed or stopped. No completion claimed.\n")
