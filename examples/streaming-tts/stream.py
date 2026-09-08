"""Persistent Maya v2 socket: readiness, ordered PCM, cancellation and new turns."""

from __future__ import annotations

import argparse
import asyncio
import base64
import binascii
import json
import os
import sys
import time
import uuid
import wave
from pathlib import Path

from websockets.asyncio.client import connect

URL = "wss://tts.mayaresearch.ai/v1/tts/stream"
CATALOG = json.loads(
    (Path(__file__).resolve().parents[2] / "docs/api-reference/catalog.json").read_text()
)


class MayaSocket:
    """One active turn at a time; never automatically replay interrupted speech."""

    def __init__(
        self,
        key,
        model="Maya Calyx",
        voice="Aarav",
        language=None,
        *,
        connector=connect,
        deadline=60,
    ):
        if not key.strip() or any(c in key for c in "\r\n"):
            raise ValueError("Set MAYA_API_KEY")
        if model not in CATALOG["models"] or voice not in CATALOG["models"][model]:
            raise ValueError("Choose a Maya Calyx voice from docs/api-reference/catalog.json")
        if language is not None and language not in CATALOG["languages"]:
            raise ValueError("Choose a documented language code or omit it for mixed text")
        self.key, self.connector, self.deadline = key, connector, deadline
        self.start = {"type": "start", "v2": True, "model": model, "voice": voice}
        if language:
            self.start["language"] = language
        self.ws = None
        self.active = None
        self.stop = asyncio.Event()
        self.cancelled = False
        self.first_audio_ms = None
        self.chunks = 0

    async def __aenter__(self):
        self.ws = await self.connector(
            URL,
            additional_headers={"Authorization": f"Bearer {self.key}"},
            user_agent_header="maya-cookbook/0.1",
            open_timeout=15,
            close_timeout=3,
            max_size=2 * 1024 * 1024,
            max_queue=16,
        )
        try:
            await self.ws.send(json.dumps(self.start))
            message = self.message(await asyncio.wait_for(self.ws.recv(), 15))
            if message.get("type") != "metadata":
                raise ValueError("Maya did not accept v2 startup; no text was sent")
            rate = message.get("sample_rate")
            if (
                type(rate) is not int
                or rate not in (8000, 16000, 24000)
                or type(message.get("channels")) is not int
                or message.get("channels") != 1
                or message.get("encoding") != "pcm_s16le"
            ):
                raise ValueError("Unsupported readiness audio metadata")
            self.rate, self.session_id = rate, message.get("session_id")
            return self
        except BaseException:
            await self.ws.close()
            raise

    async def __aexit__(self, *_):
        if self.ws:
            await self.ws.close()

    @staticmethod
    def message(raw):
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("Expected a JSON object from Maya")
        return value

    async def interrupt(self):
        # A playback sink must discard its OWN queued audio before calling this.
        if self.active and not self.stop.is_set():
            self.cancelled = True
            self.stop.set()  # Stop delivery now, not after the server acknowledgement.
            await asyncio.wait_for(
                self.ws.send(
                    json.dumps(
                        {
                            "type": "cancel",
                            "context_id": self.active,
                        }
                    )
                ),
                3,
            )

    async def next_message(self):
        receiver = asyncio.create_task(self.ws.recv())
        stopper = asyncio.create_task(self.stop.wait())
        try:
            await asyncio.wait((receiver, stopper), return_when=asyncio.FIRST_COMPLETED)
            if self.stop.is_set():
                return None
            return self.message(receiver.result())
        finally:
            for task in (receiver, stopper):
                if not task.done():
                    task.cancel()
            await asyncio.gather(receiver, stopper, return_exceptions=True)

    async def speak(self, sentences):
        if self.active:
            raise ValueError("This teaching client supports one active turn per connection")
        if (
            not sentences
            or any(not isinstance(s, str) or not s.strip() for s in sentences)
            or sum(map(len, sentences)) > 5000
        ):
            raise ValueError("Use nonempty sentences totaling at most 5000 characters")
        cid = uuid.uuid4().hex
        self.active = cid
        self.stop.clear()
        self.cancelled, self.first_audio_ms, self.chunks = False, None, 0
        self.last_context_id = cid
        started, count, carry, completed = time.monotonic(), 0, b"", False
        try:
            async with asyncio.timeout(self.deadline):
                for index, text in enumerate(sentences):
                    frame = {
                        "type": "text",
                        "context_id": cid,
                        "text": text,
                        "continue": index < len(sentences) - 1,
                    }
                    await self.ws.send(json.dumps(frame, ensure_ascii=False))
                while not self.stop.is_set():
                    message = await self.next_message()
                    if message is None:
                        break
                    kind, incoming = message.get("type"), message.get("context_id")
                    if kind == "error" and incoming in (None, cid):
                        raise RuntimeError(
                            "Maya reported a turn error; do not replay automatically"
                        )
                    if incoming != cid:
                        continue  # Discard late packets/terminators from earlier turns.
                    if kind == "audio":
                        try:
                            audio = base64.b64decode(message["audio"], validate=True)
                        except (KeyError, ValueError, TypeError, binascii.Error):
                            raise ValueError("Invalid Base64 audio") from None
                        count += len(audio)
                        if count > self.rate * 2 * 120:
                            raise ValueError("Example audio budget exceeded")
                        carry += audio
                        usable = len(carry) - len(carry) % 2
                        if usable:
                            self.chunks += 1
                            if self.first_audio_ms is None:
                                self.first_audio_ms = (time.monotonic() - started) * 1000
                            chunk, carry = carry[:usable], carry[usable:]
                            yield chunk
                    elif kind == "cancelled":
                        self.cancelled = True
                        completed = True
                        return
                    elif kind == "end":
                        if carry or not count:
                            raise ValueError("Truncated or empty completed turn")
                        completed = True
                        return
            if self.stop.is_set():
                completed = True
        finally:
            if not completed and not self.stop.is_set():
                await self.interrupt()
            self.active = None


