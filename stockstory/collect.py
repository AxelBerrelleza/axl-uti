"""Collect stage: ticker -> data.json (see stockstory/schema.md).

Usage:
    python -m stockstory.collect TICKER [--workdir DIR]

Writes DIR/data.json. The adapter is swappable (design D2); this entry point
normalizes adapter output into the stable contract and records coverage.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def build_dataset(ticker: str) -> dict:
    # imported lazily so `--help` never needs the API env
    from commands.stocks.symbols import resolve
    from stockstory import adapter_repo

    pid = resolve(ticker)
    result = adapter_repo.collect(ticker, pid)
    sections = result["sections"]

    currency = "USD"
    if sections.get("price", {}).get("currency"):
        currency = sections["price"]["currency"]

    return {
        "ticker": ticker,
        "performance_id": pid,
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "source_adapter": adapter_repo.NAME,
        "currency": currency,
        "units": {"money": "billions", "pct": "percent", "ratios": "raw"},
        **sections,
        "coverage": {
            "available": sorted(sections.keys()),
            "missing": result["missing"],
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Collect Stock Story dataset for a ticker")
    p.add_argument("ticker")
    p.add_argument("--workdir", default=".")
    args = p.parse_args()

    data = build_dataset(args.ticker)
    out = Path(args.workdir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "data.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    cov = data["coverage"]
    print(f"wrote {path} ({len(cov['available'])} sections)")
    for m in cov["missing"]:
        print(f"  missing: {m['field']} — {m['reason']}")


if __name__ == "__main__":
    main()
