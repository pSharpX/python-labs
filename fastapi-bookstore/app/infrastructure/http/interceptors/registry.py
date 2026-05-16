import aiohttp

from app.infrastructure.http.interceptors.logging_interceptor import LoggingInterceptor
from app.infrastructure.http.interceptors.aiohttp_interceptor import AiohttpInterceptor


class InterceptorRegistry:
    def __init__(self):
        self.registry: list[AiohttpInterceptor] = []
        self.registry.append(LoggingInterceptor())

    def add(self, custom_interceptor: AiohttpInterceptor) -> None:
        if custom_interceptor:
            self.registry.append(custom_interceptor)

    def build_trace_config(self) -> aiohttp.TraceConfig:
        trace_config = aiohttp.TraceConfig()

        for interceptor in self.registry:
            trace_config.on_request_start.append(
                interceptor.on_request_start
            )
            trace_config.on_request_end.append(
                interceptor.on_request_end
            )
            trace_config.on_request_exception.append(
                interceptor.on_request_exception
            )

        return trace_config