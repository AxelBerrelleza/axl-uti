from dataclasses import dataclass


@dataclass
class ComparatorInput:
    currentRatio: float | None = None
    quickRatio: float | None = None
    debtToEquity: float | None = None
    roe: float | None = None
    netMargin: float | None = None
    per: float | None = None
    pcf: float | None = None
    ps: float | None = None
    pbv: float | None = None
