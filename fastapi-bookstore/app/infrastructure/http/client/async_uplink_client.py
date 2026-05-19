from uplink import Consumer, AiohttpClient

from app.infrastructure.http.interceptors.registry import InterceptorRegistry
from app.infrastructure.http.config.aiohttp_interceptable_client import InterceptableClientSession


class AsyncBaseHttpClient(Consumer):

    def __init__(self, base_url: str, **kwargs):
        registry = InterceptorRegistry()
        session = InterceptableClientSession(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            trace_configs=[registry.build_trace_config()]
        )

        super().__init__(
            base_url=base_url,
            client=AiohttpClient(session=session),
            **kwargs
        )