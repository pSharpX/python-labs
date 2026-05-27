import aiohttp

from app.infrastructure.http.interceptors.request_interceptor import RequestInterceptor


class InterceptableClientSession(aiohttp.ClientSession):
    def __init__(
            self,
            *args,
            interceptors: list[RequestInterceptor] | None = None,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.interceptors = interceptors or []

    async def _request(
        self,
        method,
        url,
        **kwargs,
    ):
        # ---------------------------------
        # APPLY INTERCEPTORS
        # ---------------------------------
        for interceptor in self.interceptors:
            await interceptor.before_request(
                method,
                url,
                kwargs,
            )

        trace_request_ctx = kwargs.setdefault(
            "trace_request_ctx",
            {}
        )
        request_body = None
        if "json" in kwargs:
            request_body = kwargs["json"]

        elif "data" in kwargs:
            request_body = kwargs["data"]

        trace_request_ctx["request_body"] = request_body
        return await super()._request(
            method,
            url,
            **kwargs,
        )