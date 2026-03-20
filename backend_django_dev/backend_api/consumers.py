import json

from channels.generic.websocket import AsyncWebsocketConsumer


class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        await self.accept()
        await self.send(
            text_data=json.dumps(
                {
                    "status": "connected",
                    "service": "backend_api",
                }
            )
        )

    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        if text_data is not None:
            await self.send(text_data=text_data)
        elif bytes_data is not None:
            await self.send(bytes_data=bytes_data)
