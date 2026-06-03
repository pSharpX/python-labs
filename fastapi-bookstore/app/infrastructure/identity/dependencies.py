from dependency_injector import containers, providers

from app.infrastructure.identity.okta import OktaContainer
from app.infrastructure.identity.auth0 import Auth0Container
from app.configs import MainSettings


class IdentityContainer(containers.DeclarativeContainer):

    settings = providers.Dependency(instance_of=MainSettings)

    okta = providers.Container(OktaContainer)
    auth0 = providers.Container(Auth0Container)

    okta_provider = providers.Factory(
        lambda container: container.identity_provider(),
        okta,
    )

    auth0_provider = providers.Factory(
        lambda container: container.identity_provider(),
        auth0,
    )

    identity_provider = providers.Selector(
        settings.provided.identity_provider,
        okta=okta_provider,
        auth0=auth0_provider,
    )
