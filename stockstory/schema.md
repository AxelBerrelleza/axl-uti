# `data.json` contract (stock-story pipeline)

Produced by `stockstory.collect` (adapter → normalize), consumed by
`stockstory.charts` and the drafting agent. Stable keys only — downstream
stages must never depend on source-specific field names.

```jsonc
{
  "ticker": "AMZN",
  "performance_id": "0P000000B7",
  "generated_at": "2026-07-07T12:00:00Z",      // ISO-8601 UTC
  "source_adapter": "repo-morningstar",
  "currency": "USD",                            // spot-quote TRADING currency
  "statement_currency": "MXN",                  // REPORTING currency of the statements,
                                                 // from the adapter footer; null if unknown
  "units": {                                    // global unit declarations
    "money": "billions",                        // statement values (repo adapter)
    "pct": "percent",                           // 12.3 means 12.3%
    "ratios": "raw"                             // 24.5 means 24.5x
  },

  "price": {                                    // spot quote only (no history series)
    "last": 266.0, "change_pct": 3.97,
    "week52_high": 287.0, "week52_low": 196.0,
    "market_cap": 2800000.0,                    // raw currency units
    "currency": "USD", "exchange": "XNAS"
  },

  "statements": {                               // multi-year, annual
    "income_statement":  {"columns": ["2023","2024","2025","TTM"],
                          "period_end_dates": ["20231231","20241231","20251231","20260630"],
                          "rows": {"Total Revenue": [574.79, 637.96, 716.92, 775.68]},
                          "currency": "MXN",                  // statement footer currency
                          "order_of_magnitude": "Billion"},   // statement footer magnitude
    "balance_sheet":     {"columns": [...], "period_end_dates": [...], "rows": {...}},
    "cash_flow":         {"columns": [...], "period_end_dates": [...], "rows": {...}}
  },

  "financial_health": {                         // per fiscal period (Solvency & Liquidity)
    "periods": ["2016-12", "2017-12", "..."],
    "series": {"currentRatio": [1.04, 1.09, "..."],
               "quickRatio": ["..."], "financialLeverage": ["..."],
               "debtEquityRatio": ["..."], "interestCoverage": ["..."]}
  },

  "operating_efficiency": {                     // per fiscal year (Profitability)
    "periods": ["2016", "2017", "...", "Current", "5-Yr Avg"],
    "series": {"gross_margin": ["..."], "operating_margin": ["..."],
               "net_margin": ["..."], "ebitda_margin": ["..."],
               "roa": ["..."], "roe": ["..."], "roic": ["..."],
               "interest_coverage": ["..."]}
  },

  "avg_valuation": {                            // Avg 5-yr valuation section
    "columns": ["Industry", "5-Yr Avg", "Current", "2016", "...", "YTD"],
    "series": {"Price/Earnings": ["..."], "Price/Book": ["..."],
               "Price/Sales": ["..."], "Price/CF": ["..."],
               "EV/EBITDA": ["..."], "PEG Ratio": ["..."]}
  },

  "fair_value": {                               // Morningstar fair-value history
    "columns": ["2016", "...", "YTD"],
    "price": ["..."], "fair_value": ["..."], "price_to_fair_value": ["..."]
  },

  "competitors": [                              // Competitors & Industry section
    {"ticker": "MSFT", "name": "Microsoft Corp", "price": 513.53,
     "currency": "USD", "pe": 29.63, "price_to_cf": 11.53,
     "operating_margin_pct": 46.78, "revenue_growth_pct": 17.75}
  ],

  "coverage": {                                 // what the adapter could/couldn't get
    "available": ["statements", "financial_health", "..."],
    "missing": [{"field": "price_history",
                 "reason": "repo adapter only provides spot quote"},
                {"field": "analyst_estimates",
                 "reason": "excluded by design; user must provide material"}]
  }
}
```

Rules:
- Missing values inside series are `null`, never omitted keys.
- Every collected section appears under `coverage.available`; every known gap
  under `coverage.missing` with a reason. Downstream stages skip artifacts
  whose data is missing instead of failing.
- Analyst estimates / target prices are **never** auto-collected (by design).
