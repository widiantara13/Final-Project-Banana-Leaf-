import asyncio
import json
from typing import Set, Dict, Any

class SSEBroadcaster:
    """
    Mengelola antrian koneksi Server-Sent Events (SSE)
    untuk menyiarkan event aktivitas secara real-time ke web admin dashboard.
    """
    def __init__(self):
        self._connections: Set[asyncio.Queue] = set()

    async def connect(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._connections.add(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue):
        self._connections.discard(queue)

    async def broadcast(self, data: Dict[str, Any]):
        """Mengirim pesan event ke semua client admin yang sedang membuka dashboard"""
        if not self._connections:
            return

        message = f"data: {json.dumps(data)}\n\n"
        for queue in list(self._connections):
            try:
                await queue.put(message)
            except Exception as e:
                print(f"[SSE Error] Gagal mengirim pesan ke antrian: {repr(e)}")

dashboard_broadcaster = SSEBroadcaster()

