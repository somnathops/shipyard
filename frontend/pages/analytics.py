import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import api

st.title("📊 Analytics")

try:
    trend   = api.get_monthly_trend()
    summary = api.get_summary()
except Exception as e:
    st.error(f"Cannot reach backend: {e}")
    st.stop()

# ── Monthly Trend Bar Chart ───────────────────────────────────────────────────
st.subheader("Monthly Spending Trend")

if not trend:
    st.info("Not enough data yet. Add some expenses to see charts.")
else:
    df_trend = pd.DataFrame(trend)
    fig_bar = px.bar(
        df_trend,
        x="month",
        y="total",
        labels={"month": "Month", "total": "Amount (₹)"},
        color_discrete_sequence=["#63b3ed"],
        text_auto=".0f",
    )
    fig_bar.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font_color="#cbd5e0",
        xaxis=dict(gridcolor="#1f2937"),
        yaxis=dict(gridcolor="#1f2937"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Category Pie Chart (current month) ───────────────────────────────────────
month_label = datetime.now().strftime("%B %Y")
st.subheader(f"Category Breakdown — {month_label}")

by_category = summary.get("by_category", [])

if not by_category:
    st.info("No expenses this month.")
else:
    df_cat = pd.DataFrame(by_category)
    fig_pie = px.pie(
        df_cat,
        names="category",
        values="total",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig_pie.update_layout(
        plot_bgcolor="#0d1117",
        paper_bgcolor="#0d1117",
        font_color="#cbd5e0",
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Breakdown Table")
    total = summary["total"]
    for item in by_category:
        pct = (item["total"] / total * 100) if total > 0 else 0
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(item["category"])
        col2.write(f"₹{item['total']:,.2f}")
        col3.caption(f"{pct:.1f}%")
