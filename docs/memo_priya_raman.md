# Memo to Priya Raman — Support tickets, Set E

**Subject: Headcount and routing — what the ticket data actually says**

Priya,

I would not use the current intake category/team chart as the headcount trigger.

The chatbot’s category is set when the ticket is created, and agents rarely correct it. I therefore used the customer opening message and agent closing note to produce an AI-assisted issue category, and reconstructed the **resolving team** from `agent_id` and the roster. The support policy also says Tier 2 should not be compared with Tier 1 on volume.

The biggest operational finding is the Billing/Logistics split. In the Jan 2025–Jun 2026 window, Billing is **2,425 tickets / 20.8%** of first-routed volume but only **1,798 / 15.4%** of resolving-team volume. Logistics is **1,905 / 16.4%** first-routed but **2,574 / 22.1%** of resolving-team volume. The supplied data therefore does not confirm “Billing is the biggest queue” as a workload statement; a large part of the Billing intake is being worked elsewhere.

The current helpdesk data makes the process cost visible. From 14 Sep 2025 through 30 Jun 2026 there are **7,728 tickets**. On **1,293 (16.7%)**, the first-assigned team differs from the resolving team. Those tickets account for **1,143 recorded transfer events**. At the policy rate of **Rs 305 per transfer**, that is **Rs 3.49 lakh** of transfer cost over the current period.

### Business target

**Cut misroute-linked transfer events by 50%, from 0.148 to about 0.074 transfer events per ticket.**

At Vireo’s stated run rate of ~650 tickets/week:

**33,800 tickets/year × 0.148 transfers/ticket × Rs 305 = ~Rs 15.25 lakh/year** of transfer cost at the observed pattern.

A 50% reduction is therefore worth about **Rs 7.6 lakh/year** in avoided transfer cost, or about **Rs 63,500/month**. This is a planning estimate, not booked savings; not every transfer is necessarily avoidable.

That is close to the **Rs 9 lakh annual cost of two hires**. I would therefore fix the routing/measurement problem before treating the current Billing percentage as the reason for two hires.

The tool itself is deliberately small: local TF-IDF + logistic regression, with policy-aware overrides for explicit issue types. It makes a category suggestion and produces monthly category/team charts; it does not silently re-route tickets.

I checked the final output on a fixed **50-ticket AI-assisted second-pass review** using the two free-text fields rather than the bot tag. It had **0 observed mismatches in 50 checks**. This is not an independent human gold set; treating those 50 labels as correct and independent gives a one-sided 95% upper bound of about **5.8% (~6%)** on the true mismatch rate. The main residual risks are ambiguous or unusually worded hardware cases; those should remain human-review cases.

One important caveat: the file supplied contains **139 rows before 1 Jan 2025** even though the brief defines Jan 2025–Jun 2026 as the window. I excluded those rows. The file averages about **148 tickets/week**, far below the stated current ~650/week, so the money case above is explicitly scaled to Vireo’s stated run rate.

Regards,

Triambak
