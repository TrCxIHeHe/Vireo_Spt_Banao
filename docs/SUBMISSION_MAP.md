# Vireo Audio Set E — file-by-file handoff

This file is a practical map of the final project. It is intentionally small: each file has one job.

## Public GitHub repository

Upload the contents of this folder to a new **public** GitHub repository.

### Keep / upload

- `README.md` — how to install, run, and interpret the tool.
- `requirements.txt` — Python dependencies.
- `support_tool.py` — the actual analysis program.
- `SECURITY.md` — reminder not to commit client data.
- `docs/PROMPTS_AND_BUILD_LOG.md` — what was tried, changed, and discarded.
- `docs/VALIDATION_SUMMARY.md` — how the output was checked.
- `docs/LIMITATIONS.md` — known weaknesses and shortcuts.
- `docs/recording_script.md` — the script for the required screen recording.
- `docs/SUBMISSION_MAP.md` — this handoff guide.
- `docs/memo_priya_raman.md` — copy of the one-page business memo.
- `output/monthly_category_ai.csv` — monthly AI-category counts.
- `output/monthly_category_current_tag.csv` — monthly original-tag counts.
- `output/monthly_resolving_team.csv` — monthly resolving-team counts.
- `output/team_intake_vs_resolving.csv` — first-assigned vs resolving reconciliation.
- `output/metrics.json` — business metrics used in the memo/form.
- `output/validation_audit.csv` — labels-only validation audit; no customer text.
- `output/monthly_ai_category.png` — category chart.
- `output/monthly_resolving_team.png` — team chart.
- `output/report.html` — one-file management summary.

### Do NOT upload

- Vireo's raw `tickets.csv`, `agents.csv`, `customers.csv`, `orders.csv`, or `products.csv`.
- `support-policy.pdf`.
- `email-thread.txt`.
- Any raw ticket-level export or customer-identifying output.

The repository `.gitignore` is set up to help prevent accidental client-data commits.

## Local-only input files

Keep the original client pack somewhere outside the public repository. The two files the tool actually needs for its main run are:

- `tickets.csv`
- `agents.csv`

The other client files were reviewed for context/scope, but are deliberately not required by the runnable tool.

## What each command does

Create an environment:

```bash
python -m venv .venv
```

Activate it, then install the dependencies:

```bash
pip install -r requirements.txt
```

Run the analysis:

```bash
python support_tool.py --tickets <path-to-challenge-pack>/tickets.csv --agents <path-to-challenge-pack>/agents.csv --out output
```

The run creates/refreshes the output files in `output/`.

## Required client submission

There are four things to hand in:

1. **Public GitHub URL** — the repository described above.
2. **One-page memo** — `docs/memo_priya_raman.md` or the matching copy in `submission/`.
3. **Three-minute screen recording** — record the flow in `docs/recording_script.md`, upload to Google Drive, and set the link to Viewer access.
4. **Completed submission form** — the submission form is outside this public repository. Use the prepared answer sheet from the submission bundle, then add your real Drive URL, GitHub URL, and actual hours.

## Important honesty note

The project was built with AI assistance for reasoning, scaffolding, debugging, and drafting. The submission should describe that accurately. Do not claim that no AI was used.
