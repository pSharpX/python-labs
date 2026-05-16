import json
import logging
import time

from app.infrastructure.http.masking import MaskingService
from app.infrastructure.http.interceptors.aiohttp_interceptor import AiohttpInterceptor

logger = logging.getLogger(__name__)


class LoggingInterceptor(AiohttpInterceptor):

    def __init__(self):
        self.masking = MaskingService()

    async def on_request_start(
        self,
        session,
        trace_config_ctx,
        params,
    ):
        trace_config_ctx.started_at = time.perf_counter()
        request_body = getattr(
            trace_config_ctx,
            "trace_request_ctx",
            {}
        ).get("request_body")

        logger.info(
            "Outgoing HTTP request: method = %s, url = %s, headers = %s, body = %s",
            params.method,
            params.url,
            self.masking.mask_headers(
                dict(params.headers)
            ),
            self.masking.mask_body(
                self._safe_json(request_body)
            )
        )

    async def on_request_end(
        self,
        session,
        trace_config_ctx,
        params,
    ):
        elapsed_ms = round(
            (
                time.perf_counter()
                - trace_config_ctx.started_at
            ) * 1000,
            2
        )

        response = params.response
        try:
            response_body = await response.json()
        except Exception:
            response_body = await response.text()

        logger.info(
            "Incoming HTTP response: method = %s, url = %s, status_code = %s, elapsed_ms = %s, headers = %s, response = %s",
            params.method,
            str(params.url),
            response.status,
            elapsed_ms,
            self.masking.mask_headers(dict(response.headers)),
            self.masking.mask_body(response_body),
        )

    async def on_request_exception(
        self,
        session,
        trace_config_ctx,
        params,
    ):
        elapsed_ms = round(
            (
                time.perf_counter()
                - trace_config_ctx.started_at
            ) * 1000,
            2
        )

        logger.exception(
            "HTTP request failed: method = %s, url = %s, elapsed_ms = %s",
            params.method,
            str(params.url),
            elapsed_ms,
        )

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