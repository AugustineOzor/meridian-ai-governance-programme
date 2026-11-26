# GenAI Control Map: Customer Chatbot "Sahm" (AI-003)

**Version:** 1.0 · **Date:** 2026-11-26 · **Owner:** Head of Digital Channels · **Framework:** [OWASP Top 10 for LLM Applications (2025)](https://genai.owasp.org/llm-top-10/)

Each OWASP risk is mapped to Sahm's controls, the evidence that tests them, what each control cannot stop, and who owns the residual risk. Test results are from the [red-team report](red-team-report.md) (simulated, v2 design).

**Status key:** 🟢 controlled and tested · 🟡 controlled with known gaps · 🔴 gap open · ⚪ not applicable to this system

| OWASP risk | Applies to Sahm? | Controls | Evidence | Limits of the controls | Status | Residual owner |
| --- | --- | --- | --- | --- | --- | --- |
| **LLM01 Prompt Injection** | Yes: customer messages (direct) and knowledge-base documents (indirect) | Input filter; scope router; output commitment, URL and credential filters; KB change control | D01, D03, D05, D06, I01 pass; **D04 fails (Arabic)** | Filters are pattern lists in English; new phrasings and other languages get through. No complete fix exists | 🔴 | Head of Digital Channels |
| **LLM02 Sensitive Information Disclosure** | Yes: internal documents, customer data in chats | Customer-only index; output credential filter; no customer account data reachable | L01 passes | Does not stop customers pasting their own data; chat logs hold personal data | 🟢 | DPO |
| **LLM03 Supply Chain** | Yes: vendor uses an unnamed third-party LLM | Contract: notice of model changes, incident notification, audit rights (to add at renewal); re-test after each change | AI-003 fact sheet, upstream gap | MGB cannot assess the upstream model directly | 🟡 | Procurement + Head of Digital Channels |
| **LLM04 Data and Model Poisoning** | Yes: knowledge base can be edited | KB change approval; scan for instruction-like text before publishing (**not yet in place**) | I01: poisoned FAQ found in the approved index | Output filter hides the symptom but the document is still poisoned | 🔴 | Head of Digital Channels |
| **LLM05 Improper Output Handling** | Limited: output goes only to the chat widget | Widget renders text only (HTML escaped); output never passed to other systems | Design review | If Sahm is later connected to other systems, this risk returns | 🟢 | Head of Digital Channels |
| **LLM06 Excessive Agency** | No: Sahm has no tools and cannot act on accounts | No tools granted; any future tool use needs an agent risk review | Design review | n/a today. See [agent risk sheet](agent-risk-sheet.md) for the pattern | ⚪ | – |
| **LLM07 System Prompt Leakage** | Yes | No secrets in prompts (key rotated); input filter | D01 passes; **D02 leaks the prompt** (no secrets) | The prompt can still be extracted with obfuscation; accepted because it contains no secrets | 🟡 | CISO (accepted risk) |
| **LLM08 Vector and Embedding Weaknesses** | Yes: one retrieval index | Separate customer-only index; only `status: current` documents indexed | B01, B02, L01 pass | Relies on correct document labels; a mislabelled internal document would be indexed | 🟢 | Head of Digital Channels |
| **LLM09 Misinformation** | Yes: fees, terms, eligibility | Grounding instruction; number grounding check; scope router; disclosure that Sahm is an AI | M01, M03, B01 pass; **M02 fails** (wrong passage); **C02 fails** (Arabic) | Grounding check confirms a number exists in a source, not that it answers the question; hallucination can be reduced, never removed | 🔴 | Head of Digital Channels |
| **LLM10 Unbounded Consumption** | Yes | 2,000-character input limit; per-user rate limit and daily token budget (vendor setting) | R01 passes | Rate limit not yet tested | 🟢 | Head of Digital Channels |

## Process controls that apply across all risks

| Control | Detail | Owner |
| --- | --- | --- |
| Red-team before launch and after every vendor model change or KB release | Full suite in both languages; results attached to the AI-003 fact sheet with date and model version | Head of Digital Channels, CISO |
| Conversation monitoring | Weekly sample of 100 conversations per language; track hand-offs, refusals and complaints mentioning Sahm | Head of Digital Channels |
| Incident route | Customer complaint about a Sahm answer is logged as an AI incident and triggers a test case | Head of Digital Channels |
| Customer disclosure | Customers told they are talking to an AI and can ask for a person at any time | Head of Digital Channels |

## Go-live position

Three risks are 🔴 (LLM01, LLM04, LLM09). **Sahm v2 should not go live until the Arabic gaps (R1, R2) and the poisoned FAQ (R6) are fixed and re-tested.**

_Meridian Gulf Bank is fictional._
