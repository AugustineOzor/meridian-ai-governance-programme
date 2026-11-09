# MGB AI Inventory: Schema v1.0

| Field | Allowed values / format | Question it answers |
| --- | --- | --- |
| system_id | AI-001, AI-002 ... | How do we refer to it consistently? |
| system_name | Free text | What is it called? |
| description | One sentence | What does it do? |
| business_unit | Retail; SME Lending; HR; Compliance; Operations; IT; Marketing; Finance (semicolon-separated if several) | Where is it used? |
| business_owner | Role title | Who answers for its outcomes? |
| technical_owner | Role title or vendor | Who can change it? |
| lifecycle_status | proposed, pilot, production, retired | Is it live? |
| approval_status | approved, unapproved, to_confirm | Did anyone sanction it? |
| source | built, bought, embedded, open_source | How did we get it? |
| vendor | Name or blank | Who supplies it? |
| upstream_model | Model/provider, or `unknown` | What sits underneath? |
| ai_type | predictive_ml, generative, hybrid, agentic | What kind of AI is it? |
| value_chain_role | builder, deployer, builder+deployer | Which of our obligations apply? |
| role_change_risk | Y / N | Could we become the provider (EU AI Act Art. 25)? |
| decision_impact | informs, recommends, decides | How close is it to a final decision? |
| affected_parties | customers; applicants; employees; candidates; public | Who could be harmed? |
| personal_data | Y / N / to_confirm | Does data protection law apply? |
| jurisdictions | ISO country codes, plus EU (semicolon-separated) | Which laws might apply? |
| discovered_via | register; expense_scan; proxy_scan; interview | How did we find it? |
| upstream_evidence_gap | Free text or blank | What can't we verify? |
| last_reviewed | YYYY-MM-DD | Is this entry still current? |

## Rules
1. Use controlled values only, so the inventory can be filtered, counted and charted.
2. Owners are roles, not people.
3. If you are unsure whether something is AI, include it with `approval_status = to_confirm` and explain why in `description`.
4. Columns planned for later weeks: risk tier and residual-risk owner (Week 11), vendor assessment ref (Week 13), EU AI Act classification (Week 15).

## Change log
| Version | Date | Change |
| --- | --- | --- |
| 1.0 | 2026-11-09 | Initial schema |
