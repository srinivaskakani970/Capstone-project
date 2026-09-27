# Reliability Checklist

1. **Safety check:** No personally identifiable customer data appears in the memo, narrative, or dashboard - only region-level aggregates (total sales, order counts, profit) are used, and no individual order details or customer names are exposed.

2. **Validation:** Every numerical claim in memo.md (Guntur April sales INR 62,442.27, May sales INR 138,738.93, +122.19% change, order counts 51 and 77) was cross-verified by running the SQL GROUP BY query in queries.py against pharmeasy.db and confirming the output matches the metrics_engine.py flagging results.

3. **Critique/Refine:** The memo was reviewed for unsupported causal claims; the initial draft attributed the Guntur spike to "increased regional demand," which was revised to label the cause as an unverified hypothesis and moved to the Assumptions field, since the order data alone cannot distinguish between a bulk order, a category mix shift, or a genuine demand increase.

4. **Human sign-off:** The memo has been routed through review_gate_v1 with decision "approve," and the audit_log.jsonl entry confirms the reviewer verified the numbers against the SQL output before approving distribution.