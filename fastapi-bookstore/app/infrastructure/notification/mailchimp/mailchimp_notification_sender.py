import logging

from app.application.ports.notification import NotificationSender
from app.infrastructure.notification.mailchimp.mailchimp_client import MailchimpClient
from app.infrastructure.notification.mailchimp.models import SendMessageWithTemplate

logger = logging.getLogger(__name__)

class MailchimpNotificationSender(NotificationSender):

    def __init__(self, client: MailchimpClient):
        self.mailchimp_client = client

    async def send_welcome_email(self, email: str, first_name: str) -> None:
        send_notification = SendMessageWithTemplate.create(
            template_name="template-test",
            template_content=[
                {
                    "name": "application_name",
                    "content": "Bookstore"
                },
                {
                    "name": "current_year",
                    "content": "2006"
                },
                {
                    "name": "username",
                    "content": first_name
                }
            ],
            from_email="ce.rivera@globant.com",
            from_name="Christian",
            to_email=email,
            to_name=first_name,
            merge_language="handlebars",
            global_merge_vars=[]
        )

        response = await self.mailchimp_client.send_notification(send_notification.model_dump())
        logger.info(f"Notification sent to {email}: {response[0]["status"]}")