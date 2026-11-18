"""Train and review MGB's SME credit model (AI-001) - fictional, synthetic data.

Runs six governance checks that mirror the Week 2 reading:
  1. Leakage       - train with and without `referred_to_collections`
  2. Scorecard     - the learned weights of a logistic regression
  3. Honest test   - train on 2019-2023, test on 2024 (data the model never saw)
  4. Overfitting   - compare a deep decision tree's train vs test score
  5. Thresholds    - same model, two risk-appetite policies
  6. Accuracy trap - "never default" baseline vs the model; recall and precision
  7. Outcomes by group - `owner_group` is NOT an input, but are decisions different?

Writes everything to outputs/.
Usage:  python scripts/train_credit_model.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).resolve().parents[1]
DATA, OUT = BASE / "data" / "sme_loans_2019_2024.csv", BASE / "outputs"
NUMERIC = ["years_trading", "missed_payments_24m", "loan_to_profit_ratio", "collateral_pledged"]
CATEGORICAL = ["sector"]
LEAKY = ["referred_to_collections"]
LABEL = "default_12m"

# Risk-appetite policies: chosen by people, not learned
POLICIES = {
    "Current policy (approve <8%, refer 8-20%, decline >20%)": (0.08, 0.20),
    "Growth push (approve <20%, decline >20%)": (0.20, 0.20),
}


def pipeline(numeric, categorical, model):
    pre = ColumnTransformer([("num", StandardScaler(), numeric),
                             ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), categorical)])
    return make_pipeline(pre, model)


def decide(p, approve_below, decline_above):
    return np.where(p < approve_below, "approve", np.where(p > decline_above, "decline", "refer"))


def main():
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(DATA)
    train, test = df[df.origination_year <= 2023], df[df.origination_year == 2024]
    res = {"rows": {"train_2019_2023": len(train), "test_2024": len(test)},
           "default_rate_test": round(test[LABEL].mean(), 4)}

    # 1. Leakage
    leaky = pipeline(NUMERIC + LEAKY, CATEGORICAL, LogisticRegression(max_iter=1000)).fit(train, train[LABEL])
    res["leakage"] = {"auc_with_leaky_feature": round(roc_auc_score(test[LABEL], leaky.predict_proba(test)[:, 1]), 3)}

    # 2-3. Clean scorecard model, honest time-based test
    model = pipeline(NUMERIC, CATEGORICAL, LogisticRegression(max_iter=1000)).fit(train, train[LABEL])
    p_train, p_test = model.predict_proba(train)[:, 1], model.predict_proba(test)[:, 1]
    res["leakage"]["auc_without"] = round(roc_auc_score(test[LABEL], p_test), 3)
    res["logistic"] = {"auc_train": round(roc_auc_score(train[LABEL], p_train), 3),
                       "auc_test_2024": round(roc_auc_score(test[LABEL], p_test), 3)}

    # Scorecard on unscaled features so the weights are readable
    raw = make_pipeline(ColumnTransformer([("num", "passthrough", NUMERIC),
                                           ("cat", OneHotEncoder(drop="first"), CATEGORICAL)]),
                        LogisticRegression(max_iter=5000)).fit(train, train[LABEL])
    names = NUMERIC + [f"sector = {c}" for c in raw[0].named_transformers_["cat"].categories_[0][1:]]
    card = pd.DataFrame({"feature": ["(starting score / intercept)"] + names,
                         "learned_weight": np.r_[raw[-1].intercept_, raw[-1].coef_[0]].round(3)})
    card["effect"] = np.where(card.learned_weight > 0, "raises risk", "lowers risk")
    card.loc[0, "effect"] = "baseline"
    card.to_csv(OUT / "scorecard_weights.csv", index=False)

    # 4. Overfitting
    tree = pipeline(NUMERIC, CATEGORICAL, DecisionTreeClassifier(random_state=0)).fit(train, train[LABEL])
    res["deep_tree"] = {"auc_train": round(roc_auc_score(train[LABEL], tree.predict_proba(train)[:, 1]), 3),
                        "auc_test_2024": round(roc_auc_score(test[LABEL], tree.predict_proba(test)[:, 1]), 3)}

    # 5. Thresholds: same model, different decisions
    res["policies"] = {}
    for name, (lo, hi) in POLICIES.items():
        d = pd.Series(decide(p_test, lo, hi))
        res["policies"][name] = {k: int(v) for k, v in d.value_counts().reindex(["approve", "refer", "decline"], fill_value=0).items()}

    # 6. Accuracy trap (flag as "likely default" if p > 20%)
    y, flag = test[LABEL].values, (p_test > 0.20).astype(int)
    res["accuracy_trap"] = {
        "never_default_baseline": {"accuracy": round(accuracy_score(y, np.zeros_like(y)), 3), "recall": 0.0},
        "model_at_20pct": {"accuracy": round(accuracy_score(y, flag), 3),
                           "recall": round(recall_score(y, flag), 3),
                           "precision": round(precision_score(y, flag), 3)},
    }

    # 7. Outcomes by group (owner_group never used as an input)
    lo, hi = POLICIES["Current policy (approve <8%, refer 8-20%, decline >20%)"]
    g = test.assign(decision=decide(p_test, lo, hi), p=p_test)
    by = g.groupby("owner_group").agg(loans=("loan_id", "size"), actual_default_rate=(LABEL, "mean"),
                                      mean_predicted=("p", "mean"),
                                      approve_rate=("decision", lambda s: (s == "approve").mean()),
                                      collateral_rate=("collateral_pledged", "mean")).round(3)
    by.to_csv(OUT / "outcomes_by_group.csv")
    res["outcomes_by_group"] = by.to_dict(orient="index")
    res["impact_ratio_approval_B_vs_A"] = round(by.loc["B", "approve_rate"] / by.loc["A", "approve_rate"], 2)

    # Missing outcomes: Hospitality before 2022
    h = df[df.sector == "Hospitality"]
    res["missing_outcomes_hospitality"] = {"loans_2019_2021": int((h.origination_year < 2022).sum()),
                                           "loans_2022_2024": int((h.origination_year >= 2022).sum())}

    (OUT / "model_results.json").write_text(json.dumps(res, indent=2))
    charts(card, p_test, test, res)
    print(json.dumps(res, indent=2))


def charts(card, p_test, test, res):
    teal, amber, grey = "#2a9d8f", "#e76f51", "#8d99ae"
    # Scorecard weights
    c = card.iloc[1:].sort_values("learned_weight")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(c.feature, c.learned_weight, color=[amber if w > 0 else teal for w in c.learned_weight])
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("Learned weight (positive = raises default risk)")
    ax.set_title("What the SME credit model learned (synthetic data)")
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(OUT / "scorecard_weights.png", dpi=150); plt.close()

    # Probability distribution with the human-chosen thresholds
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bins = np.linspace(0, 0.6, 41)
    ax.hist(p_test[test[LABEL] == 0], bins=bins, alpha=0.75, color=teal, label="Repaid")
    ax.hist(p_test[test[LABEL] == 1], bins=bins, alpha=0.85, color=amber, label="Defaulted")
    for x, lbl in [(0.08, "8% approve line"), (0.20, "20% decline line")]:
        ax.axvline(x, color="#333", ls="--", lw=1)
        ax.text(x + 0.005, ax.get_ylim()[1] * 0.9, lbl, fontsize=9)
    ax.set_xlabel("Predicted probability of default (2024 loans, never seen in training)")
    ax.set_ylabel("Loans")
    ax.set_title("The model gives a probability. People choose where the lines go.")
    ax.legend(); ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout(); plt.savefig(OUT / "thresholds.png", dpi=150); plt.close()


if __name__ == "__main__":
    main()
