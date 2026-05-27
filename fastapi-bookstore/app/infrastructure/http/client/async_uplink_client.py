from uplink import Consumer, AiohttpClient

from app.infrastructure.http.interceptors.registry import InterceptorRegistry
from app.infrastructure.http.config.aiohttp_interceptable_client import InterceptableClientSession
from app.infrastructure.http.interceptors.aiohttp_interceptor import AiohttpInterceptor
from app.infrastructure.http.interceptors.request_interceptor import RequestInterceptor


class AsyncBaseHttpClient(Consumer):

    def __init__(self, base_url: str, interceptors=None, **kwargs):
        if interceptors is None:
            interceptors = []
        readable_interceptors = [interceptor for interceptor in interceptors if
                                  isinstance(interceptor, AiohttpInterceptor)]
        mutable_interceptors = [interceptor for interceptor in interceptors if
                                 isinstance(interceptor, RequestInterceptor)]
        registry = InterceptorRegistry(interceptors=readable_interceptors)
        session = InterceptableClientSession(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            trace_configs=[registry.build_trace_config()],
            interceptors=mutable_interceptors,
        )

        super().__init__(
            base_url=base_url,
            client=AiohttpClient(session=session),
            **kwargs
        )