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
        "app.editorial.ollama.urllib.request.urlopen", lambda req, timeout: Response()
    )

    assert OllamaJsonClient().generate_json(
        "system", {"x": 1}, repair_prompt="return valid json"
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
        "app.editorial.ollama.urllib.request.urlopen", lambda req, timeout: Response()
    )

    try:
        OllamaJsonClient().generate_json("system", {}, repair_prompt="repair")
    except OllamaJsonError:
        return
    assert False, "expected OllamaJsonError"
