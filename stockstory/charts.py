"""Charts stage: render data.json into the template's chart slot images.

Usage:
    python -m stockstory.charts WORKDIR [--template PATH]

Reads WORKDIR/data.json, renders every chart slot declared in the template
file's "Chart slots" table, writes WORKDIR/charts/<slot>.png and prints
"slot=path" lines (missing data -> "slot=SKIPPED (reason)").

Chart slots are driven by the template file, not hard-coded here: adding a
slot to the template table is enough if a renderer with that name exists.
"""

import argparse
import itertools
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from stockstory import style as S

SLOT_RE = re.compile(r"^\|\s*`([a-z_]+)`\s*\|", re.M)


def slots_from_template(template_path: Path) -> list[str]:
    text = template_path.read_text(encoding="utf-8")
    table = text.split("## Chart slots")[-1]
    return SLOT_RE.findall(table)


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- renderers


def solvency_liquidity(data: dict, out: Path):
    fh = data.get("financial_health")
    if not fh or not fh.get("series"):
        return None, "no financial_health data"
    # '2016-12' -> '2016'; named periods (e.g. '2026-Q2') kept as-is
    periods = [p[:4] if re.fullmatch(r"\d{4}-\d{2}", p) else p for p in fh["periods"]]
    series = fh["series"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(S.FIGSIZE[0], S.FIGSIZE[1]))
    fig.suptitle(
        "Solvency & Liquidity Ratios",
        x=0.02,
        ha="left",
        fontsize=14,
        fontweight="bold",
        color=S.INK,
    )

    for i, key in enumerate(("currentRatio", "quickRatio")):
        if key in series:
            ax1.plot(
                periods,
                [_num(v) for v in series[key]],
                marker="o",
                color=S.SERIES_COLORS[i],
                label=key,
            )
    ax1.set_title("Liquidity", loc="left")
    ax1.legend()

    for i, key in enumerate(("debtEquityRatio", "financialLeverage")):
        if key in series:
            ax2.plot(
                periods,
                [_num(v) for v in series[key]],
                marker="o",
                color=S.SERIES_COLORS[i + 2],
                label=key,
            )
    ax2.set_title("Leverage", loc="left")
    ax2.legend()

    for ax in (ax1, ax2):
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=S.DPI, bbox_inches="tight")
    plt.close(fig)
    return str(out), None


def profitability(data: dict, out: Path):
    oe = data.get("operating_efficiency")
    if not oe or not oe.get("series"):
        return None, "no operating_efficiency data"
    periods, series = oe["periods"], oe["series"]
    # keep fiscal years, the 5-yr average and any current/quarter column
    keep = [i for i, p in enumerate(periods) if p != "Index"]
    xs = [periods[i] for i in keep]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(S.FIGSIZE[0], S.FIGSIZE[1]))
    fig.suptitle("Profitability", x=0.02, ha="left", fontsize=14, fontweight="bold", color=S.INK)

    for i, key in enumerate(("grossMargin", "operatingMargin", "ebitdaMargin", "netMargin")):
        if key in series:
            ax1.plot(
                xs,
                [_num(series[key][j]) for j in keep],
                marker="o",
                color=S.SERIES_COLORS[i],
                label=key.replace("Margin", " margin"),
            )
    ax1.set_title("Margins (%)", loc="left")
    ax1.legend(fontsize=9)

    for i, key in enumerate(("roe", "roic", "roa")):
        if key in series:
            ax2.plot(
                xs,
                [_num(series[key][j]) for j in keep],
                marker="o",
                color=S.SERIES_COLORS[i],
                label=key.upper(),
            )
    ax2.set_title("Returns on capital (%)", loc="left")
    ax2.legend()

    for ax in (ax1, ax2):
        ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out, dpi=S.DPI, bbox_inches="tight")
    plt.close(fig)
    return str(out), None


def growth(data: dict, out: Path):
    is_rows = (data.get("statements", {}).get("income_statement") or {}).get("rows", {})
    revenue = is_rows.get("Total Revenue")
    columns = (data.get("statements", {}).get("income_statement") or {}).get("columns", [])
    if not revenue or not columns:
        return None, "no income statement data"
    years = [c for c in columns if c != "TTM"]
    rev = [_num(v) for v in revenue[: len(years)]]

    cur = data.get("statement_currency") or data.get("currency", "USD")
    fig, ax = S.new_figure(f"Growth — Total Revenue ({cur} billions)")
    ax.bar(years, rev, color=S.BLUE, width=0.55, label="Total Revenue")
    yoy = [None] + [((b - a) / a * 100) if a else None for a, b in itertools.pairwise(rev)]
    ax2 = ax.twinx()
    ax2.grid(False)
    ax2.plot(years, yoy, color=S.ORANGE, marker="o", label="Revenue YoY %")
    ax2.set_ylabel("YoY growth %", color=S.ORANGE)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    return S.finalize(fig, out), None


