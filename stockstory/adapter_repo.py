"""First data adapter: wraps this repo's Morningstar-backed API layer.

Covers (per live probing): financials (IS/BS/CF), financial health,
operating efficiency, avg valuation, price vs fair value (incl. a monthly
close + P/FV history series since 2016), competitors, and the spot quote.

Known, reported gaps: analyst estimates (excluded by design — user must
provide material) and `overview` (endpoint 503s; company profile comes from
user-provided material or open questions).

Adapter interface: expose NAME and `collect(ticker, performance_id)` returning
{"sections": {schema-key: normalized-dict}, "missing": [{field, reason}]}.
Normalization happens here; downstream stages only see the data.json contract
(stockstory/schema.md).
"""

from typing import Any

from commands.stocks import morning_star as ms

NAME = "repo-morningstar"

# dataList-style payloads: date-ish keys that are not metric series
_DATE_KEYS = {"fiscalPeriodYearMonth", "fiscalPeriodYear", "morningstarEndingDate"}


def _datalist_to_series(data: dict) -> dict:
    rows = data.get("dataList", [])
    periods: list[str] = []
    series: dict[str, list[Any]] = {}
    for row in rows:
        period = str(row.get("fiscalPeriodYearMonth") or row.get("fiscalPeriodYear"))
        periods.append(period)
        for k, v in row.items():
            if k in _DATE_KEYS:
                continue
            series.setdefault(k, []).append(v)
    return {"periods": periods, "series": series}


def _statements(raw: dict) -> dict:
    mapping = {
        "incomeStatement": "income_statement",
        "balanceSheet": "balance_sheet",
        "cashFlow": "cash_flow",
    }
    out = {}
    for src, dst in mapping.items():
        stmt = raw.get(src)
        if not stmt or not stmt.get("rows"):
            continue
        out[dst] = {
            "columns": stmt.get("columnDefs", []),
            "period_end_dates": stmt.get("columnDefs_labels", []),
            "rows": {r["label"]: r.get("datum") for r in stmt["rows"]},
        }
    return out


def _price_vs_fair_value(raw: dict) -> dict:
    chart = (raw.get("chart") or {}).get("chartDatums") or {}
    monthly = []
    for year in chart.get("yearly", []):
        for m in year.get("monthly", []):
            monthly.append(
                {
                    "date": m.get("fairValueMonthlyDate"),
                    "close": float(m["close"]) if m.get("close") not in (None, "_PO_") else None,
                    "price_to_fair_value": (
                        float(m["priceFairValue"])
                        if m.get("priceFairValue") not in (None, "_PO_")
                        else None
                    ),
                }
            )
    recent = chart.get("recent") or {}
    out: dict[str, Any] = {"monthly": monthly}
    if recent.get("latestClose") not in (None, "_PO_"):
        out["latest_close"] = float(recent["latestClose"])
    if recent.get("latestFairValue") not in (None, "_PO_"):
        out["latest_fair_value"] = float(recent["latestFairValue"])
    return out


def _avg_valuation(raw: dict) -> dict:
    def view(key):
        v = raw.get(key) or {}
        return {r["label"]: r.get("datum") for r in v.get("rows", [])}

    exp = raw.get("Expanded") or {}
    return {
        "columns": exp.get("columnDefs", []),
        "series": view("Expanded"),  # PEG, EV/EBIT, yields, ...
        "core_series": view("Collapsed"),  # P/S, P/E, P/CF, P/B
    }


def _competitors(raw: dict) -> list:
    out = []
    for c in raw.get("competitors", []):
        out.append(
            {
                "ticker": c.get("ticker"),
                "name": c.get("name"),
                "price": c.get("lastCloseDB"),
                "currency": c.get("lastCloseCurrencyDB"),
                "pe": c.get("priceEarnings"),
                "price_to_sales": c.get("priceSale"),
                "operating_margin_pct": c.get("operatingMargin"),
                "revenue_growth_pct": c.get("revenueGrowth"),
            }
        )
    return out


def _spot_price(raw: list) -> dict:
    if not raw:
        return {}
    d = raw[0]
    return {
        "last": d.get("lastPrice"),
        "change_pct": d.get("dayChangePer"),
        "week52_high": d.get("yearRangeHigh"),
        "week52_low": d.get("yearRangeLow"),
        "market_cap": d.get("marketCap"),
        "currency": d.get("currencyCode"),
        "exchange": d.get("exchangeID"),
    }


def collect(ticker: str, performance_id: str) -> dict:
    sections, missing = {}, []

    def grab(key, fn, normalize=lambda x: x):
        try:
            sections[key] = normalize(fn(performance_id))
        except Exception as e:
            missing.append({"field": key, "reason": f"{type(e).__name__}: {e}"})

    grab("statements", ms.getFinancials, _statements)
    grab("financial_health", ms.getFinancialHealth, _datalist_to_series)
    grab("operating_efficiency", ms.getOperatingEfficency, _datalist_to_series)
    grab("avg_valuation", ms.getAvgValuation, _avg_valuation)
    grab("fair_value", ms.getPriceVsFairValue, _price_vs_fair_value)
    grab("competitors", ms.getCompetitors, _competitors)

    try:
        sections["price"] = _spot_price(ms.getInstrumentsPrice([ticker]))
    except Exception as e:
        missing.append({"field": "price", "reason": f"{type(e).__name__}: {e}"})

    missing.append(
        {"field": "analyst_estimates", "reason": "excluded by design; user must provide material"}
    )
    missing.append(
        {
            "field": "company_profile",
            "reason": "overview endpoint unavailable (503); use user material",
        }
    )

    is_rows = sections.get("statements", {}).get("income_statement", {}).get("rows", {})
    has_segments = any(
        any(
            k in label.lower()
            for k in ("segment", "division", "north america", "international", " aws")
        )
        for label in is_rows
    )
    if not has_segments:
        missing.append(
            {
                "field": "segment_breakdown",
                "reason": "statements are aggregate-only; Revenue break down "
                "needs user material or open questions",
            }
        )
    return {"sections": sections, "missing": missing}
