# Vireo Audio — Support Ticket Tool

Small, local, reproducible analysis for the Vireo Audio ticket pack.

## What it does

- Filters the analysis to **1 Jan 2025–30 Jun 2026**.
- Reconstructs the **resolving team** from `agents.csv` using `agent_id` and the ticket creation date.
- Produces an **AI-assisted category suggestion** from `customer_message` + `agent_notes`.
- Uses high-precision policy/routing rules first; a local TF-IDF + logistic-regression model is used when rules are not decisive.
- Produces monthly category and resolving-team volumes.
- Reconciles first-assigned volume vs actual resolving-team volume.
- Estimates the transfer-cost case using the policy's **Rs 305 per transfer** planning figure.

The model is deliberately advisory. The intake `category` is treated as noisy because the email thread says it is set by the chatbot at creation and agents rarely correct it.

## Clean-machine setup

Python 3.10+ is recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Put the pack's `tickets.csv` and `agents.csv` somewhere local (the reviewer supplies these files from the challenge pack; keep them outside this public repository), then run:

```bash
python support_tool.py \
  --tickets /path/to/tickets.csv \
  --agents /path/to/agents.csv \
  --out output
```

The script does **not** upload data or call a paid model/API.

## Outputs

- `ticket_predictions.csv` — generated locally on each run; **not committed to the public repo** because it contains ticket-level client text.
- `validation_audit.csv` — labels-only validation artifact (ticket ID, AI-assisted audit label, tool label, match); it contains no customer text or agent notes.
- `monthly_category_ai.csv` — monthly AI-assisted category counts.
- `monthly_category_current_tag.csv` — monthly original-tag counts.
- `monthly_resolving_team.csv` — monthly resolving-team counts.
- `team_intake_vs_resolving.csv` — first-assigned vs resolving volume.
- `metrics.json` — key business and cost metrics.
- `monthly_ai_category.png` and `monthly_resolving_team.png`.
- `report.html` — self-contained summary for review; charts are embedded, so it can be opened directly from any folder.

## Important interpretation

The support policy says Tier 2 agents should not be compared with Tier 1 on ticket volume. `Escalations & Warranty` therefore remains visible but is not used as a Tier-1 staffing comparison.

The dataset includes 139 rows created before 1 Jan 2025 even though the pack defines the analysis window as Jan 2025–Jun 2026. The tool excludes them rather than silently changing the brief.

## Validation

A fixed **50-ticket random sample** (seed `20261001`) was second-pass reviewed with **AI assistance** from `customer_message` + `agent_notes`, without using the original intake tag as the target. The audit found **0 disagreements in 50 checks (0% observed mismatch)**. This is **not an independent human gold set** and is only a spot-check. Treating the 50 review labels as correct and independent, the one-sided 95% binomial upper bound on the true mismatch rate is about **5.8% (~6%)**; because the review itself was AI-assisted, this is an uncertainty bound, not a production accuracy guarantee.

## Deliberate scope choices

Not required for the headcount/process decision:
- order/customer/product joins
- refund/replacement unit economics
- CSAT modelling
- a production API/UI
- autonomous routing

The first pass is intentionally small and reproducible.

## Project structure

`support_tool.py` is the only executable application file. The `docs/` folder contains the decision log, validation notes, limitations, recording script, memo, and this submission map. The `output/` folder contains only aggregate analysis artifacts; raw client files stay outside the public repository.

For the challenge handoff, see `docs/SUBMISSION_MAP.md`.
