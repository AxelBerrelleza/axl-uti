#!/usr/bin/env python3
"""ntn CLI preflight + shared Notion helpers for the stock-story pipeline.

Fails fast with actionable guidance when the ntn CLI is missing or logged out,
so a long generation run doesn't die at the publishing step.
"""
import json
import shutil
import subprocess
import sys


class NtnError(RuntimeError):
    pass


def ntn_api(args: list[str], body: dict | None = None) -> dict:
    """Run `ntn api <args>` and return parsed JSON. Raises NtnError on failure."""
    cmd = ["ntn", "api"] + args
    if body is not None:
        cmd += ["-d", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise NtnError(f"ntn api failed: {r.stderr.strip()}")
    return json.loads(r.stdout)


def preflight() -> str:
    """Check ntn is installed and authenticated. Returns the workspace name."""
    if shutil.which("ntn") is None:
        raise NtnError("ntn CLI not found on PATH. Install it first (see notion-cli skill).")
    r = subprocess.run(["ntn", "whoami"], capture_output=True, text=True)
    if r.returncode:
        raise NtnError(
            "ntn is not authenticated. Run `ntn login` in a terminal, then retry.\n"
            f"(ntn said: {r.stderr.strip() or r.stdout.strip()})"
        )
    return (r.stdout or "unknown workspace").strip()


def set_title(page_id: str, title: str) -> None:
    """ntn pages create does not always set the page title property; force it."""
    ntn_api([f"v1/pages/{page_id}", "-X", "PATCH"],
            {"properties": {"title": [{"text": {"content": title}}]}})


def find_child_pages(block_id: str) -> dict[str, str]:
    """Return {lowercased title: page id} for child_page blocks of block_id."""
    out, cursor = {}, None
    while True:
        args = [f"v1/blocks/{block_id}/children", "page_size==100"]
        if cursor:
            args.append(f"starting_cursor=={cursor}")
        d = ntn_api(args)
        for b in d["results"]:
            if b["type"] == "child_page":
                out[b["child_page"]["title"].strip().lower()] = b["id"]
        if not d["has_more"]:
            return out
        cursor = d["next_cursor"]


if __name__ == "__main__":
    try:
        print("ntn OK:", preflight())
    except NtnError as e:
        sys.exit(str(e))
