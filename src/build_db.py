"""Load the LSE 'New Issues and IPOs' workbook into a SQLite database.

Usage:
    python src/build_db.py data/New_issues_and_IPOs.xlsx data/lse_new_issues.db
"""
import sqlite3
import sys

import pandas as pd

SHEET = "New Issues and IPOs"
HEADER_ROW = 7  # the column headers sit on row 8 of the sheet

RENAME = {
    "Market": "market",
    "Date": "admission_date",
    "Year": "year",
    "LSE IPO": "ipo_flag",
    "TIDM": "tidm",
    "Company": "company",
    "Issue type": "issue_type",
    "Transfer": "transfer",
    "Country of Inc.": "country_of_inc",
    "FTSE Industry": "ftse_industry_code",
    "FTSE Sector": "ftse_sector",
    "FTSE Subsector": "ftse_subsector",
    "Issue Price": "issue_price",
    "Currency": "currency",
    "Market Cap - Opening Price (£m)": "market_cap_gbp_m",
    "Nominated Advisor (AIM only)": "nomad",
    "Money Raised - New (£m)": "raised_new_gbp_m",
    "Money Raised - Existing (£m)": "raised_existing_gbp_m",
    "TOTAL RAISED (£m)": "raised_total_gbp_m",
}

NUMERIC = ["year", "issue_price", "market_cap_gbp_m",
           "raised_new_gbp_m", "raised_existing_gbp_m", "raised_total_gbp_m"]


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns=RENAME)[list(RENAME.values())]
    df = df.dropna(subset=["company", "market"])

    for col in NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")  # '-' and blanks -> NULL
    df["year"] = df["year"].astype("Int64")
    df["admission_date"] = pd.to_datetime(df["admission_date"]).dt.strftime("%Y-%m-%d")
    for col in ["company", "ftse_sector", "ftse_subsector", "issue_type", "market"]:
        df[col] = df[col].astype("string").str.strip()

    # Simpler market grouping for analysis
    df["market_group"] = df["market"].map({
        "AIM": "AIM",
        "UK Main Market": "Main Market",
        "International Main Market": "Main Market",
    }).fillna("Other (SFM/PSM)")
    df["is_ipo"] = (df["ipo_flag"] == "IPO").astype(int)
    return df


def main(xlsx_path: str, db_path: str) -> None:
    raw = pd.read_excel(xlsx_path, sheet_name=SHEET, header=HEADER_ROW)
    df = clean(raw)
    with sqlite3.connect(db_path) as con:
        df.to_sql("new_issues", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX IF NOT EXISTS ix_year ON new_issues(year)")
    print(f"Loaded {len(df):,} admissions ({df['year'].min()}-{df['year'].max()}) into {db_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
