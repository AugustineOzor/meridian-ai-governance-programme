# Model Review: SME Credit Model (AI-001)

**Reviewer:** AI Governance (second line) · **Model owner:** Head of SME Credit Risk · **Builder:** Head of Data Science · **Version:** 1.0 · **Date:** 2026-11-16

**Scope:** the ten governance questions from the Week 2 reading, applied to the model trained in `scripts/train_credit_model.py` on `data/sme_loans_2019_2024.csv` (17,463 synthetic loans). Each answer states the evidence, the finding and a rating.

**Rating key:** 🟢 adequate · 🟡 needs action · 🔴 must fix before use

## Summary

| # | Question | Rating | Headline |
| --- | --- | --- | --- |
| 1 | Label definition | 🟡 | Defined (90+ DPD in 12 months) but not confirmed consistent across source systems |
| 2 | Training period | 🟢 | 2019–2023 train, 2024 held out; includes the 2020–21 stress period |
| 3 | Missing outcomes | 🟡 | Only 86 hospitality loans before 2022 because most were declined |
| 4 | Feature approval | 🟡 | Five features used; no record of who approved each |
| 5 | Proxies | 🔴 | Group B approved at 0.91× the rate of group A while defaulting slightly less |
| 6 | Available at decision time | 🔴 → 🟢 | Leaky field found (AUC 0.99) and removed |
| 7 | Honest test | 🟢 | Scored on 2024 loans never seen in training |
| 8 | Train/test gap | 🟢 | Logistic model healthy; deep tree overfits badly and was rejected |
| 9 | Beyond accuracy | 🟡 | Recall 36%, precision 34% at the 20% line; cost of errors not yet documented |
| 10 | Threshold ownership | 🟡 | Thresholds exist; no recorded owner or rationale |

**Overall:** not ready for wider use. Two items (5, 9) need action before extension to the Dublin branch; item 6 is resolved.

## Detailed findings

### 1. What exactly is the label?
**Evidence:** `default_12m` = 90+ days past due within 12 months of origination.
**Finding:** the definition is reasonable and matches common credit practice. The review could not confirm that both source systems (core banking and the legacy SME platform) apply 90 days the same way.
**Action:** Head of Data Science to confirm label derivation per source system. 🟡

### 2. Which years, and why?
**Evidence:** training 2019–2023 (13,880 loans), testing 2024 (3,583 loans).
**Finding:** the window covers a stress period and recent conditions. 🟢

### 3. Whose outcomes are missing?
**Evidence:** hospitality has 86 booked loans in 2019–2021 against 827 in 2022–2024. Declined applications have no outcomes at all.
**Finding:** the model's view of hospitality, and of any group MGB historically declined, reflects MGB's past lending choices rather than true risk (reject inference problem). Its learned hospitality weight is lower risk than construction, which may simply reflect that only the strongest hospitality applicants were approved.
**Action:** document reject-inference approach; monitor hospitality defaults quarterly. 🟡

### 4. Which features, and who approved each?
**Evidence:** `years_trading`, `missed_payments_24m`, `loan_to_profit_ratio`, `collateral_pledged`, `sector`. `district` and `owner_group` were excluded.
**Finding:** sensible feature set, but there is no record of who approved each feature or why `district` was excluded.
**Action:** record approvals in the learned-vs-chosen register. 🟡

### 5. Which features correlate with protected characteristics?
**Evidence (2024 test loans, current policy):**

| Owner group | Loans | Actual default rate | Mean predicted risk | Approval rate | Collateral pledged |
| --- | --- | --- | --- | --- | --- |
| A | 2,551 | 9.1% | 8.7% | 64.3% | 61.5% |
| B | 1,032 | 8.6% | 9.5% | 58.4% | 39.6% |

**Finding:** owner group is not an input, yet group B is predicted *riskier* and approved *less* often while actually defaulting slightly *less*. Approval impact ratio B/A = **0.91**. The likely route is collateral, which group B pledges far less often. Collateral is a legitimate credit factor, so this is not automatically unlawful, but it must be justified and its effect measured. Removing a protected field does not remove its effect.
**Action:** full fairness review in Week 6; test alternatives such as weighting cash flow over collateral. 🔴

### 6. Would every feature be available at decision time?
**Evidence:** `referred_to_collections` was in the extract. With it, test AUC = **0.989**; without it, **0.787**.
**Finding:** classic leakage. The field is only set after a default, so the near-perfect score was an illusion that would have collapsed in live use. Removed from the feature set. 🔴 → 🟢

### 7. Were scores measured on unseen data?
**Evidence:** time-based split; the model never saw 2024 loans during training.
**Finding:** this mimics real use (predicting the future). 🟢

### 8. How big is the train/test gap?

| Model | Train AUC | Test AUC (2024) | Verdict |
| --- | --- | --- | --- |
| Logistic regression (scorecard) | 0.747 | 0.787 | Healthy: similar scores |
| Deep decision tree | 1.000 | 0.540 | Overfit: memorised training data |

**Finding:** the scorecard generalises; the tree is near a coin toss on new data and was rejected. The small test-above-train gap is within normal year-to-year variation. 🟢

### 9. Beyond accuracy
**Evidence (2024, default rate 9.0%):**

| Approach | Accuracy | Recall (defaults caught) | Precision (flags that were real) |
| --- | --- | --- | --- |
| Predict "no default" for everyone | 91.0% | 0% | n/a |
| Model, flag above 20% | 87.9% | 36.1% | 33.6% |

**Finding:** the useless baseline beats the model on accuracy, which proves accuracy is the wrong measure here. At the 20% line the model catches about a third of defaults, and two in three flagged applicants would have repaid. The relative cost of a missed default versus a wrongly declined business is not documented.
**Action:** Credit Risk to document error costs and justify the thresholds against them. 🟡

### 10. Who chose the thresholds?
**Evidence:** current policy approve <8%, refer 8–20%, decline >20%.
**Finding:** applying a growth policy (approve <20%) to the same model moves 995 applications from underwriter review to automatic approval. There is no recorded owner, date or rationale for the current lines.
**Action:** Credit Committee to own and minute the thresholds; review annually. 🟡

## What this review cannot establish

- **Real-world validity:** the data is synthetic, built to illustrate review techniques.
- **Causation for item 5:** the analysis shows correlation through collateral; it does not prove why group B pledges less collateral.
- **Performance by sub-segment** (sector × group, new-to-bank businesses), which needs larger samples.
- **Live behaviour:** drift after deployment is a Week 7 topic.
