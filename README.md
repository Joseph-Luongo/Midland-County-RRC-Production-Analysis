# Permian Basin RRC Production Comparison

## Overview

This project extends my previous Midland County RRC Production Analysis into a five-county Permian Basin comparison using public Texas Railroad Commission production data.

**Counties analyzed:** Midland, Martin, Howard, Reeves, and Loving  
**Period:** January 2020 through March 2026  
**Well type:** Both

The analysis is intentionally focused on metrics that are useful for screening assets and operating areas: production scale and growth, product mix, gas intensity, operator concentration, field concentration, and near-term production momentum.

## Data Source

Texas Railroad Commission Production Data Query (PDQ):  
https://webapps2.rrc.texas.gov/EWA/ewaPdqMain.do

Five RRC report types are retained for each county:

- District
- Field
- Lease
- Monthly Totals
- Operator

## Key Findings

- **Martin County is the strongest growth county in the five-county set.** Oil production increased **76.8%** from 2020 to 2025 and gas production increased **155.1%**.
- **Reeves County was the largest 2025 gas producer** at approximately **1,218.9 Bcf**.
- **Condensate materially changes the Delaware Basin comparison.** Condensate represented **54.4% of Reeves liquids** and **35.9% of Loving liquids** in 2025. Oil-only comparisons therefore understate liquids scale in those counties.
- **Howard County shows the largest shift toward gas.** Oil production was nearly flat from 2020 to 2025 while gas production increased **127.3%**. Its gas-to-liquids ratio increased from **1.93 to 4.32 MCF/BBL**.
- **Reported operator concentration varies materially.** The top five reported operators account for approximately **77.9%** of cumulative oil in Loving, compared with **47.6%** in Reeves.
- **Q1 2026 oil run rates are below the 2025 monthly average in all five counties.** Martin and Loving are the most stable; Howard shows the largest decline.

## Why Total Liquids and GLR Are Included

Part 1 focused primarily on oil, gas, and GOR. For a cross-county comparison, condensate becomes important because it is a large portion of the liquids stream in Reeves and Loving.

This project therefore adds:

- **Total Liquids = Oil + Condensate**
- **GLR = Gas (MCF) / Total Liquids (BBL)**

GLR provides a more comparable measure of gas intensity when condensate production differs substantially across counties.

## Core Figures

### Production Growth

![Production Growth](Figures/04_Production_Growth_2020_2025.png)

### 2025 Liquids Composition

![Liquids Composition](Figures/05_2025_Liquids_Composition.png)

### Gas-to-Liquids Ratio

![GLR](Figures/03_Gas_to_Liquids_Ratio.png)

## Repository Structure

```text
Permian_Basin_RRC_Production_Comparison/
├── Data/
│   ├── Data_Raw/          # Original RRC CSV exports
│   └── Data_Cleaned/      # Combined tables, metrics, and Excel workbook
├── Figures/               # Final analysis figures
├── Notebook/
│   ├── Permian_Basin_Production_Analysis.py
│   └── Permian_Basin_Production_Analysis.ipynb
├── PowerPoint/            # Final presentation
├── Report/                # Technical report DOCX and PDF
├── README.md
└── requirements.txt
```

## Python Analysis

The Python pipeline standardizes the RRC exports, combines all five counties, calculates annual and monthly metrics, ranks operators and fields, and generates the final figures.

Run from the project root:

```bash
python Notebook/Permian_Basin_Production_Analysis.py
```

The script produces:

- `Combined_Monthly_Production.csv`
- `County_Annual_Production.csv`
- `County_Key_Metrics.csv`
- `Top_Operators_by_County.csv`
- `Top_Fields_by_County.csv`
- Six final figures

The Jupyter notebook provides a more interactive version of the same workflow and has been executed successfully in the project package.

## Excel Workbook

`Data/Data_Cleaned/Permian_Basin_RRC_Analysis.xlsx` includes:

- Executive dashboard
- Formula-driven county metrics
- Annual production data
- Monthly production data
- Top-operator summaries
- Top-field summaries
- Methodology and source notes

## Business-Relevant Interpretation

The county comparison highlights several different operating profiles:

- **Martin:** strongest growth and the clearest candidate for deeper well-level productivity and decline analysis.
- **Midland:** large, established oil scale with strong gas growth.
- **Howard:** increasingly gas-intensive despite limited oil growth.
- **Reeves:** highest gas production, high condensate contribution, and a relatively fragmented reported operator base.
- **Loving:** meaningful oil and condensate scale with a relatively concentrated reported operator base.

## Important Limitation

This is a **public-data screening analysis**, not a reserve report or economic evaluation. It does not include well-level decline curves, acreage quality, drilling/completion costs, operating costs, realized pricing, NGL yields, midstream constraints, or current ownership mapping.

RRC operator reports aggregate production across the full query period. Historical operator names can remain after acquisitions or asset transfers, so operator rankings should be interpreted as **reported production concentration over the query period**, not current acreage ownership.

## Tools Used

- Texas Railroad Commission public production data
- Python
- pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- Microsoft Excel
- Microsoft PowerPoint
- LLMs
