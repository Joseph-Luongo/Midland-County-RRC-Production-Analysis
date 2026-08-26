"""Permian Basin multi-county production comparison.

Source: Texas Railroad Commission Production Data Query (PDQ)
Counties: Midland, Martin, Howard, Reeves, Loving
Period: January 2020 through March 2026
Well type: Both

The script standardizes RRC CSV exports, builds county-level production and
concentration metrics, and saves the core figures used in the report/deck.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "Data" / "Data_Raw"
CLEAN_DIR = ROOT / "Data" / "Data_Cleaned"
FIG_DIR = ROOT / "Figures"

COUNTIES = ["Midland", "Martin", "Howard", "Reeves", "Loving"]
REPORT_TYPES = ["Monthly", "Operator", "Field", "Lease", "District"]

CLEAN_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def read_rrc_csv(path: Path) -> pd.DataFrame:
    """Read an RRC PDQ CSV export, skipping the seven metadata lines."""
    return pd.read_csv(path, skiprows=7)


def clean_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce standard RRC production columns to numeric values."""
    out = df.copy()
    numeric_cols = [
        "Oil (BBL)",
        "Casinghead (MCF)",
        "GW Gas (MCF)",
        "Condensate (BBL)",
    ]
    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    if {"Casinghead (MCF)", "GW Gas (MCF)"}.issubset(out.columns):
        out["Gas (MCF)"] = out["Casinghead (MCF)"] + out["GW Gas (MCF)"]
    return out


def load_monthly(county: str) -> pd.DataFrame:
    """Load and standardize monthly county production."""
    df = read_rrc_csv(RAW_DIR / f"{county}_Monthly.csv")
    df = df[df["Date"].astype(str).str.strip().str.lower() != "total"].copy()
    df = clean_numeric(df)
    df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(), format="%b %Y")
    df["County"] = county
    df["Year"] = df["Date"].dt.year
    df["Liquids (BBL)"] = df["Oil (BBL)"] + df["Condensate (BBL)"]
    df["GOR (MCF/BBL Oil)"] = np.where(
        df["Oil (BBL)"] > 0,
        df["Gas (MCF)"] / df["Oil (BBL)"],
        np.nan,
    )
    df["GLR (MCF/BBL Liquids)"] = np.where(
        df["Liquids (BBL)"] > 0,
        df["Gas (MCF)"] / df["Liquids (BBL)"],
        np.nan,
    )
    return df


def load_ranked_report(county: str, report_type: str) -> pd.DataFrame:
    """Load operator/field/lease/district report and remove the Total row."""
    df = read_rrc_csv(RAW_DIR / f"{county}_{report_type}.csv")
    first_col = df.columns[0]
    df = df[df[first_col].astype(str).str.strip().str.lower() != "total"].copy()
    df = clean_numeric(df)
    df["County"] = county
    if "Oil (BBL)" in df.columns:
        df["Liquids (BBL)"] = df["Oil (BBL)"] + df.get("Condensate (BBL)", 0)
    return df


def build_annual(monthly: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "Oil (BBL)",
        "Casinghead (MCF)",
        "GW Gas (MCF)",
        "Gas (MCF)",
        "Condensate (BBL)",
        "Liquids (BBL)",
    ]
    annual = monthly.groupby(["County", "Year"], as_index=False)[cols].sum()
    annual["GOR (MCF/BBL Oil)"] = annual["Gas (MCF)"] / annual["Oil (BBL)"]
    annual["GLR (MCF/BBL Liquids)"] = annual["Gas (MCF)"] / annual["Liquids (BBL)"]
    return annual


