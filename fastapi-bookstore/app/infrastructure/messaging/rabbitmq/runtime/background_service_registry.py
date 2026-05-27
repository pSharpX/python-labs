import asyncio


class BackgroundServiceRegistry:

    def __init__(self, services: list):
        self.services = services
        self.tasks = []

    def register(self, service):
        self.services.append(service)

    async def start_all(self):
        for service in self.services:

            task = asyncio.create_task(
                service.start()
            )

            self.tasks.append(task)

    async def stop_all(self):
        for service in self.services:
            await service.stop()