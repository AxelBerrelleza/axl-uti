class AxlError(Exception):
    pass


class ConfigMissingError(AxlError):
    pass


class ConfigInvalidError(AxlError):
    pass


class APIError(AxlError):
    def __init__(self, status_code: int, endpoint: str, detail: str = ""):
        self.status_code = status_code
        self.endpoint = endpoint
        self.detail = detail
        super().__init__(f"API error {status_code} on {endpoint}: {detail}")


class APIAuthError(APIError):
    def __init__(self, status_code: int, endpoint: str):
        super().__init__(status_code, endpoint, "Authentication failed")


class APIRateLimitError(APIError):
    def __init__(self, endpoint: str):
        super().__init__(429, endpoint, "Rate limit exceeded")


class APIServerError(APIError):
    def __init__(self, status_code: int, endpoint: str):
        super().__init__(status_code, endpoint, "Server error")


class NetworkError(AxlError):
    def __init__(self, endpoint: str, original_error: Exception | None = None):
        self.endpoint = endpoint
        self.original_error = original_error
        super().__init__(f"Network error on {endpoint}: {original_error}")
