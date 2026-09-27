"""
draft_report.py -- CII insight generator (Task 3.1).
Produces one Context-Insight-Implication block per unique flagged region.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from metrics_engine import run_flagging

DB_PATH = Path(__file__).parent / "pharmeasy.db"


def get_metrics(db_path: Path = DB_PATH) -> dict:
    """Retrieve region x month sales and order counts from the database."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("""
        SELECT region,
               SUBSTR(order_date, 1, 7) AS month,
               SUM(sales_inr) AS total_sales,
               SUM(profit_inr) AS total_profit,
               COUNT(DISTINCT order_id) AS order_count
        FROM orders_clean
        GROUP BY region, SUBSTR(order_date, 1, 7)
        ORDER BY region, month
    """).fetchall()
    conn.close()
    metrics = {}
    for region, month, sales, profit, orders in rows:
        metrics.setdefault(region, {})[month] = {
            "sales": round(sales, 2),
            "profit": round(profit, 2),
            "orders": orders,
        }
    return metrics


def compute_mom_changes(metrics: dict) -> dict:
    """Compute MoM percentage changes for each region and transition."""
    transitions = [("2026-04", "2026-05"), ("2026-05", "2026-06")]
    changes = {}
    for region, month_data in metrics.items():
        for prev_m, curr_m in transitions:
            prev_sales = month_data.get(prev_m, {}).get("sales", 0)
            curr_sales = month_data.get(curr_m, {}).get("sales", 0)
            if prev_sales == 0:
                pct = 0.0
            else:
                pct = round((curr_sales - prev_sales) / prev_sales * 100, 2)
            changes.setdefault(region, {})[f"{prev_m}->{curr_m}"] = pct
    return changes


def draft_report_v1(flagged_regions: list[str], metrics: dict) -> list[dict]:
    """
    Produce one CII block per unique flagged region.
    Each block has Context, Insight, and Implication fields.
    """
    changes = compute_mom_changes(metrics)
    report_blocks = []

    for region in sorted(set(flagged_regions)):
        region_data = metrics.get(region, {})
        region_changes = changes.get(region, {})

        apr_sales = region_data.get("2026-04", {}).get("sales", 0)
        may_sales = region_data.get("2026-05", {}).get("sales", 0)
        jun_sales = region_data.get("2026-06", {}).get("sales", 0)
        apr_orders = region_data.get("2026-04", {}).get("orders", 0)
        may_orders = region_data.get("2026-05", {}).get("orders", 0)
        jun_orders = region_data.get("2026-06", {}).get("orders", 0)
        apr_may_pct = region_changes.get("2026-04->2026-05", 0)
        may_jun_pct = region_changes.get("2026-05->2026-06", 0)

        context = (
            f"{region} recorded sales of INR {apr_sales:,.2f} in April 2026 "
            f"({apr_orders} orders), INR {may_sales:,.2f} in May 2026 "
            f"({may_orders} orders), and INR {jun_sales:,.2f} in Jun 2026 "
            f"({jun_orders} orders)."
        )

        insight_parts = []
        if abs(apr_may_pct) > 8:
            direction = "increased" if apr_may_pct > 0 else "decreased"
            insight_parts.append(
                f"Sales {direction} by {apr_may_pct:+.2f}% from April to May "
                f"(INR {apr_sales:,.2f} to INR {may_sales:,.2f})."
            )
        if abs(may_jun_pct) > 8:
            direction = "increased" if may_jun_pct > 0 else "decreased"
            insight_parts.append(
                f"Sales {direction} by {may_jun_pct:+.2f}% from May to June "
                f"(INR {may_sales:,.2f} to INR {jun_sales:,.2f})."
            )
        insight = " ".join(insight_parts) if insight_parts else "No significant movement above threshold."

        if abs(apr_may_pct) > 50 or abs(may_jun_pct) > 50:
            implication = (
                f"{region} shows a swing exceeding 50% in at least one transition, "
                f"warranting immediate investigation into order-mix or operational changes."
            )
        elif abs(apr_may_pct) > 20 or abs(may_jun_pct) > 20:
            implication = (
                f"{region} shows a notable movement exceeding 20% in at least one transition: "
                f"regional leads should review category-level detail for root-cause signals."
            )
        else:
            implication = (
                f"{region} shows moderate volatility; continue monitoring and flag if the trend persists next month."
            )

        report_blocks.append({
            "region": region,
            "context": context,
            "insight": insight,
            "implication": implication,
        })

    return report_blocks


if __name__ == "__main__":
    flagging_results = run_flagging()
    metrics = get_metrics()

    # Union of flagged regions across both transitions
    all_flagged = set()
    for t_data in flagging_results.values():
        all_flagged.update(t_data["flagged"])
    all_flagged = sorted(all_flagged)

    print(f"Unique flagged regions (union of both transitions): {all_flagged}")
    print(f"count: {len(all_flagged)}\n")

    blocks = draft_report_v1(all_flagged, metrics)
    for block in blocks:
        print(f"--- {block['region']} ---")
        print(f"  Context:    {block['context']}")
        print(f"  Insight:    {block['insight']}")
        print(f"  Implication:{block['implication']}")
        print()
