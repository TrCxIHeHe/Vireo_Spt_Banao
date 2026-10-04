# Three-minute screen-recording script

Target length: 2:30–2:50.

**0:00–0:25 — Start from clean machine**
Show `README.md`, then the venv install and the single `python support_tool.py ...` command.

**0:25–0:55 — Show the business problem**
Open `output/report.html`. Point to the Billing vs Logistics reconciliation:
- Billing is 20.8% of first-routed tickets but 15.4% of resolving volume.
- Logistics is 16.4% first-routed but 22.1% of resolving volume.

**0:55–1:35 — Show the categorizer**
After running the tool locally, open the generated `output/ticket_predictions.csv` (this file is intentionally ignored by Git because it contains ticket-level client text). Show the `category` and `ai_category` columns.
Give two examples:
- a “paid but not delivered” ticket becomes Delivery & Shipping rather than Billing.
- a “promo code invalid” ticket becomes Billing & Payments rather than Product Enquiry.

**1:35–2:05 — Show validation**
Open `output/validation_audit.csv` and `docs/VALIDATION_SUMMARY.md`:
- fixed 50-ticket sample
- AI-assisted second-pass review, not an independent human gold set
- 0 observed mismatches in 50 checks
- explain the ~6% one-sided 95% upper-bound uncertainty and why this is only a spot-check

**2:05–2:35 — What changed / what was discarded**
Show `PROMPTS_AND_BUILD_LOG.md`:
- dropped pure keywords
- dropped “match the bot tag” as the target
- kept hybrid rules + local classifier
- did not ship autonomous routing

**2:35–2:50 — Close on the business number**
State:
“Current-helpdesk data shows 1,143 transfer events on tickets that were first assigned to a different team than the resolving team. At 650 tickets/week, cutting that pattern by half is worth about Rs 7.6 lakh a year in avoided transfer cost. That is a process target, not booked savings.”