async def main(args):
    output = Path(args.output)
    if output.exists():
        raise ValueError("Output exists. Choose another --output")
    async with MayaSocket(
        os.getenv("MAYA_API_KEY", ""), args.model, args.voice, args.language
    ) as client:
        pcm = bytearray()
        async for chunk in client.speak(args.text):
            pcm.extend(chunk)
            if args.cancel_after_chunks and client.chunks >= args.cancel_after_chunks:
                await client.interrupt()
        if client.cancelled:
            print("Turn cancelled. Partial audio was discarded; no completed WAV written.")
            return
        with output.open("xb") as target, wave.open(target, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(client.rate)
            wav.writeframes(pcm)
        print(
            json.dumps(
                {
                    "output": str(output),
                    "pcm_bytes": len(pcm),
                    "sample_rate": client.rate,
                    "chunks": client.chunks,
                    "first_audio_ms": client.first_audio_ms,
                    "session_id": client.session_id,
                    "context_id": client.last_context_id,
                }
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="append", required=True)
    parser.add_argument(
        "--model", choices=["Maya Calyx"], default=os.getenv("MAYA_MODEL", "Maya Calyx")
    )
    parser.add_argument("--voice", default=os.getenv("MAYA_VOICE", "Aarav"))
    parser.add_argument("--language", default=os.getenv("MAYA_LANGUAGE") or None)
    parser.add_argument("--output", default="stream.wav")
    parser.add_argument("--cancel-after-chunks", type=int, default=0)
    try:
        asyncio.run(main(parser.parse_args()))
    except (Exception, KeyboardInterrupt):
        print(
            "Streaming failed or stopped. No complete result claimed; see troubleshooting.",
            file=sys.stderr,
        )
        sys.exit(1)
