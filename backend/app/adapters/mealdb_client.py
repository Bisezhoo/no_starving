from typing import Any

import httpx


class MealDbClient:
    def __init__(self, base_url: str, timeout_seconds: float = 8, proxy: str | None = None, trust_env: bool = True):
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds
        self.proxy = proxy
        self.trust_env = trust_env

    async def search(self, query: str) -> dict[str, Any]:
        return await self._get("search.php", {"s": query})

    async def filter_by_ingredient(self, ingredient: str) -> dict[str, Any]:
        return await self._get("filter.php", {"i": ingredient})

    async def filter_by_category(self, category: str) -> dict[str, Any]:
        return await self._get("filter.php", {"c": category})

    async def filter_by_area(self, area: str) -> dict[str, Any]:
        return await self._get("filter.php", {"a": area})

    async def lookup(self, meal_id: str) -> dict[str, Any]:
        return await self._get("lookup.php", {"i": meal_id})

    async def random(self) -> dict[str, Any]:
        return await self._get("random.php", {})

    async def _get(self, endpoint: str, params: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            proxy=self.proxy,
            trust_env=self.trust_env,
        ) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
