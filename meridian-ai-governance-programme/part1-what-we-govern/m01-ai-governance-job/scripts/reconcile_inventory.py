"""Add unapproved AI tools found by the shadow-AI scan to the AI inventory.

- New tools get the next AI-0xx id, approval_status=unapproved and the fields the scan can fill.
- Tools already in the inventory (matched on system_name) are skipped, so the script is safe to re-run.
- Approved tools seen in the scan have the scan source appended to discovered_via.

Usage:  python scripts/reconcile_inventory.py
"""
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
INVENTORY = ROOT / "00-inventory" / "inventory.csv"
FINDINGS = Path(__file__).resolve().parents[1] / "outputs" / "shadow_ai_findings.csv"


def next_id(ids):
    nums = [int(i.split("-")[1]) for i in ids if str(i).startswith("AI-")]
    n = max(nums, default=0) + 1
    while True:
        yield f"AI-{n:03d}"
        n += 1


def main():
    inv = pd.read_csv(INVENTORY, dtype=str).fillna("")
    found = pd.read_csv(FINDINGS, dtype=str).fillna("")
    ids = next_id(inv.system_id)
    added, today = [], date.today().isoformat()

    for _, f in found.iterrows():
        if f.register_id:  # approved tool: record that the scan also saw it
            mask = inv.system_id == f.register_id
            for src in f.discovered_via.split("+"):
                if src not in inv.loc[mask, "discovered_via"].iloc[0]:
                    inv.loc[mask, "discovered_via"] += f";{src}"
            continue
        if f.tool in set(inv.system_name):
            continue
        row = {c: "" for c in inv.columns}
        row.update({
            "system_id": next(ids),
            "system_name": f.tool,
            "description": f"Unapproved {f.category.replace('_', ' ')} found by shadow-AI scan",
            "business_unit": f.departments.replace(", ", ";"),
            "business_owner": "TO ASSIGN",
            "technical_owner": f.vendor,
            "lifecycle_status": "production",
            "approval_status": "unapproved",
            "source": "bought",
            "vendor": f.vendor,
            "upstream_model": "unknown",
            "ai_type": f.ai_type,
            "value_chain_role": "deployer",
            "personal_data": "to_confirm",
            "jurisdictions": "QA",
            "discovered_via": f.discovered_via.replace("+", ";"),
            "last_reviewed": today,
        })
        inv = pd.concat([inv, pd.DataFrame([row])], ignore_index=True)
        added.append(row["system_id"] + " " + f.tool)

    inv.to_csv(INVENTORY, index=False)
    print(f"Inventory now has {len(inv)} systems. Added {len(added)}:")
    print("\n".join(f"  {a}" for a in added) or "  (none)")


if __name__ == "__main__":
    main()
