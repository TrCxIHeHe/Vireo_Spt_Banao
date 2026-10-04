# Validation summary

A fixed **50-ticket random sample** (seed `20261001`) was second-pass reviewed with **AI assistance** using the `customer_message` + `agent_notes` fields. The original intake tag was not used as the target label.

Result: **0 disagreements in 50 checks (0% observed mismatch).**

This review is **not an independent human gold standard**. It is a small AI-assisted spot-check. If the 50 audit labels are treated as correct and independent, a one-sided 95% binomial upper bound on the true mismatch rate is about **5.8% (~6%)**. Because the review labels themselves were AI-assisted, that bound should not be read as a formal production-accuracy guarantee.

Expected residual-risk cases are ambiguous multi-intent tickets, typo-heavy language, and hardware cases where warranty/repair, refund, and delivery language appear together. No such mismatch was observed in this 50-ticket sample.

`output/validation_audit.csv` contains only `ticket_id`, the AI-assisted audit label, the tool label, and a match flag. It intentionally contains no customer message or agent note.

The tool remains advisory and does not modify helpdesk state.
