"""
app.py -- PharmEasy Regional Pulse interactive dashboard (Streamlit + Plotly),
Run with: streamlit run app.py
"""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pharmeasy.db"

st.set_page_config(page_title="PharmEasy Regional Pulse", layout="wide")
st.title("PharmEasy Regional Pulse Dashboard")


# ----Data Loading ----
@st.cache_data
def load_data():
    conn = sqlite3.connect(str(DB_PATH))
    orders = pd.read_sql("SELECT * FROM orders_clean", conn)
    regions = pd.read_sql("SELECT * FROM regions_master", conn)
    conn.close()
    orders["month"] = orders["order_date"].str[:7]
    return orders, regions


orders_df, regions_df = load_data()

# ---- Executive Summary (Task 4.2) ----
total_sales = orders_df["sales_inr"].sum()
total_profit = orders_df["profit_inr"].sum()
total_orders = orders_df["order_id"].nunique()

st.markdown("### Executive Summary")
st.markdown(
    f"Across April-June 2026, PharmEasy's Telugu-states desk processed "
    f"**{total_orders:,}** distinct orders generating **INR {total_sales:,.2f}** in total sales "
    f"and **INR {total_profit:,.2f}** in total profit. "
    f"Month-on-month trends show Hyderabad on a sustained upward trajectory "
    f"(+16.29% Apr-May, +20.61% May-Jun) while Visakhapatnam experienced a sharp "
    f"contraction in May (-62.46%) followed by partial recovery in June (+99.12%), "
    f"OTC Medicines and Prescription Medicines together account for the majority of "
    f"order volume, with Wellness & Nutrition and Medical Devices contributing higher "
    f"per-order values. "
    f"The most significant finding is Guntur's +122.19% sales spike from April to May, "
    f"the single largest swing across all regions - the category and detail views below "
    f"provide the drill-down needed to investigate its drivers."
)

# ---- Region Filter ----
all_regions = sorted(orders_df["region"].unique().tolist())
region_options = ["All Regions"] + all_regions
selected_region = st.selectbox("Filter by Region", region_options)

if selected_region == "All Regions":
    filtered_df = orders_df.copy()
else:
    filtered_df = orders_df[orders_df["region"] == selected_region].copy()

# ---- Overview Level: KPI Cards ----
st.markdown("---")
st.markdown("### Overview")
kpi_sales = filtered_df["sales_inr"].sum()
kpi_profit = filtered_df["profit_inr"].sum()
kpi_orders = filtered_df["order_id"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales (INR)", f"{kpi_sales:,.2f}")
col2.metric("Total Profit (INR)", f"{kpi_profit:,.2f}")
col3.metric("Total Orders (Distinct)", f"{kpi_orders:,}")

# ---- Charts ----
st.markdown("---")
st.markdown("### Charts")

chart_col1, chart_col2 = st.columns(2)

# 1. Line chart: Monthly sales by region (trend)
with chart_col1:
    monthly_sales = (
        filtered_df.groupby(["month", "region"])["sales_inr"]
        .sum()
        .reset_index()
    )
    # Determine highlight color for flagged region (Guntur)
    region_colors = {r: "#636EFA" for r in all_regions}
    region_colors["Guntur"] = "#EF553B"

    fig_line = px.line(
        monthly_sales,
        x="month",
        y="sales_inr",
        color="region",
        color_discrete_map=region_colors,
        title="How did regional sales trend across Apr-Jun 2026?",
        labels={"sales_inr": "Total Sales (INR)", "month": "Month", "region": "Region"},
    )
    fig_line.update_yaxes(rangemode="tozero")
    fig_line.update_layout(xaxis_type="category")
    st.plotly_chart(fig_line, use_container_width=True)

# 2. Bar chart: Total sales by region (comparison)
with chart_col2:
    region_sales = (
        filtered_df.groupby(["region"])["sales_inr"]
        .sum()
        .reset_index()
        .sort_values("sales_inr", ascending=True)
    )
    colors = ["#EF553B" if r == "Guntur" else "#636EFA" for r in region_sales["region"]]
    fig_bar = go.Figure(
        go.Bar(
            x=region_sales["sales_inr"],
            y=region_sales["region"],
            orientation="h",
            marker_color=colors,
        )
    )
    fig_bar.update_layout(
        title="Which regions generated the most total sales (Apr-Jun 2026)?",
        xaxis_title="Total Sales (INR)",
        yaxis_title="Region",
        xaxis=dict(rangemode="tozero", dtick=100000),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 3. Pie/Donut chart: Sales share by category (part-of-whole)
cat_sales = (
    filtered_df.groupby("category")["sales_inr"]
    .sum()
    .reset_index()
    .sort_values("sales_inr", ascending=False)
)
fig_pie = px.pie(
    cat_sales,
    values="sales_inr",
    names="category",
    title="What share of sales does each category contribute?",
    hole=0.4,
)
fig_pie.update_traces(textinfo="label+percent")
st.plotly_chart(fig_pie, use_container_width=True)

# ---- Category Level ----
st.markdown("---")
st.markdown("### Category Breakdown")
cat_breakdown = (
    filtered_df.groupby("category")
    .agg(
        total_sales=("sales_inr", "sum"),
        total_profit=("profit_inr", "sum"),
        order_count=("order_id", "nunique"),
    )
    .reset_index()
    .sort_values("total_sales", ascending=False)
)
cat_breakdown["total_sales"] = cat_breakdown["total_sales"].round(2)
cat_breakdown["total_profit"] = cat_breakdown["total_profit"].round(2)
st.dataframe(cat_breakdown, use_container_width=True, hide_index=True)

# ---- Detail Level ----
st.markdown("---")
st.markdown("### Detail: Region x Month Data")
detail = (
    filtered_df.groupby(["region", "month"])
    .agg(
        total_sales=("sales_inr", "sum"),
        total_profit=("profit_inr", "sum"),
        order_count=("order_id", "nunique"),
    )
    .reset_index()
    .sort_values(["region", "month"])
)
detail["total_sales"] = detail["total_sales"].round(2)
detail["total_profit"] = detail["total_profit"].round(2)
st.dataframe(detail, use_container_width=True, hide_index=True)
