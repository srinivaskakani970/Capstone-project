from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DATA_PATH = BASE_DIR / "pharmeasy_orders_raw.csv"
REGIONS_MASTER_PATH = BASE_DIR / "regions_master.csv"
CLEAN_DATA_PATH = BASE_DIR / "orders_clean.csv"
CLEANING_SUMMARY_PATH = BASE_DIR / "cleaning_summary.json"
REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "region",
    "category",
    "product",
    "quantity",
    "sales_inr",
    "profit_inr",
]


def validate_schema(df: pd.DataFrame, required_columns: Iterable[str]) -> dict:
    required_columns = list(required_columns)
    missing_columns = [column for column in required_columns if column not in df.columns]
    return {
        "status": "validated" if not missing_columns else "blocked_schema",
        "row_count": int(len(df)),
        "missing_columns": missing_columns,
    }


def clean_orders(
    raw_path: Path = RAW_DATA_PATH,
    regions_master_path: Path = REGIONS_MASTER_PATH,
    output_path: Path = CLEAN_DATA_PATH,
    summary_path: Path = CLEANING_SUMMARY_PATH,
) -> tuple[pd.DataFrame, dict]:
    raw_df = pd.read_csv(raw_path)
    regions_master_df = pd.read_csv(regions_master_path)

    raw_region_variants = sorted(raw_df["region"].dropna().unique().tolist())
    deduped_df = raw_df.drop_duplicates().copy()
    duplicates_removed = int(len(raw_df) - len(deduped_df))

    deduped_missing_profit = int(deduped_df["profit_inr"].isna().sum())
    deduped_missing_category = int(deduped_df["category"].isna().sum())

    deduped_df["region"] = deduped_df["region"].astype(str).str.strip().str.title()

    canonical_regions = set(regions_master_df["region"])
    active_regions = canonical_regions - {"Kurnool"}
    normalized_regions = set(deduped_df["region"].unique())
    unknown_regions = sorted(normalized_regions - canonical_regions)
    if unknown_regions:
        raise ValueError(f"Unexpected normalized region values: {unknown_regions}")
    if normalized_regions != active_regions:
        raise ValueError(f"Normalized regions do not match active regions: {sorted(normalized_regions)}")

    product_category_lookup = (
        deduped_df.dropna(subset=["category"])[["product", "category"]]
        .drop_duplicates()
        .set_index("product")["category"]
        .to_dict()
    )
    deduped_df["category"] = deduped_df["category"].fillna(deduped_df["product"].map(product_category_lookup))

    category_margin_lookup = (
        deduped_df.dropna(subset=["profit_inr"])
        .assign(profit_margin=lambda df: df["profit_inr"] / df["sales_inr"])
        .groupby("category")["profit_margin"]
        .mean()
        .to_dict()
    )

    missing_profit_mask = deduped_df["profit_inr"].isna()
    deduped_df.loc[missing_profit_mask, "profit_inr"] = deduped_df.loc[missing_profit_mask].apply(
        lambda row: round(row["sales_inr"] * category_margin_lookup[row["category"]], 2),
        axis=1,
    )

    deduped_df["quantity"] = deduped_df["quantity"].astype(int)
    deduped_df["sales_inr"] = deduped_df["sales_inr"].astype(float).round(2)
    deduped_df["profit_inr"] = deduped_df["profit_inr"].astype(float).round(2)
    deduped_df = deduped_df[REQUIRED_COLUMNS]
    deduped_df.to_csv(output_path, index=False)

    cleaned_schema = validate_schema(deduped_df, REQUIRED_COLUMNS)
    broken_schema = validate_schema(deduped_df.drop(columns=["profit_inr"]), REQUIRED_COLUMNS)

    summary = {
        "raw_rows": int(len(raw_df)),
        "clean_rows": int(len(deduped_df)),
        "duplicates_removed": duplicates_removed,
        "raw_region_variant_count": int(len(raw_region_variants)),
        "normalized_region_count": int(deduped_df["region"].nunique()),
        "raw_region_variants": raw_region_variants,
        "normalized_regions": sorted(deduped_df["region"].unique().tolist()),
        "missing_profit_before_imputation": deduped_missing_profit,
        "missing_category_before_imputation": deduped_missing_category,
        "missing_profit_after_imputation": int(deduped_df["profit_inr"].isna().sum()),
        "missing_category_after_imputation": int(deduped_df["category"].isna().sum()),
        "schema_validation_clean": cleaned_schema,
        "schema_validation_broken": broken_schema,
    }
    summary_path.write_text(json.dumps(summary, indent=2))
    return deduped_df, summary


if __name__ == "__main__":
    df, summary = clean_orders()
    print(json.dumps(summary, indent=2))