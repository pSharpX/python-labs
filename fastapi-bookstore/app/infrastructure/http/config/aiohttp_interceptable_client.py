import aiohttp

class InterceptableClientSession(aiohttp.ClientSession):

    async def _request(
        self,
        method,
        url,
        **kwargs,
    ):
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