# Known limitations

1. **Ticket scope mismatch.** The export includes 139 rows created before 1 Jan 2025. They are excluded because the brief defines Jan 2025–Jun 2026.
2. **Intake tags are noisy.** The bot creates the initial category and agents rarely correct it. Existing tags are not treated as ground truth.
3. **Resolver team is a proxy for workload.** It is more operationally useful than `assigned_team`, but a resolved ticket is still not a direct measure of effort.
4. **Transfers are only populated in the current helpdesk.** The process-cost calculation uses the current-helpdesk window from 14 Sep 2025 onward.
5. **Transfer economics are planning estimates.** Rs 305 is the policy's fully loaded transfer cost. Not every transfer is avoidable, so the 50% savings scenario is a target, not observed savings.
6. **The 650/week projection is an extrapolation.** The supplied file averages far below that run rate, so the monthly/yearly process cost is scaled to the stated current volume.
7. **No autonomous routing.** The tool suggests a category. It does not modify helpdesk state.
8. **Validation is a spot-check, not a benchmark.** A fixed random sample of 50 had 0 observed mismatches, but the review labels were AI-assisted rather than an independent human gold set. Treating those 50 labels as correct and independent gives a one-sided 95% upper bound of about 5.8% (~6%) on the true mismatch rate; that is not a production guarantee. A larger blind human-reviewed audit should precede production use.
9. **Re-run check.** The final tool was extracted into a fresh project directory and re-run against the supplied tickets/agent files; it reproduced the shipped metrics exactly. This environment could not verify downloading dependencies from PyPI.
10. **Open/pending tickets are included in volume.** 577 in-scope tickets are open or pending yet carry an `agent_id`; `resolver_team` for these means the handling agent's team, not a completed resolution.
11. **Tier 2 stays in the percentage denominators.** It is shown but not compared with Tier 1. Excluding tickets resolved by Tier 2 agents gives roughly Billing 22.1% -> 16.4% and Logistics 17.3% -> 23.4%: same conclusion.
12. **Misroute-linked transfers are a proxy.** In the current helpdesk, 341 tickets whose resolving team differs from the first-assigned team have 0 recorded transfers, and 138 same-team tickets have transfers > 0. Total current-helpdesk transfers are 1,299, of which 1,143 sit on mismatched tickets.
13. **The fallback classifier learns from the noisy bot tag.** Rules decide first; the local model only handles cases the rules do not, but its training labels are the intake tags.
14. **Duplicate check.** No repeated ticket IDs, no repeated customer+SKU+message rows, and no legacy/helpdesk pairs for the same customer+SKU within 24h were found, so no de-duplication was applied.

