from uplink import AiohttpClient
from uplink.auth import ApiTokenHeader

from app.application.ports.identity import IdentityProvider
from app.infrastructure.identity.okta.okta_settings import OktaSettings
from app.infrastructure.identity.okta.okta_client import OktaClient
from app.infrastructure.identity.okta.models import CreateUser


class OktaIdentityProvider(IdentityProvider):

    def __init__(self, settings: OktaSettings):
        self.settings = settings
        self.okta_client = OktaClient(
            settings.org_url,
            auth=ApiTokenHeader("Authorization", f"SSWS {settings.token}"),
            client=AiohttpClient()
        )

    async def create_user(self, email: str, first_name: str, last_name: str, phone: str) -> str:
        create_user = CreateUser.create(email=email, first_name=first_name, last_name=last_name, phone=phone)
        return await self.okta_client.create_user(create_user.model_dump())