def build_metrics(
    monthly: pd.DataFrame,
    annual: pd.DataFrame,
    operators: pd.DataFrame,
    fields: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    for county in COUNTIES:
        a = annual[annual["County"] == county].set_index("Year")
        m = monthly[monthly["County"] == county]
        op = operators[operators["County"] == county].sort_values("Oil (BBL)", ascending=False)
        fld = fields[fields["County"] == county].sort_values("Oil (BBL)", ascending=False)

        oil20 = a.loc[2020, "Oil (BBL)"]
        oil25 = a.loc[2025, "Oil (BBL)"]
        gas20 = a.loc[2020, "Gas (MCF)"]
        gas25 = a.loc[2025, "Gas (MCF)"]
        liq20 = a.loc[2020, "Liquids (BBL)"]
        liq25 = a.loc[2025, "Liquids (BBL)"]
        cond25 = a.loc[2025, "Condensate (BBL)"]

        avg25 = m[m["Year"] == 2025][["Oil (BBL)", "Gas (MCF)", "Liquids (BBL)"]].mean()
        avg26 = m[m["Year"] == 2026][["Oil (BBL)", "Gas (MCF)", "Liquids (BBL)"]].mean()

        op_total = op["Oil (BBL)"].sum()
        fld_total = fld["Oil (BBL)"].sum()

        rows.append(
            {
                "County": county,
                "2025 Oil (MMbbl)": oil25 / 1e6,
                "2020-2025 Oil Growth (%)": (oil25 / oil20 - 1) * 100,
                "2020-2025 Oil CAGR (%)": ((oil25 / oil20) ** (1 / 5) - 1) * 100,
                "2025 Gas (Bcf)": gas25 / 1e6,
                "2020-2025 Gas Growth (%)": (gas25 / gas20 - 1) * 100,
                "2020-2025 Gas CAGR (%)": ((gas25 / gas20) ** (1 / 5) - 1) * 100,
                "2025 Condensate (MMbbl)": cond25 / 1e6,
                "2025 Total Liquids (MMbbl)": liq25 / 1e6,
                "2025 Condensate Share of Liquids (%)": cond25 / liq25 * 100,
                "2020 GLR (MCF/BBL Liquids)": gas20 / liq20,
                "2025 GLR (MCF/BBL Liquids)": gas25 / liq25,
                "2020-2025 GLR Change (%)": ((gas25 / liq25) / (gas20 / liq20) - 1) * 100,
                "2026 Q1 Oil Momentum vs 2025 Avg (%)": (avg26["Oil (BBL)"] / avg25["Oil (BBL)"] - 1) * 100,
                "2026 Q1 Gas Momentum vs 2025 Avg (%)": (avg26["Gas (MCF)"] / avg25["Gas (MCF)"] - 1) * 100,
                "Top Oil Operator (2020-Mar 2026)": op.iloc[0]["Operator Name"],
                "Top Operator Oil Share (%)": op.iloc[0]["Oil (BBL)"] / op_total * 100,
                "Top 5 Operator Oil Share (%)": op.head(5)["Oil (BBL)"].sum() / op_total * 100,
                "Top Oil Field (2020-Mar 2026)": fld.iloc[0]["Field Name"],
                "Top Field Oil Share (%)": fld.iloc[0]["Oil (BBL)"] / fld_total * 100,
            }
        )
    return pd.DataFrame(rows)


def top_n_with_share(df: pd.DataFrame, name_col: str, n: int) -> pd.DataFrame:
    rows = []
    for county in COUNTIES:
        part = df[df["County"] == county].sort_values("Oil (BBL)", ascending=False).copy()
        total = part["Oil (BBL)"].sum()
        top = part.head(n).copy()
        top["Oil Share (%)"] = np.where(total > 0, top["Oil (BBL)"] / total * 100, np.nan)
        top["Rank"] = np.arange(1, len(top) + 1)
        keep = ["County", "Rank", name_col, "Oil (BBL)", "Gas (MCF)", "Condensate (BBL)", "Oil Share (%)"]
        rows.append(top[keep])
    return pd.concat(rows, ignore_index=True)


def save_figures(annual: pd.DataFrame, metrics: pd.DataFrame) -> None:
    trend = annual[annual["Year"].between(2020, 2025)].copy()

    # 1 - annual oil trend
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for county in COUNTIES:
        p = trend[trend["County"] == county]
        ax.plot(p["Year"], p["Oil (BBL)"] / 1e6, marker="o", label=county)
    ax.set_title("Annual Oil Production by County")
    ax.set_xlabel("Year")
    ax.set_ylabel("Oil Production (MMbbl)")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_Annual_Oil_Production.png", dpi=200)
    plt.close(fig)

    # 2 - annual gas trend
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for county in COUNTIES:
        p = trend[trend["County"] == county]
        ax.plot(p["Year"], p["Gas (MCF)"] / 1e6, marker="o", label=county)
    ax.set_title("Annual Gas Production by County")
    ax.set_xlabel("Year")
    ax.set_ylabel("Gas Production (Bcf)")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_Annual_Gas_Production.png", dpi=200)
    plt.close(fig)

    # 3 - gas-to-liquids ratio trend
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for county in COUNTIES:
        p = trend[trend["County"] == county]
        ax.plot(p["Year"], p["GLR (MCF/BBL Liquids)"], marker="o", label=county)
    ax.set_title("Gas-to-Liquids Ratio by County")
    ax.set_xlabel("Year")
    ax.set_ylabel("MCF Gas per BBL Total Liquids")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_Gas_to_Liquids_Ratio.png", dpi=200)
    plt.close(fig)

    # 4 - growth comparison
    plot = metrics.set_index("County").loc[COUNTIES]
    x = np.arange(len(COUNTIES))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.bar(x - width / 2, plot["2020-2025 Oil Growth (%)"], width, label="Oil")
    ax.bar(x + width / 2, plot["2020-2025 Gas Growth (%)"], width, label="Gas")
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Production Growth: 2020 to 2025")
    ax.set_xlabel("County")
    ax.set_ylabel("Growth (%)")
    ax.set_xticks(x, COUNTIES)
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_Production_Growth_2020_2025.png", dpi=200)
    plt.close(fig)

    # 5 - liquids composition
    fig, ax = plt.subplots(figsize=(9, 5.2))
    oil = plot["2025 Oil (MMbbl)"].to_numpy()
    cond = plot["2025 Condensate (MMbbl)"].to_numpy()
    ax.bar(COUNTIES, oil, label="Oil")
    ax.bar(COUNTIES, cond, bottom=oil, label="Condensate")
    ax.set_title("2025 Liquids Production and Product Mix")
    ax.set_xlabel("County")
    ax.set_ylabel("Liquids Production (MMbbl)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "05_2025_Liquids_Composition.png", dpi=200)
    plt.close(fig)

    # 6 - operator concentration
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.bar(COUNTIES, plot["Top 5 Operator Oil Share (%)"])
    ax.set_title("Cumulative Oil Concentration: Top Five Reported Operators")
    ax.set_xlabel("County")
    ax.set_ylabel("Share of 2020-Mar 2026 Oil Production (%)")
    ax.set_ylim(0, 100)
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "06_Top5_Operator_Concentration.png", dpi=200)
    plt.close(fig)


def main() -> None:
    monthly = pd.concat([load_monthly(c) for c in COUNTIES], ignore_index=True)
    annual = build_annual(monthly)
    operators = pd.concat([load_ranked_report(c, "Operator") for c in COUNTIES], ignore_index=True)
    fields = pd.concat([load_ranked_report(c, "Field") for c in COUNTIES], ignore_index=True)

    metrics = build_metrics(monthly, annual, operators, fields)
    top_ops = top_n_with_share(operators, "Operator Name", 10)
    top_fields = top_n_with_share(fields, "Field Name", 5)

    monthly.to_csv(CLEAN_DIR / "Combined_Monthly_Production.csv", index=False)
    annual.to_csv(CLEAN_DIR / "County_Annual_Production.csv", index=False)
    metrics.to_csv(CLEAN_DIR / "County_Key_Metrics.csv", index=False)
    top_ops.to_csv(CLEAN_DIR / "Top_Operators_by_County.csv", index=False)
    top_fields.to_csv(CLEAN_DIR / "Top_Fields_by_County.csv", index=False)

    save_figures(annual, metrics)

    print("Analysis complete.")
    print(metrics.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
