import json
import wave

import httpx
import pytest
from conftest import scratch_recipe as m


class STTSocket:
    def __init__(self, messages):
        self.messages, self.sent, self.closed = messages, [], False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        self.closed = True

    async def send(self, frame):
        self.sent.append(frame)

    def __aiter__(self):
        self.items = iter(self.messages)
        return self

    async def __anext__(self):
        try:
            return json.dumps(next(self.items))
        except StopIteration:
            raise StopAsyncIteration from None


async def test_stt_final_tokens_only_and_required_finished():
    socket = STTSocket(
        [
            {"tokens": [{"text": "Wrong", "is_final": False}]},
            {"tokens": [{"text": "Hello", "is_final": True}]},
            {
                "tokens": [
                    {"text": " world", "is_final": True},
                    {"text": "<end>", "is_final": True},
                ],
                "finished": True,
            },
        ]
    )
    text = await m.transcribe(
        b"\x01\x00" * 100, 16000, "test-key-not-live", connector=lambda *a, **k: socket
    )
    assert text == "Hello world" and socket.closed
    assert json.loads(socket.sent[0])["model"] == "stt-rt-v5"
    assert socket.sent[-1] == ""


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"tokens": []}],
        [{"finished": True}],
        [{"error_code": 401}],
        [{"error_type": "invalid_request"}],
    ],
)
async def test_stt_missing_completion_or_error_is_not_success(messages):
    socket = STTSocket(messages)
    with pytest.raises(ExceptionGroup):
        await m.transcribe(
            b"\x01\x00", 16000, "test-key-not-live", connector=lambda *a, **k: socket
        )
    assert socket.closed


@pytest.mark.parametrize(
    "pcm,rate", [(b"", 16000), (b"a", 16000), (b"aa", 8000), (b"aa" * (16000 * 31), 16000)]
)
async def test_invalid_input_never_opens_stt(pcm, rate):
    with pytest.raises(ValueError):
        await m.transcribe(pcm, rate, "test-key-not-live", connector=None)


async def test_llm_exact_route_model_and_bounded_output():
    def handler(request):
        body = json.loads(request.content)
        assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
        assert body["model"] == "example/exact-model" and body["max_tokens"] == 1024
        return httpx.Response(
            200, json={"choices": [{"finish_reason": "stop", "message": {"content": "Hello!"}}]}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        assert (
            await m.reply("Hi", "test-key-not-live", "example/exact-model", client=client)
            == "Hello!"
        )


@pytest.mark.parametrize("status", [400, 401, 402, 429, 500, 502])
async def test_llm_errors_no_fallback(status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={"error": "secret-canary"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RuntimeError) as error:
            await m.reply("Hi", "test-key-not-live", "example/exact-model", client=client)
        assert "secret-canary" not in str(error.value) and len(calls) == 1


@pytest.mark.parametrize("content", [None, "", " ", 4, ["Hi"], "x" * 5001])
async def test_unusable_llm_content_rejected(content):
    def handler(request):
        return httpx.Response(
            200, json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError):
            await m.reply("Hi", "test-key-not-live", "example/exact-model", client=client)


@pytest.mark.parametrize("channels,width,rate", [(2, 2, 16000), (1, 1, 16000), (1, 2, 44100)])
def test_bad_input_wav_rejected(tmp_path, channels, width, rate):
    path = tmp_path / "input.wav"
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(width)
        wav.setframerate(rate)
        wav.writeframes(bytes(100))
    with pytest.raises(ValueError):
        m.read_input(path)


def test_exact_input_wav(tmp_path):
    path = tmp_path / "input.wav"
    m.save_wav(path, b"\x01\x02" * 20, 24000)
    assert m.read_input(path) == (b"\x01\x02" * 20, 24000)


@pytest.mark.parametrize("finish_reason", ["length", "content_filter", "tool_calls", None])
async def test_truncated_or_nonfinal_reply_never_becomes_speech(finish_reason):
    def handler(request):
        return httpx.Response(
            200,
            json={"choices": [{"finish_reason": finish_reason, "message": {"content": "Cut off"}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError, match="finish"):
            await m.reply("Hi", "test-key-not-live", "example/exact-model", client=client)


@pytest.mark.parametrize("choices", [None, [], [None], [{"finish_reason": "stop"}]])
async def test_malformed_llm_response_rejected(choices):
    def handler(request):
        return httpx.Response(200, json={"choices": choices})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ValueError):
            await m.reply("Hi", "test-key-not-live", "example/exact-model", client=client)


@pytest.mark.parametrize("language", ["hi", "te", "en"])
async def test_explicit_language_hint_not_silently_dropped(language):
    socket = STTSocket([{"tokens": [{"text": "Hello", "is_final": True}], "finished": True}])
    await m.transcribe(
        b"\x01\x00", 16000, "test-key-not-live", language=language, connector=lambda *a, **k: socket
    )
    config = json.loads(socket.sent[0])
    assert config["language_hints"] == [language] and config["language_hints_strict"] is True
