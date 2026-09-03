# Stock Story Template

Canonical structure for a Stock Story draft page. Derived from the conforming
stories AMZN, GOOGL, MSCI, SPGI. This file is read at run time by the drafting
agent and by the chart stage; edit it to change future outputs — no code
changes needed.

- Language: English
- Page location: `Notas/Finance/Análisis Fundamental/Tesis Individuales/<TICKER>/Stock-Story-{recent-quarter}`
- Sections marked `required` must always appear; `optional` sections appear
  only when data or user material supports them.

## Sections

### 1. Summary `required`
Two-to-four sentence snapshot: what the company does, how the stock is priced
vs. its history and vs. fair value, and the one-line stance of the thesis.
Numbers only from `data.json` or cited material.

### 2. About `required`
What the business is, how it makes money, scale (market cap, geography).
Chart slot: none.
Note: the repo data source provides no company profile; draft from user
material if provided, otherwise keep it short and flag the gap in open
questions.

#### 2.1 10K Definitions and comments `required`
Key terms or accounting definitions worth understanding before reading the
financials, plus comments on anything unusual in the 10-K/annual report.
Driven by user material; if none provided, list the definitions the reader
needs and note the report hasn't been reviewed yet.

### 3. Financial performance & health `required`
Intro line framing the multi-year trend. Every subsection below pulls from
`data.json`.

#### 3.1 Revenue break down `optional`
Segment/geography mix. Chart slot: `revenue_breakdown`.
Data source gap: aggregate statements only — use user material if provided,
otherwise replace with a short note + an open question.

#### 3.2 Solvency & Liquidity Ratios `required`
Current/quick ratio, leverage, debt/equity, interest coverage across the
periods in `financial_health`. Chart slot: `solvency_liquidity`.

#### 3.3 Profitability `required`
Margins (gross/operating/net/EBITDA), ROA/ROE/ROIC vs the 5-yr average and
industry from `operating_efficiency`. Chart slot: `profitability`.

#### 3.4 Growth `required`
Revenue and earnings growth over the statement years + TTM, 5-yr averages.
Chart slot: `growth`.

### 4. Company's past `required`
How the market has priced the company over time. Chart slots:
`price_vs_fair_value` (monthly close vs Morningstar fair value), then
`avg_valuation`.

#### 4.1 Avg. 5-yr Valuation `required`
Current multiples vs 5-yr average and industry (`avg_valuation`): P/E,
P/B, P/S, P/CF, EV/EBITDA, PEG. State where the discount/premium is.

### 5. Upsides and Downsides `required`
Two bulleted lists — `Upsides:` and `Downsides:` as bold labels, bullets
underneath. Balanced and evidence-backed; no cheerleading, no doom.

#### 5.1 Competitors & Industry `required`
Peer comparison from `competitors` (P/E, P/S, operating margin, revenue
growth) plus where the company sits in its industry.

### 6. Conclusion and personal perspective `required`
Synthesis + the author's view. Clearly separate what the data shows from the
personal interpretation. End with what would change the thesis.

### 7. Ownership `optional`
Insider/institutional ownership if material is provided. (Seen in MSCI.)

### 8. Open questions `required, generated`
Auto-appended by the pipeline. Neutral, company-specific questions about
ratios, business model, operation, market, competitors, future expectations
and perspective; also any missing inputs (recent quarter, analyst estimates,
segment data, company profile). This is where the human picks up.

## Chart slots

| slot | section | data needed |
|---|---|---|
| `revenue_breakdown` | 3.1 | segment data (user material; usually missing) |
| `solvency_liquidity` | 3.2 | `financial_health` |
| `profitability` | 3.3 | `operating_efficiency` |
| `growth` | 3.4 | `statements.income_statement` |
| `price_vs_fair_value` | 4 | `fair_value.monthly` |
| `avg_valuation` | 4.1 | `avg_valuation` |

Charts missing their data are skipped and reported, never faked.
