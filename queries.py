"""
queries.py -- JOIN validation, duplicate-key check, COUNT(*) vs COUNT(fk) pitfall,
                per-region order counts, and region x month metrics with MoM growth.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "pharmeasy.db"


def run_queries(db_path: Path = DB_PATH) -> dict:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    results = {}

    # --- Task 2.2 ---

    # Row-count check: LEFT JOIN vs INNER JOIN
    left_join_count = cur.execute("""
        SELECT COUNT(*) FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
    """).fetchone()[0]

    inner_join_count = cur.execute("""
        SELECT COUNT(*) FROM regions_master r
        INNER JOIN orders_clean o ON r.region = o.region
    """).fetchone()[0]

    results["left_join_count"] = left_join_count
    results["inner_join_count"] = inner_join_count
    results["join_delta"] = left_join_count - inner_join_count

    print("=== Task 2.2: JOIN validation ===")
    print(f"LEFT JOIN row count: {left_join_count}")
    print(f"INNER JOIN row count: {inner_join_count}")
    print(f"Delta (LEFT - INNER): {left_join_count - inner_join_count}")
    print()

    # Duplicate-key check
    dup_rows = cur.execute("""
        SELECT order_id, COUNT(*) as cnt
        FROM orders_clean
        GROUP BY order_id
        HAVING COUNT(*) > 1
    """).fetchall()

    results["duplicate_order_ids"] = dup_rows
    print(f"Duplicate order_id rows: {len(dup_rows)} (expected 0)")
    print()

    # COUNT(*) vs COUNT(order_id) pitfall
    count_comparison = cur.execute("""
        SELECT r.region,
               COUNT(*) AS count_star,
               COUNT(o.order_id) AS count_order_id
        FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
        GROUP BY r.region
        ORDER BY r.region
    """).fetchall()

    results["count_comparison"] = count_comparison
    print("COUNT(*) vs COUNT(order_id) comparison:")
    print(f"{'Region':<20} {'COUNT(*)':<12} {'COUNT(order_id)':<18} {'Match?'}")
    print("-" * 65)
    for region, count_star, count_oid in count_comparison:
        match = "YES" if count_star > count_oid else "NO <-- disagree"
        print(f"{region:<20} {count_star:<12} {count_oid:<18} {match}")
    print()

    # Per-region order counts via LEFT JOIN + GROUP BY, ordered ascending
    per_region = cur.execute("""
        SELECT r.region,
               COUNT(o.order_id) AS order_count
        FROM regions_master r
        LEFT JOIN orders_clean o ON r.region = o.region
        GROUP BY r.region
        ORDER BY order_count ASC
    """).fetchall()

    results["per_region_order_counts"] = per_region
    print("Per-region order counts (ascending);")
    for region, cnt in per_region:
        print(f"{region:<20} {cnt}")
    print()

    # --- Task 2.3: Region x month metrics and MoM growth ---
    region_month_sales = cur.execute("""
        SELECT region,
               SUBSTR(order_date, 1, 7) AS month,
               SUM(sales_inr) AS total_sales
        FROM orders_clean
        GROUP BY region, SUBSTR(order_date, 1, 7)
        ORDER BY region, month
    """).fetchall()

    results["results_month_sales"] = region_month_sales
    print("=== Task 2.3: Region x Month Sales ===")
    print(f"{'Region':<20} {'Month':<12} {'Total Sales (INR)'}")
    print("-" * 50)
    for region, month, total_sales in region_month_sales:
        print(f"{region:<20} {month:<12} {total_sales:>14,.2f}")
    print()

    # Compute MoM growth
    # Build lookup: {(region, month): total_sales}
    sales_lookup = {}
    for region, month, total_sales in region_month_sales:
        sales_lookup[(region, month)] = total_sales

    regions = sorted(set(r for r, m in sales_lookup))
    months = ["2026-04", "2026-05", "2026-06"]
    transitions = [("2026-04", "2026-05"), ("2026-05", "2026-06")]

    mom_growth = {}
    print("Month-on-Month Growth (%):")
    print(f"{'Region':<20} {'Apr->May':<15} {'May->Jun':<15}")
    print("-" * 50)
    for region in regions:
        row_vals = []
        for prev_m, curr_m in transitions:
            prev_sales = sales_lookup.get((region, prev_m), 0)
            curr_sales = sales_lookup.get((region, curr_m), 0)
            if prev_sales == 0:
                pct = 0.0
            else:
                pct = round((curr_sales - prev_sales) / prev_sales * 100, 2)
            mom_growth[(region, f"{prev_m}->{curr_m}")] = pct
            row_vals.append(pct)
        print(f"{region:<20} {row_vals[0]:>12.2f}% {row_vals[1]:>12.2f}%")
    print()

    results["mom_growth"] = mom_growth

    conn.close()
    return results


if __name__ == "__main__":
    run_queries()