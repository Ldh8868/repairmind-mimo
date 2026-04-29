from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

from app.config import Settings


class MiMoAPIError(RuntimeError):
    pass


class MiMoClient:
    """Minimal OpenAI-compatible chat client for Xiaomi MiMo.

    Official docs expose an OpenAI-compatible chat completions endpoint.
    Keep the client small so users can inspect and modify it easily.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self.settings.mimo_api_key) and not self.settings.demo_mode

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> Optional[str]:
        if not self.enabled:
            return None

        url = self.settings.mimo_base_url.rstrip("/") + "/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.settings.mimo_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.mimo_api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code >= 400:
            raise MiMoAPIError(f"MiMo API error {response.status_code}: {response.text[:500]}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise MiMoAPIError(f"Unexpected MiMo response schema: {data}") from exc
