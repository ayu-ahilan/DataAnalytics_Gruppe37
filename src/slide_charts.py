"""Charts for the presentation slides, in the colour scheme of the slides.

Run after notebook 02 (needs the table 'analysis'):

    python -m src.slide_charts

Writes outputs/slide_chart_*.png.
"""
import matplotlib.pyplot as plt
import pandas as pd

from . import config
from .db import get_connection

INK, MUTED, BG, GRID = "#16202E", "#55606E", "#F6F4EF", "#DDD8CE"
BLUE, ORANGE = "#2E5E9E", "#D2631F"
REGIONS = [("German-speaking", BLUE, "German-speaking"), ("Romandy", ORANGE, "Romandy")]

plt.rcParams.update({
    "font.family": "Arial", "font.size": 20, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
})

FILTER = ("t.arr_scheduled IS NOT NULL AND t.cancelled = 0 AND t.arr_status = 'REAL' "
          "AND t.arr_delay_min BETWEEN -10 AND 180")
FUNNEL = [
    ("All train stops (Switzerland)", "SELECT COUNT(*) FROM stops t"),
    ("with scheduled arrival", "SELECT COUNT(*) FROM stops t WHERE t.arr_scheduled IS NOT NULL"),
    ("not cancelled", "SELECT COUNT(*) FROM stops t WHERE t.arr_scheduled IS NOT NULL AND t.cancelled = 0"),
    ("actual time measured (REAL)", "SELECT COUNT(*) FROM stops t WHERE t.arr_scheduled IS NOT NULL "
                                    "AND t.cancelled = 0 AND t.arr_status = 'REAL'"),
    ("plausible delay", f"SELECT COUNT(*) FROM stops t WHERE {FILTER}"),
    ("+ stations (join on bpuic)", f"SELECT COUNT(*) FROM stops t JOIN stations s ON s.bpuic = t.bpuic WHERE {FILTER}"),
    ("+ weather (top 100, hour)", "SELECT COUNT(*) FROM analysis"),
]


def delay_by_hour(conn, path):
    d = pd.read_sql("""
        SELECT region, CAST(strftime('%H', arr_scheduled) AS INT) AS hour,
               100.0 * AVG(arr_delay_min >= 3) AS share
        FROM analysis WHERE region IN ('German-speaking', 'Romandy')
        GROUP BY 1, 2""", conn)
    d = d[d.hour >= 5]  # night hours have too few trains
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    for a, b in [(6, 9), (16, 19)]:
        ax.axvspan(a - 0.5, b - 0.5, color=GRID, alpha=0.6, lw=0)
    top = d["share"].max() * 1.12
    for x in (7, 17):
        ax.text(x, top * 0.95, "Peak hours", ha="center", color=MUTED, fontsize=17)
    for region, col, label in REGIONS:
        s = d[d.region == region].sort_values("hour")
        ax.plot(s.hour, s.share, color=col, lw=3.5, marker="o", ms=6)
        last = s.iloc[-1]
        ax.text(last.hour + 0.4, last.share, label, color=col, fontsize=19, va="center", fontweight="bold")
    ax.set_xlim(4.5, 27.0); ax.set_ylim(0, top)
    ax.set_xticks(range(6, 24, 3)); ax.set_xticklabels([f"{h}:00" for h in range(6, 24, 3)])
    ax.set_ylabel("Share of late arrivals (≥ 3 min) in %"); ax.set_xlabel("Scheduled arrival time")
    ax.grid(axis="y", color=GRID, lw=1); ax.set_axisbelow(True)
    ax.spines["bottom"].set_bounds(4.5, 23.5)
    plt.tight_layout(); plt.savefig(path, dpi=200); plt.close(fig)


def integration_funnel(conn, path):
    labels = [label for label, _ in FUNNEL][::-1]
    values = [conn.execute(q).fetchone()[0] for _, q in FUNNEL][::-1]
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    ax.barh(labels, values, color=[ORANGE] + [BLUE] * (len(values) - 1), height=0.62)
    for y, v in enumerate(values):
        ax.text(v + max(values) * 0.012, y, f"{v:,}", va="center", fontsize=18, color=INK)
    ax.set_xlim(0, max(values) * 1.25)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: "0" if x == 0 else f"{x / 1e6:g} M"))
    ax.set_xlabel("Number of records")
    ax.tick_params(axis="y", length=0, labelsize=19, labelcolor=INK)
    ax.spines["left"].set_visible(False)
    plt.tight_layout(); plt.savefig(path, dpi=200); plt.close(fig)


def inherited_vs_gained(conn, path):
    d = pd.read_sql("""
        SELECT region,
               AVG(arr_delay_min >= 3) AS late,
               AVG(CASE WHEN arr_delay_min >= 3 THEN prev_dep_delay >= 3 END) AS late_already_before
        FROM analysis WHERE region IN ('German-speaking', 'Romandy') AND prev_dep_delay IS NOT NULL
        GROUP BY region""", conn).set_index("region")
    fig, ax = plt.subplots(figsize=(10.4, 6.0))
    for i, (region, col, label) in enumerate(REGIONS):
        before = 100 * d.loc[region, "late"] * d.loc[region, "late_already_before"]
        new = 100 * d.loc[region, "late"] - before
        ax.barh(i, before, color=col, height=0.55)
        ax.barh(i, new, left=before, color=col, alpha=0.35, height=0.55)
        ax.text(before + new + 0.15, i, f"{before + new:.1f}% late", va="center", fontsize=19, color=INK)
    ax.set_yticks([0, 1]); ax.set_yticklabels([r[2] for r in REGIONS])
    ax.set_xlabel("Share of late arrivals (≥ 3 min) in %")
    ax.set_xlim(0, 100 * d["late"].max() * 1.35); ax.set_ylim(-0.6, 1.9)
    ax.text(0, 1.62, "dark = already late at the previous stop,  light = new delay",
            fontsize=16, color=MUTED)
    ax.tick_params(axis="y", length=0, labelsize=20, labelcolor=INK); ax.spines["left"].set_visible(False)
    plt.tight_layout(); plt.savefig(path, dpi=200); plt.close(fig)


def main():
    conn = get_connection()
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    delay_by_hour(conn, config.OUTPUT_DIR / "slide_chart_delay_by_hour.png")
    integration_funnel(conn, config.OUTPUT_DIR / "slide_chart_integration_funnel.png")
    inherited_vs_gained(conn, config.OUTPUT_DIR / "slide_chart_inherited_delay.png")
    print("slide charts written to", config.OUTPUT_DIR)


if __name__ == "__main__":
    main()
