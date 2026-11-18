"""Add Week 3 model classification to the MGB AI inventory and find explanation gaps.

- Merges output_type, algorithm_family, explainability and fact_sheet into 00-inventory/inventory.csv
  (safe to re-run: existing values for these columns are overwritten from the classification file).
- An "explanation gap" is a system that recommends or decides about people
  while its explainability is low or unknown.
- Writes outputs/explainability_matrix.csv, outputs/explainability_summary.md
  and outputs/explainability_vs_impact.png.

Usage:  python scripts/classify_inventory.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
INVENTORY = ROOT / "00-inventory" / "inventory.csv"
CLASSES = BASE / "data" / "model_classification.csv"
OUT = BASE / "outputs"

FACT_SHEETS = {
    "AI-001": "part1-what-we-govern/m03-models-and-stack/fact-sheets/AI-001-sme-credit-model.md",
    "AI-003": "part1-what-we-govern/m03-models-and-stack/fact-sheets/AI-003-customer-chatbot.md",
    "AI-008": "part1-what-we-govern/m03-models-and-stack/fact-sheets/AI-008-kyc-id-verification.md",
}
NEW_COLS = ["output_type", "algorithm_family", "explainability", "fact_sheet"]
PEOPLE = {"customers", "applicants", "candidates", "employees"}


def main():
    OUT.mkdir(exist_ok=True)
    inv = pd.read_csv(INVENTORY, dtype=str).fillna("")
    cls = pd.read_csv(CLASSES, dtype=str).fillna("")
    inv = inv.drop(columns=[c for c in NEW_COLS if c in inv.columns])
    inv = inv.merge(cls.drop(columns="basis"), on="system_id", how="left")
    inv["fact_sheet"] = inv.system_id.map(FACT_SHEETS).fillna("")
    missing = inv[inv.output_type.isna() | (inv.output_type == "")].system_id.tolist()
    if missing:
        raise SystemExit(f"No classification for: {missing}")
    inv.to_csv(INVENTORY, index=False)

    affects_people = inv.affected_parties.apply(lambda s: bool(set(s.split(";")) & PEOPLE))
    inv["explanation_gap"] = (inv.decision_impact.isin(["recommends", "decides"])
                              & affects_people
                              & inv.explainability.isin(["low", "unknown"]))
    cols = ["system_id", "system_name", "output_type", "algorithm_family", "explainability",
            "decision_impact", "affected_parties", "approval_status", "explanation_gap"]
    matrix = inv[cols].sort_values(["explanation_gap", "system_id"], ascending=[False, True])
    matrix.to_csv(OUT / "explainability_matrix.csv", index=False)

    gaps = matrix[matrix.explanation_gap]
    lines = [
        "# Explainability summary (Week 3)",
        "",
        f"- Systems classified: **{len(inv)}**",
        f"- By output type: " + ", ".join(f"{k} {v}" for k, v in inv.output_type.value_counts().items()),
        f"- By explainability: " + ", ".join(f"{k} {v}" for k, v in inv.explainability.value_counts().items()),
        f"- Algorithm family not disclosed by vendor: **{(inv.algorithm_family == 'not_disclosed').sum()}**",
        f"- **Explanation gaps** (recommends or decides about people, explainability low or unknown): **{len(gaps)}**",
        "",
        "| ID | System | Output | Explainability | Decision impact | Affected |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for _, r in gaps.iterrows():
        lines.append(f"| {r.system_id} | {r.system_name} | {r.output_type} | {r.explainability} | "
                     f"{r.decision_impact} | {r.affected_parties.replace(';', ', ')} |")
    (OUT / "explainability_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    chart(inv)
    print("\n".join(lines))


def chart(inv):
    x_order = ["informs", "recommends", "decides"]
    y_order = ["high", "medium", "low", "unknown"]
    fig, ax = plt.subplots(figsize=(9, 5.6))
    ax.add_patch(plt.Rectangle((0.5, 1.5), 2, 2, color="#e76f51", alpha=0.10, zorder=0))
    ax.text(2.45, 1.58, "Explanation gap zone", ha="right", va="top", fontsize=9, color="#b5442a")
    for (x, y), cell in inv.groupby([inv.decision_impact.map(x_order.index),
                                     inv.explainability.map(y_order.index)]):
        n, per_row = len(cell), 6
        for k, (_, r) in enumerate(cell.iterrows()):
            row, col = divmod(k, per_row)
            in_row = min(per_row, n - row * per_row)
            px = x + (col - (in_row - 1) / 2) * 0.15
            py = y + (row - (-(-n // per_row) - 1) / 2) * 0.22
            colour = "#2a9d8f" if r.approval_status == "approved" else "#e9a03b"
            ax.scatter(px, py, s=230, color=colour, edgecolor="white", zorder=3)
            ax.text(px, py, r.system_id.split("-")[1].lstrip("0"), ha="center", va="center",
                    fontsize=7, color="white", weight="bold", zorder=4)
    for v in (0.5, 1.5):
        ax.axvline(v, color="#ddd", lw=0.8, zorder=1)
    for v in (0.5, 1.5, 2.5):
        ax.axhline(v, color="#ddd", lw=0.8, zorder=1)
    ax.set_xticks(range(3), ["Informs", "Recommends", "Decides"])
    ax.set_yticks(range(4), ["High", "Medium", "Low", "Unknown"])
    ax.tick_params(length=0)
    ax.set_xlim(-0.5, 2.5); ax.set_ylim(3.5, -0.5)
    ax.set_xlabel("How close the output is to a decision")
    ax.set_ylabel("How explainable the model is")
    ax.set_title("MGB AI estate: explainability vs decision impact (numbers = AI-0xx)")
    ax.scatter([], [], color="#2a9d8f", label="Approved"); ax.scatter([], [], color="#e9a03b", label="Unapproved")
    ax.legend(loc="upper right", frameon=False)
    for side in ax.spines.values():
        side.set_visible(False)
    plt.tight_layout(); plt.savefig(OUT / "explainability_vs_impact.png", dpi=150); plt.close()


if __name__ == "__main__":
    main()
