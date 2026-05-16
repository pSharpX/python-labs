from abc import ABC, abstractmethod

class AiohttpInterceptor(ABC):

    @abstractmethod
    async def on_request_start(self, session, trace_config_ctx, params) -> None:
        pass

    @abstractmethod
    async def on_request_end(self, session, trace_config_ctx, params) -> None:
        pass

    @abstractmethod
    async def on_request_exception(self, session, trace_config_ctx, params) -> None:
        pass