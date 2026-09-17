from __future__ import annotations

import json
import os
import urllib.request


class OllamaJsonError(RuntimeError):
    """Raised when Ollama does not return valid JSON after one repair attempt."""


class OllamaJsonClient:
    def __init__(
        self,
        model: str | None = None,
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 180,
    ):
        self.model = model or os.getenv("AUTOTUBE_LLM_MODEL", "qwen3.5:9b")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _call(self, prompt: str) -> str:
        body = json.dumps(
            {
                "model": self.model,
                "stream": False,
                "prompt": prompt,
            }
        ).encode()
        request = urllib.request.Request(
            self.base_url + "/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read())
        return payload["response"].strip()

    def generate_json(
        self,
        system_prompt: str,
        payload: dict,
        *,
        repair_prompt: str | None = None,
    ) -> dict:
        raw = self._call(
            system_prompt
            + "\n\nINPUT JSON:\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as first_error:
            if repair_prompt is None:
                raise OllamaJsonError(str(first_error)) from first_error

            repaired = self._call(repair_prompt + "\n\nBROKEN OUTPUT:\n" + raw)
            try:
                result = json.loads(repaired)
            except json.JSONDecodeError as second_error:
                raise OllamaJsonError(str(second_error)) from second_error

        if not isinstance(result, dict):
            raise OllamaJsonError("expected a JSON object")
        return result
