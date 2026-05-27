

class RequestInterceptor:

    async def before_request(
        self,
        method: str,
        url: str,
        kwargs: dict,
    ):
        pass