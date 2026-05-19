from uplink import Consumer

from infrastructure.http.middleware.logging_session import LoggingSession


class BaseHttpClient(Consumer):

    def __init__(self, base_url: str, **kwargs):
        session = LoggingSession()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },

        super().__init__(
            base_url=base_url,
            session=session,
            headers=headers,
            **kwargs
        )