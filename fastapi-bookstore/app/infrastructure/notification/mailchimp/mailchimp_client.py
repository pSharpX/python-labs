from uplink import post, Body, headers, json, returns, error_handler, response_handler, Consumer

from app.infrastructure.http.client.async_uplink_client import AsyncBaseHttpClient
from app.infrastructure.notification.mailchimp.mailchimp_error_handler import MailchimpErrorHandler


@headers({
    "Content-Type": "application/json",
    "Accept": "application/json",
})
@error_handler(MailchimpErrorHandler.raise_api_error)
@response_handler(MailchimpErrorHandler.raise_for_status)
class MailchimpClient(AsyncBaseHttpClient):

    @json
    @returns.json(key="_id")
    @post("/messages/send-template")
    async def send_notification(self, user: Body) -> str:
        """Send email notification using a template"""
        pass
