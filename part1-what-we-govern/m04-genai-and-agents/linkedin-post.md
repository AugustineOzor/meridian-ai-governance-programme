I red-teamed a (simulated) bank chatbot this week. Same model, two designs.

As launched: 5 of 21 tests passed. One sentence extracted an API key from the system prompt. It leaked the internal credit policy. And a hidden instruction inside a published FAQ made it send customers a phishing link asking for their card number and PIN.

With layered controls: 16 of 21 passed, no critical failures.

What surprised me:

→ The controls that did the most cost nothing. Cleaning the retrieval index (removing an old fee schedule and an internal policy) and taking secrets out of the system prompt fixed more than any filter.

→ The remaining failures had one cause: language. Every filter worked in English. In Arabic, the bot confirmed a fee waiver and told a customer they'd likely be approved for a loan. In a bilingual market, an English-only control is half a control.

→ Controls have a price. The filter that blocks "refund" promises also blocked a correct answer about the refund policy.

I also wrote a risk sheet for a payments agent. Its most important control isn't in the prompt: the agent has no tool to approve payments or change bank details. You can't talk a model out of a permission it doesn't have.

Test suite, report and control map: [repo link]

#AIGovernance #AISecurity #LLMSecurity #RedTeaming #OWASP
