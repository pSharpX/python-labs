import json
import logging
import time

import requests

from app.infrastructure.http.masking import MaskingService

logger = logging.getLogger(__name__)


class LoggingSession(requests.Session):

    def __init__(self):
        self.masking = MaskingService()
        super().__init__()

    def send(self, request, **kwargs):
        started_at = time.perf_counter()

        # ----------------------------
        # BEFORE REQUEST
        # ----------------------------
        logger.info(
            "Outgoing HTTP request: method = %s, url = %s, headers = %s, body = %s",
            request.method,
            request.url,
            self.masking.mask_headers(
                dict(request.headers)
            ),
            self.masking.mask_body(
                self._safe_json(request.body)
            )
        )

        try:
            response = super().send(request, **kwargs)
            elapsed_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2
            )

            # ----------------------------
            # AFTER RESPONSE
            # ----------------------------
            logger.info(
                "Incoming HTTP response: method = %s, url = %s, status_code = %s, elapsed_ms = %s, headers = %s, response = %s",
                request.method,
                request.url,
                response.status_code,
                elapsed_ms,
                self.masking.mask_headers(
                    dict(response.headers)
                ),
                self.masking.mask_body(
                    self._extract_response(response)
                )
            )

            return response
        except Exception as ex:
            elapsed_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2
            )

            logger.exception(
                "HTTP request execution failed: method = %s, url = %s, elapsed_ms = %s",
                request.method,
                request.url,
                elapsed_ms,
            )

            raise

    @staticmethod
    def _safe_json(body):

        if body is None:
            return None

        if isinstance(body, bytes):
            body = body.decode()

        try:
            return json.loads(body)
        except Exception:
            return body

    @staticmethod
    def _extract_response(response):

        if not response.content:
            return None

        try:
            return response.json()
        except Exception:
            return response.text