import asyncio
import contextlib

from app.application.use_cases.process_outbox.handler import ProcessOutboxHandler


class OutboxWorker:
    def __init__(
            self,
            handler: ProcessOutboxHandler
    ):
        self.handler = handler
        self.running = False
        self.task = None

    async def start(self):
        self.running = True

        self.task = asyncio.create_task(
            self.run()
        )

    async def run(self):
        while self.running:
            try:
                await self.handler.handle()
            except Exception as ex:
                print(ex)

            await asyncio.sleep(5)

    async def stop(self):
        self.running = False

        if self.task:
            self.task.cancel()

            with contextlib.suppress(
                    asyncio.CancelledError
            ):
                await self.task