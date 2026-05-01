import streamlit as st
import pandas as pd
from datetime import datetime
import api

st.title("💸 Expense Tracker")

now = datetime.now()
current_month = now.strftime("%Y-%m")
month_label   = now.strftime("%B %Y")

# ── Fetch summary ─────────────────────────────────────────────────────────────
try:
    summary = api.get_summary(current_month)
    trend   = api.get_monthly_trend()
except Exception as e:
    st.error(f"Cannot reach backend: {e}")
    st.stop()

total        = summary["total"]
by_category  = summary["by_category"]

# ── Top KPI cards ─────────────────────────────────────────────────────────────
st.subheader(f"📅 {month_label}")
col1, col2, col3 = st.columns(3)

col1.metric("Total Spent", f"₹{total:,.2f}")
col2.metric("Categories Used", len(by_category))

if trend and len(trend) >= 2:
    prev  = trend[-2]["total"]
    delta = total - prev
    col3.metric("vs Last Month", f"₹{delta:+,.2f}", delta_color="inverse")
else:
    col3.metric("Transactions", len(api.list_expenses(month=current_month)))

st.divider()

# ── Category breakdown ────────────────────────────────────────────────────────
if not by_category:
    st.info("No expenses this month. Go to **Add Expense** to log your first one.")
else:
    st.subheader("Spending by Category")
    for item in by_category:
        pct = (item["total"] / total * 100) if total > 0 else 0
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.progress(pct / 100, text=item["category"])
        col2.write(f"₹{item['total']:,.2f}")
        col3.caption(f"{pct:.1f}%")

st.divider()

# ── Recent transactions ───────────────────────────────────────────────────────
st.subheader("Recent Transactions")
try:
    expenses = api.list_expenses(month=current_month)
except Exception:
    expenses = []

if not expenses:
    st.info("No transactions this month.")
else:
    for exp in expenses[:10]:
        col1, col2, col3 = st.columns([4, 2, 1])
        col1.write(f"**{exp['description'] or exp['category']}**  `{exp['category']}`")
        col2.write(exp["date"])
        col3.write(f"₹{exp['amount']:,.2f}")
