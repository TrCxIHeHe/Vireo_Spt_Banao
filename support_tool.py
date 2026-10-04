
#!/usr/bin/env python3
"""
Vireo Audio support-ticket analyzer.

Reads tickets.csv + agents.csv, filters to Jan 2025-Jun 2026,
suggests semantic categories from the two free-text fields, reconciles
first-assigned vs resolving-team volumes, and writes monthly tables/charts.

No paid API/model calls are required.
"""
from __future__ import annotations
import argparse, base64, json, re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression


START = pd.Timestamp("2025-01-01")
END = pd.Timestamp("2026-06-30 23:59:59")
TRANSFER_COST_INR = 305
AGENT_HOUR_INR = 165


def high_precision_cat(message: str, note: str) -> str | None:
    """Policy-aware issue categorizer. Returns None when rules are not decisive."""
    m = re.sub(r"[^a-z0-9]+", " ", str(message).lower())
    n = re.sub(r"[^a-z0-9]+", " ", str(note).lower())
    s = m + " " + n

    # Explicit service / warranty status. Do not let a mere RMA mention
    # override an obvious underlying issue in the customer opening message.
    if re.search(r"\b(warranty claim|wty claim|claim number|claim status|repair status|service centre|service center)\b", s):
        if re.search(r"\b(screen|touch|display|audio|sound|pairing|bluetooth|battery|charging|charge)\b", m) and not re.search(r"\b(warranty claim|repair|rma|service centre|service center)\b", m):
            pass
        else:
            return "Warranty & Repair"

    if re.search(r"\b(firmware update|firmware upadte|update (?:failed|stuck|hang)|update failed|update hang|progress bar|loading screen in the app|app closes|app not opening|app crash|recovery mode|software update)\b", s):
        return "App & Firmware"

    # Explicit hardware faults should outrank a later refund/replacement request.
    if re.search(r"\b(strap pin came off|strap pin|hinge|button broken|case cracked|body cracked|screen unresponsive|screen lights up|touch(?:screen)?|tap ten times|touch not responding|display|speaker not powering on|device not powering on)\b", m):
        return "Warranty & Repair"

    if re.search(r"\b(battery|battery backup|battery life|drain(?:ing)?|goes from full to empty|charge it twice|charging case|case is not charging|not charging|won t charge|wont charge|won t turn on|wont turn on|no lights|case no led|no led)\b", s):
        return "Charging & Battery"

    if re.search(r"\b(single side|one side|one ear|right earbud.*silent|left earbud.*silent|sound (?:like|comes)|static noise|hiss|crackling sound|audio distortion|distorted audio|mic|microphone|sound quality|underwater)\b", s):
        return "Audio Quality"

    if re.search(r"\b(pairing|pair\b|bluetooth|disconnect(?:s)?|connection dropping|keeps losing my phone|device list|wifi|wi fi|network setup|cannot connect|cannto connect|not discoverable)\b", s):
        return "Connectivity"

    # Return-pickup/cancellation cases are returns even when a courier or refund is mentioned.
    if re.search(r"\b(return pickup|return pickup has not|refund not|refund pending|refund delay|refund not received|where is the money for the return|pickup has not happened|pickup pending|pkp not done|cancel order|cancellation|cancelled before dispatch|change of mind|reverse pickup|reverse)\b", m) or "cncel" in m or "cancell" in m:
        return "Returns & Refunds"

    if re.search(r"\b(order not delivered|not delivered|shipment not received|delivery delayed|tracking|courier|rto\b|reship|out for delivery|stuck on shipped|got something else|wrong item|wrong variant|wrong colour|wrong color|box was crushed|dent on the case|damaged in transit|damaged.*(?:box|case)|delivery address|change delivery address|shipping address|address update|wrong pincode|nothing in hand)\b", s):
        return "Delivery & Shipping"

    if re.search(r"\b(invoice|gst invoice|gstin|promo code|coupon|discount|festive offer|charged twice|duplicate payment|paid but .*no order|paid .* no order|no order id|amount deducted|bank shows .*twice|bank .* went to you .* no order|payment gateway|payment failed|payment debited|transaction|after i paid|payment was done|paid and .*nothing shows)\b", s):
        return "Billing & Payments"

    if re.search(r"\b(otp|login|log in|logged in|password|account)\b", s):
        return "Account & Login"

    if re.search(r"\b(before i buy|pre sales|pre purchase|product enquiry|product inquiry|spec sheet|compatible with|compatibility|will this survive a shower|does .* work with iphone)\b", s):
        return "Product Enquiry"

    return None


