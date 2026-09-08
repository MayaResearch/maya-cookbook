import asyncio
import base64
import json

import pytest
from conftest import stream_recipe as m


class FakeSocket:
    def __init__(self, frames=None, metadata=None):
        self.sent, self.frames, self.closed = [], frames, False
        self.queue = asyncio.Queue()
        self.queue.put_nowait(
            json.dumps(
                metadata
                if metadata is not None
                else {
                    "type": "metadata",
                    "sample_rate": 24000,
                    "channels": 1,
                    "encoding": "pcm_s16le",
                    "session_id": "test-session",
                }
            )
        )

    async def send(self, text):
        data = json.loads(text)
        self.sent.append(data)
        if data["type"] == "text" and not data["continue"] and self.frames is not None:
            for frame in self.frames:
                self.queue.put_nowait(json.dumps({"context_id": data["context_id"], **frame}))

    async def recv(self):
        return await self.queue.get()

    async def close(self):
        self.closed = True

    async def connect(self, url, **kwargs):
        assert url == m.URL and "test-key-not-live" not in url
        assert kwargs["additional_headers"]["Authorization"] == "Bearer test-key-not-live"
        return self


def audio(data, **kwargs):
    return {"type": "audio", "audio": base64.b64encode(data).decode(), **kwargs}


async def collect(client, texts=None):
    return b"".join([chunk async for chunk in client.speak(texts or ["Hello"])])


async def test_metadata_before_text_unique_turns_same_connection():
    socket = FakeSocket([audio(b"\x01\x02"), {"type": "end"}])
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        assert await collect(client, ["First.", "Second."]) == b"\x01\x02"
        assert await collect(client) == b"\x01\x02"
    assert socket.sent[0]["type"] == "start" and socket.sent[0]["v2"]
    texts = [f for f in socket.sent if f["type"] == "text"]
    assert texts[0]["context_id"] == texts[1]["context_id"] != texts[2]["context_id"]
    assert [f["continue"] for f in texts] == [True, False, False]
    assert socket.sent[0]["model"] == "Maya Calyx"
    assert socket.sent[0]["voice"] == "Aarav"
    assert all("speed" not in f for f in socket.sent)
    assert socket.closed


@pytest.mark.parametrize(
    "kwargs",
    [
        {"model": "Unsupported Model"},
        {"model": "maya calyx"},
        {"voice": "aarav"},
        {"voice": "Nobody"},
        {"language": "en-US"},
    ],
)
def test_invalid_calyx_settings_fail_before_connect(kwargs):
    with pytest.raises(ValueError):
        m.MayaSocket("test-key-not-live", **kwargs)


@pytest.mark.parametrize(
    "voice",
    [
        "Jackson",
        "Riley",
        "Vance",
        "Christine",
        "Christopher",
        "Ananya",
        "Arjun",
        "Shailika",
        "Gargi",
    ],
)
def test_excluded_speakers_cannot_open_stream(voice):
    with pytest.raises(ValueError):
        m.MayaSocket("test-key-not-live", voice=voice)


@pytest.mark.parametrize(
    "metadata",
    [
        {"type": "error"},
        {"type": "audio"},
        [],
        "x",
        {"type": "metadata", "sample_rate": 24000, "channels": 2, "encoding": "pcm_s16le"},
        {"type": "metadata", "sample_rate": 44100, "channels": 1, "encoding": "pcm_s16le"},
        {"type": "metadata", "sample_rate": 24000, "channels": 1, "encoding": "mulaw"},
        {"type": "metadata", "sample_rate": "24000", "channels": 1, "encoding": "pcm_s16le"},
    ],
)
async def test_rejected_readiness_never_sends_text(metadata):
    socket = FakeSocket(metadata=metadata)
    with pytest.raises((ValueError, TypeError)):
        async with m.MayaSocket("test-key-not-live", connector=socket.connect):
            pytest.fail("Startup must not succeed")
    assert all(f["type"] == "start" for f in socket.sent)
    assert socket.closed


async def test_odd_network_chunks_are_reassembled_without_dropping_bytes():
    socket = FakeSocket([audio(b"a"), audio(b"bc"), audio(b"d"), {"type": "end"}])
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        assert await collect(client) == b"abcd"


@pytest.mark.parametrize(
    "frames",
    [
        [audio(b"a"), {"type": "end"}],
        [{"type": "end"}],
        [{"type": "audio", "audio": "***"}],
        [{"type": "audio", "audio": None}],
        [{"type": "error", "context_id": None}],
        [{"type": "error"}],
    ],
)
async def test_invalid_turns_fail_loudly(frames):
    socket = FakeSocket(frames)
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        with pytest.raises((ValueError, RuntimeError)):
            await collect(client)
        assert client.active is None


async def test_old_audio_and_end_cannot_finish_new_turn():
    socket = FakeSocket(
        [
            audio(b"bad!", context_id="old"),
            {"type": "end", "context_id": "old"},
            audio(b"good"),
            {"type": "end"},
        ]
    )
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        assert await collect(client) == b"good"


async def test_cancel_stops_locally_without_ack_then_reuse():
    socket = FakeSocket([audio(b"good"), audio(b"late"), {"type": "end"}])
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        received = []
        async for chunk in client.speak(["First turn"]):
            received.append(chunk)
            await client.interrupt()
        assert b"".join(received) == b"good" and client.cancelled
        assert await collect(client) == b"goodlate"
        assert not client.cancelled
    assert len([f for f in socket.sent if f["type"] == "cancel"]) == 1


async def test_cancel_unblocks_pending_receiver_without_reply():
    socket = FakeSocket()
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        task = asyncio.create_task(collect(client))
        await asyncio.sleep(0)
        await client.interrupt()
        assert await asyncio.wait_for(task, 0.5) == b""


async def test_cancelled_terminal_completes_without_end():
    socket = FakeSocket([{"type": "cancelled"}])
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        assert await collect(client) == b"" and client.cancelled


async def test_no_progress_times_out_and_cancels_once():
    socket = FakeSocket()
    async with m.MayaSocket("test-key-not-live", connector=socket.connect, deadline=0.01) as client:
        with pytest.raises(TimeoutError):
            await collect(client)
    assert len([f for f in socket.sent if f["type"] == "cancel"]) == 1


@pytest.mark.parametrize("texts", [[], [""], [" "], [4], ["x" * 5001]])
async def test_empty_or_oversized_input_no_text_sent(texts):
    socket = FakeSocket()
    async with m.MayaSocket("test-key-not-live", connector=socket.connect) as client:
        with pytest.raises(ValueError):
            async for _ in client.speak(texts):
                pass
    assert all(f["type"] == "start" for f in socket.sent)


async def test_socket_closed_on_exception():
    socket = FakeSocket()
    with pytest.raises(RuntimeError):
        async with m.MayaSocket("test-key-not-live", connector=socket.connect):
            raise RuntimeError("stop")
    assert socket.closed
