"""Draw who controls each layer of the AI stack for three MGB systems.

Reads data/stack_map.csv and writes outputs/stack_control_map.png.
Usage:  python scripts/render_stack_map.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import textwrap

BASE = Path(__file__).resolve().parents[1]
COLOURS = {"MGB": "#2a9d8f", "Cloud": "#7aa6c2", "Vendor": "#e9a03b", "Upstream": "#b8b8b8"}
LABELS = {"MGB": "MGB controls", "Cloud": "Cloud provider (shared responsibility)",
          "Vendor": "Vendor controls", "Upstream": "Upstream, no evidence path"}
SYSTEMS = {"AI-001": "AI-001 SME credit model\n(built in-house)",
           "AI-003": "AI-003 Customer chatbot\n(bought)",
           "AI-008": "AI-008 KYC ID verification\n(bought)"}


def main():
    df = pd.read_csv(BASE / "data" / "stack_map.csv")
    layers = df.drop_duplicates("layer_no").sort_values("layer_no", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 7.2))
    for j, sid in enumerate(SYSTEMS):
        for _, r in df[df.system_id == sid].iterrows():
            y = 7 - r.layer_no
            ax.add_patch(plt.Rectangle((j + 0.04, y + 0.06), 0.92, 0.88, color=COLOURS[r.controller]))
            ax.text(j + 0.5, y + 0.5, "\n".join(textwrap.wrap(r.owner, 26)), ha="center", va="center",
                    fontsize=8.5, color="white" if r.controller != "Upstream" else "#333", weight="bold")
        ax.text(j + 0.5, -0.25, SYSTEMS[sid], ha="center", va="bottom", fontsize=10, weight="bold")
    for _, r in layers.iterrows():
        ax.text(-0.05, 7 - r.layer_no + 0.5, f"{r.layer_no}. {r.layer}", ha="right", va="center", fontsize=10)
    ax.set_xlim(-1.3, 3); ax.set_ylim(7, -1.0); ax.axis("off")
    ax.set_title("Who controls each layer of the stack? Buying a system hands most layers to someone else",
                 fontsize=12, pad=12)
    ax.legend(handles=[Patch(color=c, label=LABELS[k]) for k, c in COLOURS.items()],
              loc="upper center", bbox_to_anchor=(0.55, 0.0), ncol=4, frameon=False, fontsize=9)
    plt.tight_layout()
    plt.savefig(BASE / "outputs" / "stack_control_map.png", dpi=150, bbox_inches="tight")
    counts = df.groupby(["system_id", "controller"]).size().unstack(fill_value=0)
    print(counts)


if __name__ == "__main__":
    main()
