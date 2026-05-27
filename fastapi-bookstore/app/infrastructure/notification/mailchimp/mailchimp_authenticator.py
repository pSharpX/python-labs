import logging

from app.infrastructure.http.interceptors.request_interceptor import RequestInterceptor
from app.infrastructure.notification.mailchimp.mailchimp_settings import MailchimpSettings

logger = logging.getLogger(__name__)


class MailchimpAuthenticator(RequestInterceptor):

    def __init__(self):
        self.settings = MailchimpSettings()

    async def before_request(self, method: str, url: str, kwargs: dict):
        body = kwargs.get("json")

        if not isinstance(body, dict):
            return

        body["key"] = self.settings.api_key

        kwargs["json"] = body
