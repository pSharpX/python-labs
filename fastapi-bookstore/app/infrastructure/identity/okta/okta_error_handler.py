import logging

from requests import Response
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class OktaErrorHandler:

    @staticmethod
    def raise_for_status(response: Response):
        """Checks whether the response was successful."""
        if 200 <= response.status_code < 300:
            # Pass through the response.
            return response

        logger.error(f"OKTA call got unexpected response: status_code = {response.status_code}, message = {response.json()}")
        raise AppException("OKTA call got unexpected response")

    @staticmethod
    def raise_api_error(exc_type, exc_val, exc_tb):
        """Wraps client error with custom API error"""
        logger.error(f"OKTA call failed: type = {exc_type}, value = {exc_val}, traceback = {exc_tb}")
        raise AppException(exc_val)