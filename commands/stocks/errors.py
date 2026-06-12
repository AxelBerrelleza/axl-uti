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


class ComparatorError(AxlError):
    def __init__(self, phase: str, original_error: Exception, symbol: str | None = None):
        self.symbol = symbol
        self.phase = phase
        self.original_error = original_error
        if symbol:
            msg = f"Failed loading {phase} for '{symbol}': {original_error}"
        else:
            msg = f"Failed loading {phase}: {original_error}"
        super().__init__(msg)
