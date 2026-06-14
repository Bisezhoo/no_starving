from typing import Any, AsyncIterator

import httpx


class OpenRouterClient:
    def __init__(self, api_key: str, model: str, base_url: str, timeout_seconds: float = 30):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds

    async def stream_chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "stream": True,
        }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds, trust_env=False) as client:
            async with client.stream("POST", "chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line
