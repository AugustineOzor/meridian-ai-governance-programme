"The model declined her, not us."

This week I built a credit model for a fictional bank to show why that sentence is wrong.

A credit model doesn't decline anyone. It produces a probability. People choose the thresholds that turn it into approve, refer or decline. On the same 2024 loans, one policy sends 995 applicants to a human underwriter. Another sends zero.

Three things the model review caught:

→ A data leak. One field was only filled in after a default. With it, the model looked 99% perfect. Without it: 79%. The "perfect" model would have failed on day one.

→ The accuracy trap. Predicting "nobody defaults" scored 91% accuracy and caught zero defaults.

→ Unequal outcomes with no protected input. Owner group wasn't in the model, yet one group was approved less often while defaulting slightly less. The route: collateral.

The model learns the weights. People choose the features, the label, the data and the thresholds. Governance lives in those choices, so each one now has an owner in a register.

Model, review and board explainer: [repo link]

#AIGovernance #ModelRisk #ResponsibleAI #GRC #CreditRisk
