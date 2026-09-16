"""Shared chart style for Stock Story images.

All charts render with one look so every ticker's story feels like the same
report. Sized for Notion page width, PNG, well under the 5 MB free-plan limit.
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# palette
INK = "#1a2332"
BLUE = "#2f6fb2"
ORANGE = "#e08a3c"
GREEN = "#3f9d6d"
RED = "#c25450"
GREY = "#8a93a3"
LIGHT = "#eef1f5"
SERIES_COLORS = [BLUE, ORANGE, GREEN, RED, "#7f5fb0", "#4fa3a5"]

FIGSIZE = (12, 5)
DPI = 140  # -> 1680px wide, Notion-friendly

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": GREY,
        "axes.grid": True,
        "grid.color": LIGHT,
        "grid.linewidth": 1.0,
        "axes.axisbelow": True,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "legend.frameon": False,
        "figure.dpi": DPI,
    }
)


def new_figure(title: str, tall: bool = False):
    fig, ax = plt.subplots(figsize=(FIGSIZE[0], FIGSIZE[1] + (1.5 if tall else 0)))
    ax.set_title(title, loc="left", pad=14)
    return fig, ax


def finalize(fig, out_path) -> str:
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return str(out_path)
