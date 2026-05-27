import logging

from app.application.ports.notification import NotificationSender
from app.application.ports.messaging import MessageHandler

logger = logging.getLogger(__name__)

class SendWelcomeNotificationHandler(MessageHandler):

    def __init__(
        self,
        notification_sender: NotificationSender,
    ):
        self.notification_sender = notification_sender

    async def handle(self, event: dict):
        logger.debug(f"Sending welcome notification: user_id = {event["user_id"]}")
        await self.notification_sender.send_welcome_email(
            email=event["email"],
            first_name=event["first_name"],
        )
        logger.debug(f"Notification sent successfully")