from dependency_injector import containers, providers
from uplink.auth import ApiTokenHeader

from app.infrastructure.identity.okta import OktaSettings, OktaIdentityProvider
from app.infrastructure.identity.okta.okta_client import OktaClient


def get_okta_authenticator(settings: OktaSettings) -> ApiTokenHeader:
    return ApiTokenHeader("Authorization", f"SSWS {settings.token}")

class OktaContainer(containers.DeclarativeContainer):

    okta_settings = providers.ThreadSafeSingleton(OktaSettings)

    okta_authenticator = providers.Callable(
        get_okta_authenticator,
        settings=okta_settings
    )
    okta_client = providers.Factory(
        OktaClient,
        base_url=okta_settings.provided.org_url,
        auth=okta_authenticator
    )

    identity_provider = providers.Factory(OktaIdentityProvider, client=okta_client)