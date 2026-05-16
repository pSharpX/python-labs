from uplink import post, Body, headers, json, returns, error_handler, response_handler, Consumer

from app.infrastructure.identity.okta.okta_error_handler import OktaErrorHandler
from app.infrastructure.http.client.uplink_client import BaseHttpClient


@headers({
    "Content-Type": "application/json",
    "Accept": "application/json",
})
@error_handler(OktaErrorHandler.raise_api_error)
@response_handler(OktaErrorHandler.raise_for_status)
class OktaClient(BaseHttpClient):

    @json
    @returns.json(key="id")
    @post("/api/v1/users")
    async def create_user(self, user: Body) -> str:
        """Register a new Okta user"""
        pass