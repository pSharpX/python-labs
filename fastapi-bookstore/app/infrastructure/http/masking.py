from typing import Any


class MaskingService:

    SENSITIVE_HEADERS = {
        "authorization",
        "x-api-key",
        "cookie",
        "set-cookie",
    }

    SENSITIVE_FIELDS = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "client_secret",
        "api_key",
    }

    @classmethod
    def mask_headers(cls, headers: dict):
        masked = {}

        for key, value in headers.items():
            if key.lower() in cls.SENSITIVE_HEADERS:
                masked[key] = "***MASKED***"
            else:
                masked[key] = value

        return masked

    @classmethod
    def mask_body(cls, data: Any):
        if isinstance(data, dict):
            result = {}

            for key, value in data.items():
                if key.lower() in cls.SENSITIVE_FIELDS:
                    result[key] = "***MASKED***"

                elif isinstance(value, (dict, list)):
                    result[key] = cls.mask_body(value)

                else:
                    result[key] = value
            return result

        elif isinstance(data, list):
            return [
                cls.mask_body(item)
                for item in data
            ]

        return data