# Analysis Notes: Reading the Scan Like an Auditor

Working notes from Step 2, written before drafting the findings report.

**1. Why is the direct OpenAI API (AI-016) a different risk from staff using consumer ChatGPT (AI-010)?**
A staff member using ChatGPT is a *user* of someone else's product, which makes MGB a careless deployer. IT staff calling the API from their own scripts are *building* a system: they choose the prompts, the data that goes in and what happens to the output. That makes MGB a builder, so design, testing, documentation and, if a script touches a high-risk use, provider obligations all apply, and none of it is happening. The personal API key also means there are no company logs, no data-use terms and no continuity if that person leaves.

**2. Which findings involve departments likely to handle personal or credit data?**
- **SME Lending:** ChatGPT and Gamma. Client financial statements and credit memos are likely inputs.
- **HR:** ChatGPT and Otter.ai. Candidate CVs, interview recordings and employee relations.
- **Compliance:** Claude, DeepL, Perplexity and Fireflies. Client due-diligence files and suspicious-activity work.
- **Finance:** ChatGPT and Perplexity. Less personal data, but confidential financial information.

**3. What AI would this method never detect?**
- AI features embedded in approved software (found AI-021 only through an interview).
- Free tools used on personal phones or home networks.
- Any AI tool not in the 18-pattern catalogue.
- AI inside vendor services, where the vendor uses AI on MGB's behalf (an outsourced call centre, for example).
- Locally run models: once downloaded from Hugging Face, they generate no further proxy traffic (AI-022 is the example).

**Takeaway:** the scan is good at finding *paid web tools* and blind to *built and embedded* AI, which are the higher-risk categories. Interviews are not optional.
