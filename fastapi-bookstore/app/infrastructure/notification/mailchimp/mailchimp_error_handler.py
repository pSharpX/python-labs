import logging

from requests import Response
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class MailchimpErrorHandler:

    @staticmethod
    def raise_for_status(response: Response):
        """Checks whether the response was successful."""
        if 200 <= response.status_code < 300:
            # Pass through the response.
            return response

        response_text = response.text
        try:
            error_payload = response.json()
        except Exception as exc:
            logger.error(f"Error parsing response: {type(exc).__name__}: {str(exc)}")
            error_payload = response_text

        logger.error(
            f"HTTP request failed: status_code = {response.status_code}, url = {response.url}, response = {error_payload}",
        )
        raise AppException(f"HTTP request failed: status_code = {response.status_code}")

    @staticmethod
    def raise_api_error(exc_type, exc_val, exc_tb):
        """Wraps client error with custom API error"""
        logger.error(f"HTTP request failed: type = {exc_type}, value = {exc_val}, traceback = {exc_tb}")
        raise AppException(exc_val)