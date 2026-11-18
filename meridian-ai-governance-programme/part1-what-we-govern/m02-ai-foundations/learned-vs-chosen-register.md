# Learned vs Chosen Register: SME Credit Model (AI-001)

**Purpose:** record every design decision made by people, with an owner and a rationale. The model's weights are learned; everything below was chosen, so everything below must be owned.

**Version:** 1.0 · **Date:** 2026-11-16 · **Review cycle:** annually, and at every retraining

| # | Decision (chosen) | Current choice | Rationale | Owner (role) | Approved | Next review |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | Label definition | 90+ days past due within 12 months | Aligns with internal default definition used in provisioning | Head of SME Credit Risk | Pending | 2027-11 |
| C2 | Training data window | Loans originated 2019–2023 | Covers a stress period and recent conditions | Head of Data Science | Pending | At each retrain |
| C3 | Test approach | Time-based: hold out 2024 | Mimics live use on future applicants | Head of Data Science | Pending | At each retrain |
| C4 | Feature: years trading | Included | Established stability indicator | Head of SME Credit Risk | Pending | 2027-11 |
| C5 | Feature: missed payments (24m) | Included | Strongest repayment-behaviour signal | Head of SME Credit Risk | Pending | 2027-11 |
| C6 | Feature: loan-to-profit ratio | Included | Affordability | Head of SME Credit Risk | Pending | 2027-11 |
| C7 | Feature: collateral pledged | Included, **under review** | Loss mitigant, but drives unequal outcomes by owner group (review item 5) | Head of SME Credit Risk | Pending fairness review | Week 6 |
| C8 | Feature: sector | Included | Sector risk differs materially | Head of SME Credit Risk | Pending | 2027-11 |
| C9 | Feature: district | **Excluded** | Correlates with owner group; proxy risk with no clear credit rationale | Head of AI Governance | Pending | 2027-11 |
| C10 | Feature: referred to collections | **Excluded** | Leakage: only set after default | Head of Data Science | 2026-11-16 | n/a |
| C11 | Model type | Logistic regression (scorecard) | Explainable to applicants and regulators; deep tree overfit (test AUC 0.54) | Head of Data Science | Pending | At each retrain |
| C12 | Thresholds | Approve <8%, refer 8–20%, decline >20% | Balances growth against loss appetite; cost of errors still to be documented | Credit Committee | Pending | Annually |
| C13 | Human review | Every refer-band case reviewed by an underwriter; declines can be appealed | Low recall (36%) and fairness concerns require human judgement | Head of SME Credit Risk | Pending | Week 14 |
| C14 | Retraining trigger | Annually, or if 2 consecutive quarters show AUC below 0.70 | A new model is a change event | Head of Data Science | Pending | Week 7 |

**Rule:** no change to C1–C14 goes live without updating this register and the inventory entry for AI-001.
