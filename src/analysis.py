"""Run the SQL queries against the SQLite database, save results and draw charts.

Usage:
    python src/analysis.py data/lse_new_issues.db outputs
"""
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
AIM_COLOUR, MAIN_COLOUR, GREY = "#2a78b5", "#0b2545", "#9aa5b1"


def run_queries(con, out: Path) -> dict:
    results = {}
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        df = pd.read_sql_query(sql_file.read_text(), con)
        df.to_csv(out / f"{sql_file.stem}.csv", index=False)
        results[sql_file.stem] = df
    return results


def style(ax, title, ylabel):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)


def chart_ipo_count(by_market: pd.DataFrame, out: Path):
    pivot = (by_market[by_market.market_group != "Other (SFM/PSM)"]
             .pivot(index="year", columns="market_group", values="ipos").fillna(0))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    pivot[["Main Market", "AIM"]].plot(kind="bar", stacked=True, ax=ax,
                                        color=[MAIN_COLOUR, AIM_COLOUR], width=0.75)
    style(ax, "London IPOs per year, Main Market vs AIM", "Number of IPOs")
    ax.set_xlabel("")
    ax.set_xticklabels([f"{y}*" if y == 2026 else str(y) for y in pivot.index], rotation=0)
    ax.legend(frameon=False)
    fig.text(0.01, 0.01, "*2026 to 31 October. Excludes SFM/PSM. Source: London Stock Exchange, New Issues and IPOs.",
             fontsize=8, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out / "ipo_count_by_market.png", dpi=200)
    plt.close(fig)


def chart_new_money(totals: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colours = [GREY if y == 2026 else MAIN_COLOUR for y in totals.year]
    ax.bar(totals.year.astype(str), totals.new_money_gbp_m / 1000, color=colours)
    style(ax, "New money raised at IPO (£bn)", "£bn")
    for x, v in zip(totals.year.astype(str), totals.new_money_gbp_m / 1000):
        ax.annotate(f"{v:.1f}", (x, v), ha="center", va="bottom", fontsize=8)
    fig.text(0.01, 0.01, "2026 (grey) to 31 October. New-share money only, comparable across all years.",
             fontsize=8, color="grey")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out / "new_money_raised.png", dpi=200)
    plt.close(fig)


def chart_deal_size(con, out: Path) -> pd.DataFrame:
    # SQLite has no MEDIAN, so pull the IPO rows and compute it in pandas
    ipos = pd.read_sql_query(
        "SELECT year, raised_new_gbp_m FROM new_issues WHERE is_ipo = 1 AND year >= 2015", con)
    med = ipos.groupby("year")["raised_new_gbp_m"].median().round(1).rename("median_new_money_gbp_m")
    med.to_csv(out / "median_ipo_size.csv")
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(med.index.astype(str), med.values, marker="o", color=AIM_COLOUR)
    style(ax, "Median IPO size (new money, £m)", "£m")
    fig.tight_layout()
    fig.savefig(out / "median_ipo_size.png", dpi=200)
    plt.close(fig)
    return med.reset_index()


def main(db_path: str, out_dir: str):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        r = run_queries(con, out)
        chart_ipo_count(r["01_ipos_by_year_and_market"], out)
        chart_new_money(r["02_annual_totals"], out)
        med = chart_deal_size(con, out)
    print(r["02_annual_totals"].to_string(index=False))
    print(med.to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
