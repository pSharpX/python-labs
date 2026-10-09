import httpx
from settings import AppSettings


class ProposalAPIClient:

    def __init__(self, settings: AppSettings):
        self.base_url = settings.backend_url

    def create_proposal(self, user_request: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/api/v1/proposals",
            json={"user_request": user_request},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def send_message(self, proposal_id: str, message: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/api/v1/proposals/{proposal_id}/messages",
            json={"message": message},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def get_proposal_full(self, proposal_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/api/v1/proposals/{proposal_id}", timeout=10.0
        )
        response.raise_for_status()
        return response.json()

    def submit_approval(
        self, proposal_id: str, action: str, feedback: str = None
    ) -> dict:
        response = httpx.post(
            f"{self.base_url}/api/v1/proposals/{proposal_id}/approval",
            json={"action": action, "feedback": feedback},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def get_document_download_url(self, proposal_id: str) -> str:
        return f"{self.base_url}/api/v1/proposals/{proposal_id}/document"

