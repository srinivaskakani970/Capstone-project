# Data Quality Report

## Data-quality dimensions and how the pipeline addresses them

- **Accuracy**: Missing 'profit_inr' values are imputed using the mean category profit margin multiplied by 'sales_inr', ensuring profit values align with observed category-level economics.
- **Completeness**: Missing 'category' and 'profit_inr' values are imputed so the cleaned dataset has no blanks in those required analytical fields.
- **Consistency**: Region names are normalized by trimming whitespace and title-casing values so raw variants collapse onto canonical region names.
- **Timeliness**: The cleaning pipeline is deterministic and rerunnable against each monthly export so the latest file can be processed without manual spreadsheet intervention.
- **Validity**: 'validate_schema(df, required_columns)' blocks downstream use when required fields are missing and confirms the cleanest dataset retains the required structure.
- **Uniqueness**: Exact duplicate rows across all 8 columns are removed before any metrics are computed.
- **Relevance**: The pipeline preserves only the required analytical columns used by the downstream metrics, reporting, and dashboard stages.

## Fix-to-dimension mapping summary

- Removing exact duplicate rows addresses **Uniqueness**.
- Normalizing region text addresses **Consistency**.
- Inputing missing category values addresses **Completeness**.
- Inputing missing profit values addresses **Accuracy** and **Completeness**.
- Running schema validation addresses **Validity**.