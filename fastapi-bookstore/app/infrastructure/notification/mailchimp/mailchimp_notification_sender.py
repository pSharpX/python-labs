
from app.application.ports.notification import NotificationSender
from app.infrastructure.notification.mailchimp.mailchimp_settings import MailchimpSettings
from app.infrastructure.notification.mailchimp.mailchimp_client import MailchimpClient
from app.infrastructure.notification.mailchimp.models import SendMessageWithTemplate
from app.infrastructure.notification.mailchimp.mailchimp_authenticator import \
    MailchimpAuthenticator


class MailchimpNotificationSender(NotificationSender):

    def __init__(self, settings: MailchimpSettings):
        self.settings = settings
        self.mailchimp_client = MailchimpClient(
            settings.base_url,
            interceptors=[
                MailchimpAuthenticator()
            ]
        )

    async def send_welcome_email(self, email: str, first_name: str) -> None:
        payload: SendMessageWithTemplate = SendMessageWithTemplate.create(
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
        await self.mailchimp_client.send_notification(payload)