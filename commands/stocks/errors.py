from commands.errors import AxlError


class SymbolNotFoundError(AxlError):
    def __init__(self, ticker: str, available: str | None = None):
        self.ticker = ticker
        self.available = available
        msg = f"Ticker '{ticker}' not found"
        if available:
            msg += f". Available tickers: [{available}]"
        super().__init__(msg)


class SymbolResolveError(AxlError):
    def __init__(self, ticker: str, reason: str):
        self.ticker = ticker
        self.reason = reason
        super().__init__(f"Cannot resolve '{ticker}': {reason}")
