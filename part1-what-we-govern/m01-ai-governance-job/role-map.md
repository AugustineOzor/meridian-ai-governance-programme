# MGB AI Value-Chain Role Map

**Version:** 1.0 · **Date:** 2026-11-09 · **Owner:** Head of AI Governance · **Source:** `00-inventory/inventory.csv`

Roles attach to each system, not to MGB as a whole. For each system this map records who sits upstream (who built the model), MGB's role, who is affected downstream, and whether a change could shift MGB into the provider role under EU AI Act Art. 25.

## 1. Role map: all 22 systems

| ID | System | Upstream (model builder) | MGB role | Downstream (affected) | Role-change risk |
| --- | --- | --- | --- | --- | --- |
| AI-001 | SME credit scoring model | MGB Data Science | builder+deployer | SME loan applicants | N: MGB is already the provider |
| AI-002 | AML transaction monitoring | FinGuard Analytics | deployer | Customers | N |
| AI-003 | Customer chatbot "Sahm" | ConverseAI, on an unnamed third-party LLM | deployer | Retail customers | N today. **Watch:** fine-tuning it for eligibility or credit advice would change its intended purpose into a high-risk use |
| AI-004 | Card fraud detection | SecurePay Labs | deployer | Cardholders | N |
| AI-005 | Microsoft 365 Copilot | Microsoft and its model providers | deployer | Staff; customers whose data is processed | N |
| AI-006 | CV screening in ATS | TalentFlow | deployer | Job candidates | **Y:** HR's custom scoring weights could be a substantial modification of a high-risk (employment) system |
| AI-007 | CRM next-best-offer | CustomerSphere | deployer | Customers | N |
| AI-008 | KYC ID verification | VeriDoc | deployer | Onboarding applicants | N |
| AI-009 | Collections propensity model | MGB Data Science | builder+deployer | Customers in arrears | N: already the provider |
| AI-010 | ChatGPT (consumer) | OpenAI | deployer | Customers, staff, candidates whose data is entered | N |
| AI-011 | Claude (consumer) | Anthropic | deployer | Customers, staff | N |
| AI-012 | Gamma | Gamma Tech (upstream not disclosed) | deployer | Customers named in decks | N |
| AI-013 | DeepL | DeepL SE | deployer | Customers, staff in translated documents | N |
| AI-014 | Otter.ai | Otter.ai | deployer | Staff, candidates recorded | N |
| AI-015 | Perplexity | Perplexity AI and third-party models | deployer | Staff | N |
| AI-016 | OpenAI API (direct) | OpenAI | builder+deployer | Customers whose data the scripts process | N: already a builder, without controls |
| AI-017 | Fireflies.ai | Fireflies.ai | deployer | Staff, customers recorded | N |
| AI-018 | Gemini (consumer) | Google | deployer | Customers, staff | N |
| AI-019 | Hugging Face Hub | Various open-source model authors | builder+deployer | Depends on use | **Y:** any downloaded model put into a business process makes MGB its provider (AI-022 is one) |
| AI-020 | Midjourney | Midjourney | deployer | Public seeing marketing images | N |
| AI-021 | FP&A AI forecasting | PlanRight (model not disclosed) | deployer | Internal budget holders | N |
| AI-022 | Adverse-media sentiment script | Open-source model author on Hugging Face | builder+deployer | Clients being screened | N: already a builder. The model was taken from AI-019 |

## 2. Upstream-gap decisions

For each system with an `upstream_evidence_gap`, this table records which of the five responses was chosen: **(1)** ask in writing and record the gap, **(2)** narrow the use, **(3)** test downstream, **(4)** contract terms, **(5)** named risk owner with a review date.

| ID | Gap | Responses | Reasoning |
| --- | --- | --- | --- |
| AI-002 | No model validation report | 1, 3, 4, 5 | AML is regulated and missed alerts are costly. Request the report, run MGB's own alert-quality sample testing, add audit rights at renewal. Owner: MLRO, 6-month review |
| AI-003 | Underlying LLM and training data unknown | 1, 2, 3, 4, 5 | Customer-facing generative AI. Restrict it to product and process questions with hand-off for eligibility and complaints, run a 200-question Arabic and English test set, require notice of model changes. Owner: Head of Digital Channels, 6-month review |
| AI-004 | Retraining cadence and false positives by segment unknown | 1, 3, 5 | Automated blocking affects customers directly. Monitor false-positive complaints by segment monthly. Owner: Head of Fraud Operations |
| AI-006 | No model documentation or bias testing | 1, 2, 3, 4, 5 | High-risk employment use. Until evidence arrives, the ranking is advisory only and every rejection gets human review. Run an impact-ratio test on MGB's own applicant data (Week 17). Owner: Head of Talent Acquisition, 3-month review |
| AI-007 | Inputs used by the AI feature unknown | 1, 2, 5 | Ask the vendor which customer data drives offers, and exclude sensitive attributes in configuration. Owner: Head of Marketing |
| AI-008 | No accuracy breakdown by age, skin tone or document type | 1, 3, 4, 5 | Face matching with uneven accuracy can exclude customers. Measure manual-review referral rates by segment. Owner: Head of Customer Onboarding |
| AI-010, 011, 012, 013, 015, 018 | Consumer terms only; training use of inputs unconfirmed | 2, 5 | No vendor relationship exists to ask, so control use instead: interim notice bans confidential data, and staff move to Copilot (AI-005). Owners: department heads named in the inventory, review at 3 months |
| AI-014, 017 | Recordings stored with vendor, no contract | 2, 5 | Stop use in HR, Compliance and customer meetings immediately. Decide whether to approve a contracted note-taker. Owners: CHRO and CCO |
| AI-016 | Scripts, prompts and data unknown; personal API key | 1, 2, 4, 5 | Internal "ask" means requiring the developers to document every script. Move to a company-paid platform with logging and data-use terms. Owner: CIO |
| AI-019 | Downloaded models and their use not recorded | 1, 2, 5 | Require registration of any model before it touches business data. Owner: CIO |
| AI-020 | IP rights in generated images unclear | 1, 2, 5 | Restrict to internal and concept use until Legal reviews the terms (Week 18). Owner: Head of Marketing |
| AI-021 | Model and training data not described | 1, 5 | Low impact: internal forecasts with no personal data. Request documentation and keep human sign-off on budgets. Owner: CFO |
| AI-022 | Model card, training data and accuracy on financial news not reviewed | 2, 3, 5 | Highest-priority gap. Suspend its effect on client decisions now, then test it on labelled financial news before any reinstatement. Owner: CCO, 1-month review |

## 3. Scoping decisions: reviewed and excluded

| Candidate | Source | Decision | Reasoning |
| --- | --- | --- | --- |
| Operations Excel macro flagging payments over QAR 500k | Interview, Head of Operations, 2026-11-09 | Excluded from the AI inventory | It applies a fixed threshold that a person wrote and infers nothing from data, so it fails the "infers" test in the OECD and EU AI Act (Art. 3(1)) definitions. Re-assess if an ML score or learned threshold is added |

---
_Meridian Gulf Bank is fictional. All data is synthetic. This is independent study._
