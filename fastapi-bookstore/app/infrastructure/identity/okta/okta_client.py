from uplink import Consumer, post, Body, headers, json,returns


@headers({
    "Content-Type": "application/json",
    "Accept": "application/json",
})
class OktaClient(Consumer):

    @json
    @returns.json(key="id")
    @post("/api/v1/users")
    async def create_user(self, user: Body) -> str:
        """Register a new Okta user"""
        pass