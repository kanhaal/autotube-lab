import base64
import json

from app.editorial.ollama import OllamaJsonClient, OllamaJsonError


def test_json_client_uses_configured_model(monkeypatch):
    seen = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"response": '{"ok": true}'}).encode()

    def fake_urlopen(req, timeout):
        seen.update(json.loads(req.data))
        return Response()

    monkeypatch.setattr("app.editorial.ollama.urllib.request.urlopen", fake_urlopen)
    client = OllamaJsonClient(model="qwen3.5:9b")

    assert client.generate_json("system", {"x": 1}) == {"ok": True}
    assert seen["model"] == "qwen3.5:9b"


def test_json_client_sends_local_images_to_ollama(monkeypatch, tmp_path):
    seen = {}
    image = tmp_path / "contact.jpg"
    image.write_bytes(b"visual-bytes")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"response": '{"ok": true}'}).encode()

    def fake_urlopen(req, timeout):
        seen.update(json.loads(req.data))
        return Response()

    monkeypatch.setattr("app.editorial.ollama.urllib.request.urlopen", fake_urlopen)

    result = OllamaJsonClient().generate_json(
        "system",
        {"x": 1},
        image_paths=(image,),
    )

    assert result == {"ok": True}
    assert seen["images"] == [base64.b64encode(b"visual-bytes").decode("ascii")]


def test_json_client_repairs_invalid_json_once(monkeypatch):
    replies = iter(["not json", '{"fixed": 1}'])

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"response": next(replies)}).encode()

    monkeypatch.setattr(
        "app.editorial.ollama.urllib.request.urlopen",
        lambda req, timeout: Response(),
    )

    assert OllamaJsonClient().generate_json(
        "s", {"x": 1}, repair_prompt="return valid json"
    ) == {"fixed": 1}


def test_json_client_fails_after_one_repair(monkeypatch):
    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return json.dumps({"response": "still invalid"}).encode()

    monkeypatch.setattr(
        "app.editorial.ollama.urllib.request.urlopen",
        lambda req, timeout: Response(),
    )

    try:
        OllamaJsonClient().generate_json("s", {}, repair_prompt="repair")
    except OllamaJsonError:
        return

    raise AssertionError("expected OllamaJsonError")
