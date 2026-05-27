from uplink import post, Body, headers, json, returns, error_handler, response_handler, Consumer

from app.infrastructure.identity.okta.okta_error_handler import OktaErrorHandler
from app.infrastructure.http.client.async_uplink_client import AsyncBaseHttpClient


@headers({
    "Content-Type": "application/json",
    "Accept": "application/json",
})
@error_handler(OktaErrorHandler.raise_api_error)
@response_handler(OktaErrorHandler.raise_for_status)
class OktaClient(AsyncBaseHttpClient):

    @json
    @returns.json(key="id")
    @post("/api/v1/users")
    async def create_user(self, user: Body) -> str:
        """Register a new Okta user"""
        pass

    @json
    @returns.json(key="id")
    @post("/api/v1/users?activate=true&provider=false&nextLogin=changePassword")
    async def create_user_with_credentials(self, user: Body) -> str:
        """Register a new Okta user with credentials"""
        pass

    @json
    @post("/api/v1/users/{user_id}/lifecycle/activate?sendEmail=true")
    async def activate(self, user_id) -> str:
        """Activate an Okta user"""
        pass

    @json
    @headers({
        "Prefer": "respond-async",
    })
    @post("/api/v1/users/{user_id}/lifecycle/deactivate?sendEmail=false")
    async def deactivate(self, user_id) -> None:
        """Deactivate an Okta user"""
        pass