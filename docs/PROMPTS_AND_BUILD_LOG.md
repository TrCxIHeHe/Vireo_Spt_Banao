# Prompts, experiments, and discarded work

## AI used outside the submitted local model

I used ChatGPT to reason through the brief, inspect the data, shape the analysis, draft the memo, and write/debug the local tool.

## Local model in the tool

- TF-IDF word + character n-grams
- Logistic regression
- No paid API/model calls
- No customer data leaves the machine

## What changed between versions

### v1 — pure keyword rules
Useful for obvious cases, but too brittle when a customer asked for a refund about a delivery problem or when the existing `Other` bucket contained mixed intents.

### v2 — text classifier only
A TF-IDF + logistic-regression model replicated the existing bot tags reasonably well, but that was the wrong target: the bot tag is part of the problem. I dropped “match the old tag” as the success criterion.

### Final — hybrid
High-precision policy/routing rules resolve explicit issue types first; the local classifier handles the residual cases. The final rule pass was tightened around three recurring ambiguity classes: payment-without-order, address/delivery updates, and return/cancellation language in hardware cases.

The result is positioned as an advisory categorizer, not an autonomous router.

## Prompts used with ChatGPT

1. “Treat the Vireo brief, email thread, README and support policy as the source of truth; identify the operational decision the client is actually trying to make.”
2. “Reconstruct resolving-team workload from the agent roster and ticket resolver rather than assuming the first-assigned team equals ownership.”
3. “Design a small reproducible local tool that categorizes tickets from the two free-text fields, produces monthly category/team breakdowns, and quantifies routing waste.”
4. “Audit the proposed categorizer on a separate fixed random sample and record the kind of mistakes it makes.” The final audit was AI-assisted and therefore is not claimed as an independent human gold set.

## What I threw away

- A pure keyword-only categorizer.
- A model optimized to reproduce the intake bot's labels.
- An attempt to make a full dashboard before the business case was stable.
- Autonomous routing as a product decision; the observed ambiguity risk was not low enough to justify silent rerouting.

## Validation caveat

The 50-ticket audit labels were generated with AI assistance. The public `output/validation_audit.csv` exposes only ticket IDs, audit labels, tool labels, and match flags so the client can cross-check against the supplied pack without publishing customer text.

## Model-label caveat

The fallback TF-IDF + logistic-regression classifier is trained on the existing bot `category` field. Those labels are noisy by design. The classifier is only used when the higher-precision rule layer is inconclusive, but it can still inherit the bot taxonomy's errors.
