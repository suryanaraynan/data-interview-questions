"""
House style for Data Explained visuals: report- and dashboard-grade charts and tables.

Every visual should look like it came out of a real analytics team's monthly pack:
  - a headline that states the finding (not "Chart of X")
  - a subtitle with what is plotted, units and period
  - the data that matters highlighted; context data muted
  - annotations on the numbers the text quotes
  - targets, thresholds, benchmarks or last-year lines drawn in where they exist
  - a source footer

Usage from a post's analysis.py:
    import sys; from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    import viz_style as vs
    fig, ax = vs.figure()
    ...
    vs.headline(fig, "Finding as a sentence", "What, units, period")
    vs.footer(fig, "Synthetic data modelled on ... | Data Explained #001")
    vs.save(fig, HERE / "chart_1.png")
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

# ---------------------------------------------------------------- palette
SURFACE = "#fcfcfb"
INK = "#0b0b0b"          # primary text
INK_2 = "#52514e"        # secondary text, axis labels
INK_3 = "#8a8984"        # footers, faint notes
GRID = "#e6e5e1"
MUTED = "#c3c2bc"        # context data (daily noise, other groups, last year)
SHADE = "#f0efec"        # period / event shading

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # categorical, fixed order
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
DIVERGING = ["#184f95", "#6da7ec", "#f0efec", "#ec835a", "#d03b3b"]  # blue <-> red, grey mid
STATUS = {"good": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}

SEQ_CMAP = LinearSegmentedColormap.from_list("seq_blue", BLUE_RAMP)
DIV_CMAP = LinearSegmentedColormap.from_list("div_blue_red", DIVERGING)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
})


# ---------------------------------------------------------------- layout
def figure(width=10.0, height=5.4, nrows=1, ncols=1, **kw):
    """Figure with room above the plot for a headline + subtitle and below for a footer."""
    fig, axes = plt.subplots(nrows, ncols, figsize=(width, height), dpi=150, **kw)
    fig.subplots_adjust(top=0.80, bottom=0.14, left=0.07, right=0.84)
    for ax in np.atleast_1d(axes).ravel():
        style_axes(ax)
    return fig, axes


def style_axes(ax, grid="y"):
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, labelsize=8)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
    else:
        ax.grid(False)


def headline(fig, title, subtitle=None):
    """Title = the finding, as a sentence. Subtitle = what is plotted, units, period."""
    fig.text(0.07, 0.95, title, fontsize=13, fontweight="bold", color=INK, va="top")
    if subtitle:
        fig.text(0.07, 0.885, subtitle, fontsize=9.5, color=INK_2, va="top")


def footer(fig, text):
    fig.text(0.07, 0.025, text, fontsize=7.5, color=INK_3, va="bottom")


# ---------------------------------------------------------------- annotation
def callout(ax, x, y, text, dx=30, dy=30, color=INK, marker_color=None, ha="left"):
    """A dot on the data point with a short leader line to a label."""
    ax.scatter([x], [y], s=36, color=marker_color or color, zorder=5,
               edgecolors=SURFACE, linewidths=1.5)
    ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=8.5, color=color, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=INK_3, lw=0.8, shrinkA=0, shrinkB=4))


def ref_line(ax, y, label, color=INK_2, style="--", label_color=INK_2):
    """Target / threshold / benchmark line, labelled in the right margin.
    For a threshold use color=STATUS["critical"]; the label stays in text ink."""
    ax.axhline(y, color=color, lw=1.2, ls=style, zorder=2)
    ax.text(1.01, y, label, transform=ax.get_yaxis_transform(), fontsize=8,
            color=label_color, va="center", ha="left")


def shade(ax, x0, x1, label=None, y_label=0.97, color=SHADE):
    """Shade a period (winter, outage, campaign, policy change) and label it at the top."""
    ax.axvspan(x0, x1, color=color, zorder=0, lw=0)
    if label:
        ax.text(x0 + (x1 - x0) / 2, y_label, label, transform=ax.get_xaxis_transform(),
                fontsize=7.5, color=INK_2, ha="center", va="top")


def end_label(ax, x, y, text, color=INK, dx=6):
    """Direct label at the end of a line (use instead of / alongside a legend)."""
    ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points",
                fontsize=8.5, color=color, va="center", ha="left")


# ---------------------------------------------------------------- tables
def table_png(df, path, title, subtitle=None, footer_text=None, highlight_rows=(),
              col_formats=None, col_width=1.35, row_height=0.32):
    """Render a DataFrame as a clean report table image (header rule, zebra-free,
    right-aligned numbers, optional highlighted rows)."""
    col_formats = col_formats or {}
    n_rows, n_cols = df.shape
    width = max(6.0, col_width * n_cols + 0.6)
    extra = (subtitle or "").count("\n")
    height = row_height * (n_rows + 1) + 1.3 + 0.22 * extra
    fig = plt.figure(figsize=(width, height), dpi=150)
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.70 - 0.05 * extra])
    ax.axis("off")
    fig.text(0.04, 0.96, title, fontsize=12, fontweight="bold", color=INK, va="top")
    if subtitle:
        fig.text(0.04, 0.885, subtitle, fontsize=9, color=INK_2, va="top")
    if footer_text:
        fig.text(0.04, 0.02, footer_text, fontsize=7.5, color=INK_3, va="bottom")

    cells = [[col_formats.get(c, "{}").format(v) for c, v in row.items()] for _, row in df.iterrows()]
    tbl = ax.table(cellText=cells, colLabels=list(df.columns), loc="upper left",
                   cellLoc="right", colLoc="right", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    from pandas.api.types import is_numeric_dtype
    pd_is_numeric = [is_numeric_dtype(t) for t in df.dtypes]
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(SURFACE)
        cell.set_linewidth(0)
        cell.set_facecolor(SURFACE)
        cell.set_text_props(color=INK, fontsize=9)
        if not pd_is_numeric[c]:
            cell.set_text_props(ha="left")
            cell._loc = "left"
        if r == 0:
            cell.set_text_props(color=INK_2, fontsize=8.5, fontweight="bold")
            cell.visible_edges = "B"
            cell.set_edgecolor(INK_2)
            cell.set_linewidth(1)
        elif (r - 1) in highlight_rows:
            cell.set_facecolor("#e8f1fc")
            cell.set_text_props(fontweight="bold")
    fig.savefig(path)
    plt.close(fig)


def save(fig, path):
    fig.savefig(path)
    plt.close(fig)