def resolver_team_for_ticket(tickets: pd.DataFrame, roster: pd.DataFrame) -> pd.Series:
    roster = roster.copy()
    roster["from_dt"] = pd.to_datetime(roster["from_date"], errors="coerce")
    roster["to_dt"] = pd.to_datetime(roster["to_date"], errors="coerce").fillna(pd.Timestamp("2099-12-31"))
    # Small data pack: interval lookup is easier to audit than a complex interval join.
    result = []
    for r in tickets[["agent_id", "created_dt"]].itertuples(index=False):
        m = roster[(roster.agent_id == r.agent_id) &
                   (roster.from_dt <= r.created_dt) &
                   (roster.to_dt >= r.created_dt)]
        if len(m):
            result.append(m.sort_values("from_dt").iloc[-1]["team"])
        else:
            result.append(np.nan)
    return pd.Series(result, index=tickets.index)


def build_model(text: pd.Series, labels: pd.Series):
    feats = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=100000, sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=100000, sublinear_tf=True)),
    ])
    X = feats.fit_transform(text)
    clf = LogisticRegression(max_iter=1200, class_weight="balanced", C=2)
    clf.fit(X, labels)
    return feats, clf


def run(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    tickets = pd.read_csv(args.tickets)
    agents = pd.read_csv(args.agents)

    tickets["created_dt"] = pd.to_datetime(tickets["created_at"], errors="coerce")
    in_scope = tickets[(tickets.created_dt >= START) & (tickets.created_dt <= END)].copy()

    in_scope["resolver_team"] = resolver_team_for_ticket(in_scope, agents)
    in_scope["text"] = (in_scope.customer_message.fillna("") + "\n" + in_scope.agent_notes.fillna("")).str.lower()

    vectorizer, model = build_model(in_scope["text"], in_scope["category"])
    X = vectorizer.transform(in_scope["text"])
    ml_pred = model.predict(X)

    in_scope["ai_category"] = [
        high_precision_cat(a, b) or fallback
        for a, b, fallback in zip(in_scope.customer_message, in_scope.agent_notes, ml_pred)
    ]
    in_scope["month"] = in_scope.created_dt.dt.to_period("M").astype(str)

    in_scope.to_csv(out / "ticket_predictions.csv", index=False)

    in_scope.pivot_table(index="month", columns="ai_category", values="ticket_id", aggfunc="count", fill_value=0).to_csv(out / "monthly_category_ai.csv")
    in_scope.pivot_table(index="month", columns="category", values="ticket_id", aggfunc="count", fill_value=0).to_csv(out / "monthly_category_current_tag.csv")
    in_scope.pivot_table(index="month", columns="resolver_team", values="ticket_id", aggfunc="count", fill_value=0).to_csv(out / "monthly_resolving_team.csv")

    recon = pd.DataFrame({
        "team": sorted(in_scope.resolver_team.dropna().unique()),
    })
    recon["first_assigned_volume"] = recon["team"].map(in_scope.assigned_team.value_counts()).fillna(0).astype(int)
    recon["resolving_volume"] = recon["team"].map(in_scope.resolver_team.value_counts()).fillna(0).astype(int)
    recon["delta_resolving_minus_assigned"] = recon["resolving_volume"] - recon["first_assigned_volume"]
    recon.to_csv(out / "team_intake_vs_resolving.csv", index=False)

    # Transfer / misroute case exists only for current helpdesk rows after go-live.
    current = in_scope[(in_scope.created_dt >= pd.Timestamp("2025-09-14")) &
                       (in_scope.source_system == "helpdesk")].copy()
    current["misroute"] = current.assigned_team != current.resolver_team
    misroute_transfers = float(current.loc[current.misroute, "transfers"].sum())
    transfer_rate = misroute_transfers / len(current)

    # Charts
    monthly_ai = in_scope.pivot_table(index="month", columns="ai_category", values="ticket_id", aggfunc="count", fill_value=0)
    monthly_team = in_scope.pivot_table(index="month", columns="resolver_team", values="ticket_id", aggfunc="count", fill_value=0)

    plt.figure(figsize=(12, 6))
    bottom = np.zeros(len(monthly_ai))
    for col in monthly_ai.columns:
        vals = monthly_ai[col].values
        plt.bar(monthly_ai.index, vals, bottom=bottom, label=col)
        bottom += vals
    plt.xticks(rotation=60, ha="right")
    plt.ylabel("Tickets")
    plt.title("Monthly volume by AI-assisted category")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(out / "monthly_ai_category.png", dpi=160)
    plt.close()

    plt.figure(figsize=(12, 6))
    bottom = np.zeros(len(monthly_team))
    for col in monthly_team.columns:
        vals = monthly_team[col].values
        plt.bar(monthly_team.index, vals, bottom=bottom, label=col)
        bottom += vals
    plt.xticks(rotation=60, ha="right")
    plt.ylabel("Resolved tickets")
    plt.title("Monthly volume by resolving team")
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(out / "monthly_resolving_team.png", dpi=160)
    plt.close()

    annual_tickets = 650 * 52
    annual_misroute_transfer_cost = transfer_rate * annual_tickets * TRANSFER_COST_INR
    metrics = {
        "scope": {"start": str(START.date()), "end": str(END.date()), "tickets": int(len(in_scope)),
                  "out_of_scope_rows": int(len(tickets) - len(in_scope))},
        "team_reconciliation": recon.to_dict(orient="records"),
        "misrouting": {
            "current_helpdesk_tickets": int(len(current)),
            "tickets_assigned_to_a_different_resolving_team": int(current.misroute.sum()),
            "misroute_ticket_rate": float(current.misroute.mean()),
            "misroute_transfer_events": misroute_transfers,
            "misroute_transfer_events_per_ticket": transfer_rate,
            "misroute_transfer_cost_over_current_period_inr": misroute_transfers * TRANSFER_COST_INR,
        },
        "650_per_week_projection": {
            "tickets_per_year": annual_tickets,
            "annual_misroute_transfer_cost_inr": annual_misroute_transfer_cost,
            "annual_cost_at_50pct_reduction_inr": annual_misroute_transfer_cost * 0.5,
            "two_hire_cost_inr": 900000,
        },
        "tool_cost": {"paid_calls": 0, "api_cost_inr": 0},
        "notes": [
            "First-assigned team is intake routing metadata; resolver_team is reconstructed from the agent roster at ticket creation date.",
            "AI category is an advisory semantic categorization from customer_message + agent_notes. Existing bot category is treated as noisy, not ground truth.",
            "Tier 2 is not compared with Tier 1 for staffing, per support policy v3.2."
        ]
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    # Friendly HTML summary. Images are embedded so report.html is fully standalone
    # and can be opened from any folder without broken relative-image paths.
    billing_intake = int((in_scope.assigned_team == "Billing").sum())
    logistics_intake = int((in_scope.assigned_team == "Logistics").sum())
    billing_resolve = int((in_scope.resolver_team == "Billing").sum())
    logistics_resolve = int((in_scope.resolver_team == "Logistics").sum())
    def png_data_uri(path: Path) -> str:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    ai_chart_uri = png_data_uri(out / "monthly_ai_category.png")
    team_chart_uri = png_data_uri(out / "monthly_resolving_team.png")

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vireo support analysis</title>
<style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:30px auto;padding:0 18px;line-height:1.45;color:#222}}
img{{display:block;max-width:100%;height:auto;margin:18px 0 32px;border:1px solid #eee}}
table{{border-collapse:collapse;width:100%;margin:12px 0 18px}} td,th{{border:1px solid #ddd;padding:8px;text-align:left}}
h1,h2{{margin-top:28px}} .note{{background:#f6f6f6;padding:12px 14px;border-left:4px solid #999}}
</style></head><body>
<h1>Vireo Audio support analysis</h1>
<p><b>Scope:</b> {len(in_scope):,} tickets from 2025-01-01 through 2026-06-30.</p>
<div class="note"><b>Interpretation:</b> First-assigned is intake routing; resolving is reconstructed from the agent roster. The AI category is advisory.</div>
<h2>Headcount lens</h2>
<table><tr><th>Team</th><th>First-assigned</th><th>Resolving</th><th>Delta</th></tr>
{''.join(f"<tr><td>{r.team}</td><td>{int(r.first_assigned_volume):,}</td><td>{int(r.resolving_volume):,}</td><td>{int(r.delta_resolving_minus_assigned):+,}</td></tr>" for r in recon.itertuples())}
</table>
<p>Billing first-assigned: {billing_intake:,} ({billing_intake/len(in_scope):.1%}); Billing resolving: {billing_resolve:,} ({billing_resolve/len(in_scope):.1%}). 
Logistics first-assigned: {logistics_intake:,} ({logistics_intake/len(in_scope):.1%}); Logistics resolving: {logistics_resolve:,} ({logistics_resolve/len(in_scope):.1%}).</p>
<h2>Process economics</h2>
<p>Current helpdesk misroute tickets: {int(current.misroute.sum()):,} ({current.misroute.mean():.1%}). 
Misroute-linked transfer events: {misroute_transfers:,.0f}; current-period transfer cost: ₹{misroute_transfers*TRANSFER_COST_INR:,.0f}.
At 650 tickets/week, a 50% reduction in this transfer pattern is about ₹{annual_misroute_transfer_cost*0.5:,.0f}/year in avoided transfer cost (planning estimate, not observed savings).</p>
<h2>AI-assisted categories</h2>
<img alt="Monthly volume by AI-assisted category" src="{ai_chart_uri}">
<h2>Resolving team volume</h2>
<img alt="Monthly volume by resolving team" src="{team_chart_uri}">
</body></html>"""
    (out / "report.html").write_text(html, encoding="utf-8")

    print(f"Wrote analysis to {out.resolve()}")


def main():
    p = argparse.ArgumentParser(description="Vireo Audio support-ticket analyzer")
    p.add_argument("--tickets", required=True)
    p.add_argument("--agents", required=True)
    p.add_argument("--out", default="output")
    args = p.parse_args()
    run(args)

if __name__ == "__main__":
    main()
