from app.core.container import Container


class ContainerStarter:

    def __init__(self):
        self.container = Container()
        self.runtime = self.container.messaging_dependencies.messaging_runtime()

    def initialize(self):
        self.container.init_resources()

    def destroy(self):
        self.container.shutdown_resources()

    async def start(self):
        await self.runtime.start()

    async def stop(self):
        await self.runtime.stop()