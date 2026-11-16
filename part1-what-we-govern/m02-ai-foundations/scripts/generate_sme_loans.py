"""Generate a synthetic SME loan book for Meridian Gulf Bank (fictional), 2019-2024.

The data is built with four deliberate governance problems for the review to find:
  1. Leakage: `referred_to_collections` is only set AFTER a default.
  2. Missing outcomes: Hospitality was mostly declined before 2022, so few repaid/defaulted examples exist.
  3. Proxy pattern: `owner_group` (a stand-in for a protected characteristic) is NOT a model input,
     but it correlates with `district` and with access to collateral.
  4. Label definition: default is defined as 90+ days past due within 12 months.

All data is synthetic. Same seed = same file.
Usage:  python scripts/generate_sme_loans.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2026
OUT = Path(__file__).resolve().parents[1] / "data" / "sme_loans_2019_2024.csv"
SECTORS = ["Trading", "Construction", "Professional services", "Retail", "Hospitality", "Logistics"]
SECTOR_RISK = {"Trading": 0.0, "Construction": 0.45, "Professional services": -0.35,
               "Retail": 0.2, "Hospitality": 0.35, "Logistics": 0.05}
DISTRICTS = ["North", "Central", "West", "Industrial"]


def generate(n=18_000, seed=SEED):
    rng = np.random.default_rng(seed)
    year = rng.choice(np.arange(2019, 2025), size=n, p=[0.13, 0.14, 0.16, 0.18, 0.19, 0.20])
    owner_group = rng.choice(["A", "B"], size=n, p=[0.7, 0.3])

    # District correlates with owner_group (the proxy route)
    district = np.where(owner_group == "A",
                        rng.choice(DISTRICTS, size=n, p=[0.35, 0.35, 0.2, 0.1]),
                        rng.choice(DISTRICTS, size=n, p=[0.1, 0.15, 0.3, 0.45]))

    # Hospitality mostly declined before 2022 -> few booked loans (missing outcomes)
    sector = rng.choice(SECTORS, size=n, p=[0.24, 0.18, 0.2, 0.18, 0.08, 0.12])
    early_hosp = (sector == "Hospitality") & (year < 2022)
    drop = early_hosp & (rng.random(n) < 0.85)

    years_trading = np.clip(rng.gamma(2.2, 3.2, n), 0.5, 40).round(1)
    missed_payments_24m = rng.poisson(0.55, n)
    loan_amount_qar = (np.exp(rng.normal(13.1, 0.7, n)) // 1000 * 1000).astype(int)
    loan_to_profit = np.clip(rng.lognormal(0.6, 0.6, n), 0.2, 12).round(2)
    # Structural gap: group B pledges collateral less often
    collateral = (rng.random(n) < np.where(owner_group == "A", 0.62, 0.38)).astype(int)

    logit = (-3.25 + 0.85 * missed_payments_24m + 0.32 * np.log1p(loan_to_profit) * 3
             - 0.09 * years_trading - 0.75 * collateral
             + np.vectorize(SECTOR_RISK.get)(sector)
             + rng.normal(0, 0.35, n))
    p = 1 / (1 + np.exp(-logit))
    default_12m = (rng.random(n) < p).astype(int)

    # Leakage: set after the outcome is known
    referred = np.where(default_12m == 1, rng.random(n) < 0.94, rng.random(n) < 0.01).astype(int)

    df = pd.DataFrame({
        "loan_id": [f"L{100000 + i}" for i in range(n)],
        "origination_year": year,
        "sector": sector,
        "district": district,
        "years_trading": years_trading,
        "missed_payments_24m": missed_payments_24m,
        "loan_amount_qar": loan_amount_qar,
        "loan_to_profit_ratio": loan_to_profit,
        "collateral_pledged": collateral,
        "referred_to_collections": referred,
        "owner_group": owner_group,
        "default_12m": default_12m,
    })
    return df[~drop].reset_index(drop=True)


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    df = generate()
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} loans to {OUT} | default rate {df.default_12m.mean():.1%}")
