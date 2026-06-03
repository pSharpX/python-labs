from dependency_injector import containers, providers

from app.infrastructure.notification.mailchimp import MailchimpSettings, MailchimpNotificationSender
from app.infrastructure.notification.mailchimp.mailchimp_client import MailchimpClient
from app.infrastructure.notification.mailchimp.mailchimp_authenticator import MailchimpAuthenticator


class MailchimpContainer(containers.DeclarativeContainer):

    mailchimp_settings = providers.ThreadSafeSingleton(MailchimpSettings)

    mailchimp_authenticator = providers.Factory(MailchimpAuthenticator, settings=mailchimp_settings)
    mailchimp_client = providers.Factory(
        MailchimpClient,
        base_url=mailchimp_settings.provided.base_url,
        interceptors=providers.List(
            mailchimp_authenticator
        )
    )

    notification_sender = providers.Factory(MailchimpNotificationSender, client=mailchimp_client)