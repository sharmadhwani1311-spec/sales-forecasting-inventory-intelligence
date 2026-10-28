
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Sales Forecasting & Inventory Intelligence",
    page_icon="📊",
    layout="wide"
)

# Project paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

st.title("📊 Sales Forecasting & Inventory Intelligence")
st.caption("Retail demand forecasting and inventory insights")

# Load saved project outputs
@st.cache_data
def load_data():
    results = pd.read_csv(OUTPUT_DIR / "model_comparison.csv")
    inventory = pd.read_csv(
        OUTPUT_DIR / "inventory_recommendations_demo.csv"
    )
    inventory["date"] = pd.to_datetime(inventory["date"])
    return results, inventory

try:
    results, inventory = load_data()
except FileNotFoundError:
    st.error(
        "Required CSV files are missing. "
        "Check that the outputs folder contains both project CSV files."
    )
    st.stop()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

min_date = inventory["date"].min().date()
max_date = inventory["date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = inventory[
        inventory["date"].dt.date.between(start_date, end_date)
    ]
else:
    filtered = inventory.copy()

if filtered.empty:
    st.warning("No data available for this date range.")
    st.stop()

# KPI cards
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Actual Sales",
    f"{filtered['sales'].sum():,.0f}"
)

col2.metric(
    "Average Predicted Daily Demand",
    f"{filtered['predicted_daily_demand'].mean():,.0f}"
)

col3.metric(
    "Dates Requiring Stock Review",
    f"{(filtered['stock_status'] == 'Review Stock').sum():,}"
)

st.divider()

# Sales forecast chart
st.subheader("📈 Actual vs Predicted Sales")

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(filtered["date"], filtered["sales"], label="Actual Sales")
ax.plot(
    filtered["date"],
    filtered["predicted_daily_demand"],
    label="Predicted Sales"
)
ax.set_xlabel("Date")
ax.set_ylabel("Sales")
ax.legend()
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

# Model comparison
st.subheader("🤖 Model Performance Comparison")
st.dataframe(results, use_container_width=True, hide_index=True)

# Inventory insights
st.subheader("📦 Inventory Intelligence")
st.caption(
    "Stock figures are illustrative demo assumptions, "
    "not actual inventory measurements."
)


# Count inventory alerts

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Inventory Alert Summary")

    review_count = (
        filtered["stock_status"] == "Review Stock"
    ).sum()

    sufficient_count = (
        filtered["stock_status"] == "Stock Appears Sufficient"
    ).sum()

    st.metric("Dates Requiring Review", int(review_count))
    st.metric("Dates Appearing Sufficient", int(sufficient_count))

    st.caption(
        "These counts represent demo scenarios, "
        "not verified real inventory conditions."
    )
    
    st.markdown("#### Stock Status Distribution")

    status_counts = pd.Series({
        "Review Stock": int(review_count),
        "Stock Appears Sufficient": int(sufficient_count)
    })

    st.bar_chart(status_counts)


with col2:
    st.markdown("#### Reorder Quantity Trend")

    reorder_trend = (
        filtered.set_index("date")["demo_reorder_quantity"]
    )

    st.line_chart(reorder_trend)

st.markdown("#### Highest Reorder Quantities")

top_reorders = filtered.nlargest(
    10, "demo_reorder_quantity"
)[
    [
        "date",
        "predicted_daily_demand",
        "demo_current_stock",
        "demo_reorder_quantity",
        "stock_status"
    ]
]

st.dataframe(
    top_reorders,
    use_container_width=True,
    hide_index=True
)

st.markdown("#### Highest Reorder Quantities")

top_reorders = (
    filtered.nlargest(10, "demo_reorder_quantity")[
        ["date", "predicted_daily_demand",
         "demo_current_stock", "demo_reorder_quantity",
         "stock_status"]
    ]
)

st.dataframe(top_reorders, use_container_width=True, hide_index=True)


st.dataframe(
    filtered[
        [
            "date",
            "predicted_daily_demand",
            "demo_current_stock",
            "estimated_7_day_demand",
            "demo_reorder_quantity",
            "stock_status"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# Download filtered results
csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Inventory Report (CSV)",
    data=csv_data,
    file_name="inventory_report.csv",
    mime="text/csv"
)

st.caption("Sales Forecasting & Inventory Intelligence | Project Dashboard")
