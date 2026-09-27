"""
metrics_engine.py -- Significance flagging with state persistence (Task 2.4).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "pharmeasy.db"
STATE_DIR = Path(__file__).parent / "state"


def compute_percentage_change_v1(current: float, previous: float) -> float:
    """Return MoM percentage change; handles division-by-zero by returning 0."""
    if previous == 0:
        return 0.0
    return round((current - previous) / previous * 100, 2)


def flag_significant_regions_v1(
    changes: dict[str, float],
    threshold: float= 8,
) -> list[str]:
    """Flag regions whose abs MoM change exceeds the threshold."""
    return sorted([region for region, pct in changes.items() if abs(pct) > threshold])


def save_state_v1(month_summary: dict, path: str | Path) -> None:
    """Persist a month's computed summary as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(month_summary, indent=2))


def load_previous_state_v1(path: str | Path) -> dict:
    """Reload a previously saved month summary from JSON."""
    path = Path(path)
    return json.loads(path.read_text())


def get_region_month_sales(db_path: Path = DB_PATH) -> dict[tuple[str, str], float]:
    """Query region x month total sales from the database."""
    conn = sqlite3.connect(str(db_path))
    rows = conn.execute("""
        SELECT region,
               SUBSTR(order_date, 1, 7) AS month,
               SUM(sales_inr) AS total_sales
        FROM orders_clean
        GROUP BY region, SUBSTR(order_date, 1, 7)
        ORDER BY region, month
    """).fetchall()
    conn.close()
    return {(r, m): s for r, m, s in rows}


def run_flagging(db_path: Path = DB_PATH) -> dict:
    """Run the full flagging pipeline and return results."""
    sales = get_region_month_sales(db_path)
    regions = sorted(set(r for r, m in sales))
    months = ["2026-04", "2026-05", "2026-06"]
    transitions = [("2026-04", "2026-05"), ("2026-05", "2026-06")]

    all_results = {}
    for prev_m, curr_m in transitions:
        transition_key = f"{prev_m}->{curr_m}"
        changes = {}
        for region in regions:
            prev_sales = sales.get((region, prev_m), 0)
            curr_sales = sales.get((region, curr_m), 0)
            changes[region] = compute_percentage_change_v1(curr_sales, prev_sales)

        flagged = flag_significant_regions_v1(changes, threshold = 8)

        month_summary = {
            "transition": transition_key,
            "changes": changes,
            "flagged_regions": flagged,
            "sales": {r: sales.get((r, prev_m), 0) for r in regions},
        }

        # Save state
        state_path = STATE_DIR / f"state_{prev_m}.json"
        save_state_v1(month_summary, state_path)

        all_results[transition_key] = {
            "changes": changes,
            "flagged": flagged,
        }

    return all_results


def demo_state_persistence() -> None:
    """Demonstrate save/load round-trip."""
    state_path = STATE_DIR / "state_2026-04.json"
    if not state_path.exists():
        print("State file not found. Run run_flaging() first.")
        return
    loaded = load_previous_state_v1(state_path)
    print("\n=== State Persistence Round-Trip ===")
    print(f"Loaded state from: {state_path}")
    print(f"Transition: {loaded['transition']}")
    print(f"Flagged regions: {loaded['flagged_regions']}")
    print(f"Changes: {json.dumps(loaded['changes'], indent=2)}")


if __name__ == "__main__":
    results = run_flagging()

    for transition, data in results.items():
        print(f"\n=== {transition} ===")
        print(f"Changes: {json.dumps(data['changes'], indent=2)}")
        print(f"Flagged regions (threshold=8): {data['flagged']}")
        not_flagged = sorted(set(data["changes"].keys()) - set(data["flagged"]))
        print(f"NOT flagged: {not_flagged}")

    demo_state_persistence()
