import io
import json
import urllib.error
import wave
from types import SimpleNamespace

import pytest
from conftest import http_recipe as m


@pytest.mark.parametrize(
    "model,voice", [(m, v) for m, vs in m.CATALOG["models"].items() for v in vs]
)
def test_documented_voice_pairs(model, voice):
    assert m.payload("Hello", model, voice)["voice"] == voice


@pytest.mark.parametrize("language", m.CATALOG["languages"])
def test_documented_language_codes(language):
    assert m.payload("Synthetic test", language=language)["language"] == language


@pytest.mark.parametrize(
    "kwargs",
    [
        {"text": ""},
        {"text": "  "},
        {"text": 4},
        {"text": "x" * 5001},
        {"model": "maya calyx"},
        {"model": "Unsupported Model", "voice": "Aarav"},
        {"voice": "aarav"},
        {"voice": "Nobody"},
        {"language": "en-US"},
        {"language": "en-IN"},
        {"language": "xx"},
        {"speed": True},
        {"speed": False},
        {"speed": "1"},
        {"speed": 0},
        {"speed": float("nan")},
        {"speed": float("inf")},
        {"speed": 1.26},
        {"model": "Maya Calyx", "voice": "Aarav", "speed": 1},
    ],
)
def test_bad_input_fails_before_network(kwargs):
    with pytest.raises(ValueError):
        m.payload(**({"text": "Hello"} | kwargs))


@pytest.mark.parametrize("speed", [0.5, 0.75, 1, 1.25])
def test_calyx_rejects_speed(speed):
    with pytest.raises(ValueError, match="does not accept speed"):
        m.payload("Hello", speed=speed)


def test_calyx_only_catalog_and_defaults():
    assert set(m.CATALOG["models"]) == {"Maya Calyx"}
    assert len(m.CATALOG["models"]["Maya Calyx"]) == 24
    assert not set(m.CATALOG["models"]["Maya Calyx"]) & set(m.CATALOG["excluded_calyx_voices"])
    assert m.payload("Hello") == {"text": "Hello", "model": "Maya Calyx", "voice": "Aarav"}


def test_mixed_language_not_forced():
    assert "language" not in m.payload("नमस्ते hello")


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
def test_excluded_speakers_cannot_be_selected(voice):
    with pytest.raises(ValueError):
        m.payload("Hello", "Maya Calyx", voice)


@pytest.mark.parametrize(
    "header,rate",
    [
        ("audio/L16; rate=24000; channels=1", 24000),
        ('audio/l16; channels=1; rate="16000"', 16000),
        ("audio/L16; rate=8000", 8000),
    ],
)
def test_metadata_rate_not_request_rate(header, rate):
    assert m.pcm_rate(header) == rate


@pytest.mark.parametrize(
    "header",
    [
        "",
        "application/json",
        "audio/wav",
        "audio/basic; rate=8000",
        "audio/L16",
        "audio/L16; rate=44100",
        "audio/L16; rate=24000; channels=2",
        "audio/L16; rate=NaN",
        "audio/L16; rate=0",
    ],
)
def test_bad_format_rejected(header):
    with pytest.raises(ValueError):
        m.pcm_rate(header)


@pytest.mark.parametrize("rate", [8000, 16000, 24000])
def test_pcm_preserved_exactly_in_wav(tmp_path, rate):
    pcm = b"\x01\x02\xfe\xff" * 100
    path = tmp_path / "out.wav"
    m.save_wav(path, pcm, rate)
    with wave.open(str(path), "rb") as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (1, 2, rate)
        assert wav.readframes(wav.getnframes()) == pcm
    with pytest.raises(FileExistsError):
        m.save_wav(path, b"\x00\x00", rate)
    assert path.read_bytes()[44:] == pcm


@pytest.mark.parametrize("pcm", [b"", b"\x00", b"123"])
def test_no_file_for_incomplete_pcm(tmp_path, pcm):
    path = tmp_path / "out.wav"
    with pytest.raises(ValueError):
        m.save_wav(path, pcm, 24000)
    assert not path.exists()


class Response(io.BytesIO):
    def __init__(self, body=b"\x01\x00" * 100, status=200, content_type=None):
        super().__init__(body)
        self.status = status
        self.headers = {
            "Content-Type": content_type or "audio/L16; rate=16000; channels=1",
            "x-request-id": "synthetic-request",
        }


def test_http_headers_format_and_key_location():
    def open_request(req, timeout):
        assert req.full_url == m.ENDPOINT
        assert "test-key-not-live" not in req.full_url
        assert req.get_header("Authorization") == "Bearer test-key-not-live"
        assert req.get_header("User-agent")
        assert json.loads(req.data)["text"] == "नमस्ते"
        return Response()

    pcm, rate, report = m.synthesize(
        m.payload("नमस्ते"), "test-key-not-live", opener=SimpleNamespace(open=open_request)
    )
    assert len(pcm) == 200 and rate == 16000
    assert report["request_id"] == "synthetic-request"


@pytest.mark.parametrize("code", [400, 401, 403, 429, 500, 502, 503])
def test_http_error_no_audio_or_retry(code):
    calls = []

    def fail(req, timeout):
        calls.append(req)
        raise urllib.error.HTTPError(m.ENDPOINT, code, "secret-canary", {}, None)

    with pytest.raises(RuntimeError) as error:
        m.synthesize(m.payload("Hi"), "test-key-not-live", opener=SimpleNamespace(open=fail))
    assert len(calls) == 1
    assert "secret-canary" not in str(error.value)


@pytest.mark.parametrize(
    "response",
    [
        Response(b""),
        Response(b"a"),
        Response(b'{"error":"oops"}', content_type="application/json"),
        Response(status=206),
    ],
)
def test_invalid_http_success_is_not_audio(response):
    with pytest.raises(ValueError):
        m.synthesize(
            m.payload("Hi"),
            "test-key-not-live",
            opener=SimpleNamespace(open=lambda *a, **k: response),
        )


def test_redirect_refused():
    with pytest.raises(ValueError, match="redirect"):
        m.NoRedirects().redirect_request(None, None, 302, None, {}, "https://elsewhere.invalid")


@pytest.mark.parametrize("key", ["", " ", "bad\rkey", "bad\nkey"])
def test_bad_key_before_io(key):
    with pytest.raises(ValueError):
        m.synthesize(m.payload("Hello"), key)
