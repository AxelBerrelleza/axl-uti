# axl-uti

A CLI for querying Morningstar stock data via RapidAPI.

## Setup

### 1. Python environment

```bash
uv sync --extra dev
```

### 2. API key

```bash
cp .env.sample .env   # then open .env and set MS_API_KEY
```

### 3. Symbol config

Stock tickers are mapped to Morningstar PerformanceIds in a personal config file
that lives **outside version control**.

```bash
# Copy the example file and add your own tickers
cp symbols.example.json ~/.axl-uti/symbols.json
```

The file format is a simple JSON object:

```json
{
  "MSFT": "0P000003MH",
  "AAPL": "0P000000GY",
  "AMZN": "0P000000B7"
}
```

You can also place `symbols.json` in the project root as a **dev override** (it is
git-ignored). The CLI checks `./symbols.json` first, then `~/.axl-uti/symbols.json`.

To find the PerformanceId for any symbol, use the `search` command:

```bash
uv run python main.py stocks search MSFT
```

## Usage

`uv run` automatically uses the project's `.venv` without requiring manual activation.
If you already have the venv activated (`source .venv/bin/activate`), `python main.py` works identically.

```bash
# Recommended (no venv activation needed)
uv run python main.py --help
uv run python main.py stocks search MSFT
uv run python main.py stocks overview MSFT
# Use a raw PerformanceId directly (bypasses symbol lookup)
uv run python main.py stocks overview --pid 0P000003MH

# Also works with an activated venv
python main.py stocks search MSFT
```