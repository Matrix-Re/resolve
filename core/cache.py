import os
import time
from dataclasses import dataclass

from core.message import DNSQuery, DNSResponse


@dataclass
class CacheEntry:
    response: DNSResponse
    expires_at: float


class DNSCache:
    """
    Simple in-memory DNS cache with TTL support.
    """

    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}

    def build_key(self, query: DNSQuery) -> str:
        return f"{query.domain}:{query.record_type}"

    def get(self, query: DNSQuery) -> DNSResponse | None:
        key = self.build_key(query)
        entry = self._entries.get(key)

        if entry is None:
            return None

        if time.time() >= entry.expires_at:
            del self._entries[key]
            return None

        return entry.response

    def set(self, query: DNSQuery, response: DNSResponse) -> None:
        if response.ttl is None or response.ttl <= 0:
            return

        key = self.build_key(query)
        expires_at = time.time() + response.ttl

        self._entries[key] = CacheEntry(
            response=response,
            expires_at=expires_at,
        )

    def clear(self) -> None:
        self._entries.clear()

    def size(self) -> int:
        return len(self._entries)

    def display(self) -> None:
        """
        Clear the console and display the current cache content with TTL countdown.
        """
        os.system("cls" if os.name == "nt" else "clear")

        print("=== DNS Cache ===")

        if not self._entries:
            print("Cache empty")
            print("=================")
            return

        current_time = time.time()
        expired_keys: list[str] = []

        print(f"{'Key':<35} {'Domain':<25} {'Type':<8} {'Value':<25} {'TTL left':<10}")
        print("-" * 110)

        for key, entry in self._entries.items():
            ttl_left = int(entry.expires_at - current_time)

            if ttl_left <= 0:
                expired_keys.append(key)
                continue

            response = entry.response

            print(
                f"{key:<35} "
                f"{str(response.domain):<25} "
                f"{str(response.record_type):<8} "
                f"{str(response.value):<25} "
                f"{ttl_left:<10}"
            )

        for key in expired_keys:
            del self._entries[key]

        if len(self._entries) == 0:
            print("Cache empty")

        print("=================")