def price_vs_fair_value(data: dict, out: Path):
    fv = data.get("fair_value")
    monthly = (fv or {}).get("monthly") or []
    pts = [m for m in monthly if m.get("date") and m.get("close")]
    if len(pts) < 12:
        return None, "insufficient price/fair-value history"
    dates = pd.to_datetime([m["date"] for m in pts])
    closes = [m["close"] for m in pts]
    fvs = [
        (_num(m["close"]) / m["price_to_fair_value"])
        if m.get("price_to_fair_value") and 0.2 <= m["price_to_fair_value"] <= 3.0
        else None
        for m in pts
    ]

    fig, ax = S.new_figure("Price vs Morningstar Fair Value (monthly)")
    ax.plot(dates, closes, "-", color=S.BLUE, label="Close price")
    ax.plot(dates, fvs, "-", color=S.GREEN, label="Fair value (derived)")
    ax.legend()
    fig.autofmt_xdate()
    return S.finalize(fig, out), None


def avg_valuation(data: dict, out: Path):
    av = data.get("avg_valuation")
    if not av or not av.get("columns"):
        return None, "no avg_valuation data"
    cols = av["columns"]
    if cols and cols[0] == "Calendar":
        cols = cols[1:]  # label-column header; datum lists don't include it
    try:
        i_cur = cols.index("Current")
    except ValueError:  # current column renamed (e.g. '2026-Q2')
        cand = [i for i, c in enumerate(cols) if re.fullmatch(r"\d{4}-[QH]\d", c or "")]
        if not cand:
            return None, "avg_valuation current column not recognized"
        i_cur = cand[0]
    try:
        i_5y, i_idx = cols.index("5-Yr"), cols.index("Index")
    except ValueError:
        return None, "avg_valuation columns not recognized"

    rows = []
    for label, datum in (av.get("core_series") or {}).items():
        rows.append((label, datum[i_cur], datum[i_5y], datum[i_idx]))
    if not rows:
        return None, "no core valuation multiples"

    fig, ax = plt.subplots(figsize=(S.FIGSIZE[0], 0.6 * (len(rows) + 2) + 0.8))
    ax.set_title(
        f"Valuation — {cols[i_cur]} vs 5-yr average vs Industry",
        loc="left",
        pad=14,
        fontsize=14,
        fontweight="bold",
        color=S.INK,
    )
    ax.axis("off")
    table = ax.table(
        cellText=[[label, *_fmt3((cur, i5, idx))] for label, cur, i5, idx in rows],
        colLabels=["Multiple", cols[i_cur], "5-Yr Avg", "Industry"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8)
    for (r, _c), cell in table.get_celld().items():
        if r == 0:
            cell.set_facecolor(S.INK)
            cell.set_text_props(color="white", weight="bold")
        elif r % 2 == 0:
            cell.set_facecolor(S.LIGHT)
    return S.finalize(fig, out), None


def _fmt3(vals):
    out = []
    for v in vals:
        n = _num(v)
        out.append(f"{n:.2f}" if n is not None else "—")
    return out


RENDERERS = {
    "solvency_liquidity": solvency_liquidity,
    "profitability": profitability,
    "growth": growth,
    "price_vs_fair_value": price_vs_fair_value,
    "avg_valuation": avg_valuation,
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("workdir")
    p.add_argument(
        "--template",
        default=str(
            Path(__file__).resolve().parent.parent
            / ".agents/skills/stock-story/stock-story-template.md"
        ),
    )
    args = p.parse_args()

    workdir = Path(args.workdir)
    data = json.loads((workdir / "data.json").read_text(encoding="utf-8"))
    charts_dir = workdir / "charts"
    charts_dir.mkdir(exist_ok=True)

    slots = slots_from_template(Path(args.template))
    for slot in slots:
        fn = RENDERERS.get(slot)
        if fn is None:
            print(f"{slot}=SKIPPED (no renderer — needs user material or a new renderer)")
            continue
        try:
            path, err = fn(data, charts_dir / f"{slot}.png")
        except Exception as e:
            path, err = None, f"{type(e).__name__}: {e}"
        print(f"{slot}={path}" if path else f"{slot}=SKIPPED ({err})")


if __name__ == "__main__":
    main()
