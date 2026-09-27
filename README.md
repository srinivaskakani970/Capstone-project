# PharmEasy Regional Pulse

A single, repeatable pipeline that ingests a raw monthly order export, cleans and validates it, computes SQL-verified region/month performance metrics, flags significant regional movements, drafts a reviewable insight narrative and recommendation memo, routes drafts through a human review gate with audit trail, and presents everything through a local interactive Streamlit dashboard.

## Setup & Run (3 commands)

### macOS / Linux (bash / zsh)

```bash
# 1. Create a virtual environment and install dependencies
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# 2. Generate the dataset and run the full pipeline
python generate_dataset.py && python clean_data.py && python build_db.py && python queries.py && python metrics_engine.py && python draft_report.py && python review_gate.py

# 3. Launch the dashboard
streamlit run app.py
```

### Windows (PowerShell)

```powershell
# 1. Create a virtual environment and install dependencies
python -m venv venv; .\venv\Scripts\Activate; pip install -r requirements.txt

# 2. Generate the dataset and run the full pipeline
python generate_dataset.py; python clean_data.py; python build_db.py; python queries.py; python metrics_engine.py; python draft_report.py; python review_gate.py

# 3. Launch the dashboard
streamlit run app.py
```

## Repository Structure

| File | Part | Purpose |
|------|------|---------|
| 'generate_dataset.py' | 1 | Deterministic dataset generator (seed 2026) |
| 'clean_data.py' | 1 | Cleaning pipeline + 'validate_schema' function |
| 'data_quality_report.md' | 1 | Data-quality dimension mapping |
| 'build_db.py' | 2 | Builds 'pharmeasy.db' SQLite database |
| 'queries.py' | 2 | JOIN validation + region x month metrics SQL |
| 'metrics_engine.py' | 2 | Significance flagging + state persistence |
| 'draft_report.py' | 3 | 'draft_report_v1' CII insight generator |
| 'memo.md' | 3 | One-page recommendation memo (Guntur +122.19%) |
| 'review_gate.py' | 3 | 'review_gate_v1' + test harness |
| 'audit_log.jsonl' | 3 | Generated audit log (3 entries) |
| 'reliability_checklist.md' | 3 | 4-step reliability workflow checklist |
| 'app.py' | 4 | Streamlit + Plotly dashboard |
| 'presentation_storyline.md' | 4 | SCR + OCD reframings + pushback Q&A |

## Cover Note

1. **Headline finding:** Guntur recorded a +122.19% sales surge from April to May 2026 (INR 62,442.27 to INR 138,738.93), the single largest month-on-month swing across all 9 active regions, followed by a -28.11% reversion in June.

2. **Four artifacts:**
   - **Streamlit dashboard** ('app.py'): Live data exploration with KPI cards, trend/bar/donut charts, category breakdown, and region x month detail - run via 'streamlit run app.py'. 
   - **CII narrative** (embedded at the top of the dashboard): What the data means - headline KPIs, trend shape, category breakdown, implication, and pointer to the drill-down views.
   - **One-page memo** ('memo.md'): The recommendation - grounded in the Guntur +122.19% finding, with risk-tiered claims and a clear next-check date.
   - **Presentation storyline** ('presentation_storyline.md'): How you would defend the finding live - SCR framing for executive, OCD framing for regional managers, plus anticipated pushback Q&A.

3. **Recommended consumption order:** Dashboard (explore the data) -> CII narrative (understand the story) -> Memo (read the recommendation) -> Presentation storyline (prepare for the discussion).

4. **Unverified assumption:** The cause of Guntur's May spike is unknown - the order data alone cannot distinguish between a one-time bulk order, a category mix shift, or a genuine demand increase. This is flagged in the memo's Assumptions field and labeled as a hypothesis, not a fact.