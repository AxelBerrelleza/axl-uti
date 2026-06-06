# axl-uti

A CLI for querying Morningstar stock data via RapidAPI.

## Setup

### 1. Python environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
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
python main.py stocks search MSFT
```

## Usage

```bash
python main.py --help
python main.py stocks search MSFT
python main.py stocks overview MSFT
# Use a raw PerformanceId directly (bypasses symbol lookup)
python main.py stocks overview --pid 0P000003MH
```