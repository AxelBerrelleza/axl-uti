---
name: stock-story
description: >-
  Generate a complete Stock Story investment-thesis draft page in Notion from a
  ticker (plus optional research material: docs, links, images). Collects
  financials/valuation/efficiency/competitors data via the repo's Morningstar
  client, renders the section charts, drafts every template section in English
  with an unbiased stance, and publishes a DRAFT page under
  Notas/Finance/Análisis Fundamental/Tesis Individuales/<TICKER>/Stock-Story-{quarter}
  for the human to review and edit. Use whenever the user asks to write,
  generate, update or automate a Stock Story, investment thesis, ticker report
  or "stock story" in Notion — even if they only give a ticker symbol.
---

# Stock Story generation

One pipeline, four stages. Run from the repo root with the venv active:

```bash
cd <repo-root> && source .venv/bin/activate
```

Inputs: a **ticker** and an optional **starting prompt** (recent quarter,
financial-report docs, analyst-estimate docs/links, images, other research).

## Stage 1 — collect

```bash
python -m stockstory.collect TICKER --workdir ~/.cache/stock-story/TICKER
```

(Use a persistent workdir like `~/.cache/stock-story/<TICKER>`, not `/tmp` —
tmp gets wiped between sessions and the stages need each other's outputs.)

Preflight `ntn` auth before anything Notion-facing: `python -m stockstory.notion`
(or `ntn whoami`); if it fails, stop and tell the user to run `ntn login`.

Read the printed coverage report; it drives the drafting stage.

## Stage 2 — charts

```bash
python -m stockstory.charts ~/.cache/stock-story/TICKER
```

Chart slots come from `stock-story-template.md` (see its "Chart slots" table).
Skipped slots are printed with reasons — never fake a chart.

## Stage 3 — draft (you are the author)

Read, in order:
1. `stock-story-template.md` (next to this file) — WHAT to write.
2. `stock-story-prompt.md` (next to this file) — HOW to write.
3. `~/.cache/stock-story/TICKER/data.json` — the numbers.
4. The user's starting prompt material — fetch links, read docs, carry images.

Then write `~/.cache/stock-story/TICKER/draft.md` following the template exactly, with
`@@CHART:<slot>@@` on its own line wherever a chart belongs. End the draft with
the **Open questions** section (business/market-specific ratios, missing
quarter, missing analyst estimates, operation/competitors/future expectations/
perspective — neutral phrasing).

Hard rules from the prompt file: English; every number traced to data.json or
cited material; bull and bear cases both steelmanned; gaps become notes or
questions, never inventions.

## Stage 4 — publish

```bash
python -m stockstory.publish ~/.cache/stock-story/TICKER --ticker TICKER --quarter 2025-Q2
```

`--quarter` comes from the starting prompt; omit it if not provided (page is
named `Stock-Story-draft` and the open questions ask for the quarter).
Re-running the same ticker+quarter replaces the page; a new quarter creates a
sibling.

## Stage 5 — report

Give the user: the page URL, the coverage gaps, skipped charts, what was
drafted from data vs. provided material, and anything that needs their input.
The page is a DRAFT; the human reviews and edits it in Notion.

## Files

- `stock-story-template.md` — section structure & chart slots (edit freely).
- `stock-story-prompt.md` — authoring rules (edit freely).
- Repo: `stockstory/` package (collect/charts/publish/notion + adapter + style),
  schema in `stockstory/schema.md`.
- Notion mechanics reused from the `odt-to-notion` skill (single-part uploads,
  marker swap, `after_block` positioning).
