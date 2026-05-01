import streamlit as st
import pandas as pd
from datetime import datetime
import api

st.title("📋 Expense History")

try:
    categories = api.get_categories()
except Exception as e:
    st.error(f"Cannot reach backend: {e}")
    st.stop()

# ── Filters ───────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

months = []
now = datetime.now()
for i in range(6):
    from datetime import timedelta
    m = (now.replace(day=1) - timedelta(days=i * 28)).strftime("%Y-%m")
    months.append(m)
months = sorted(set(months), reverse=True)

selected_month    = col1.selectbox("Month", months, index=0)
selected_category = col2.selectbox("Category", ["All"] + categories)

filter_category = None if selected_category == "All" else selected_category

try:
    expenses = api.list_expenses(month=selected_month, category=filter_category)
except Exception as e:
    st.error(f"Failed to fetch expenses: {e}")
    st.stop()

# ── Table ─────────────────────────────────────────────────────────────────────
st.subheader(f"Results ({len(expenses)} transactions)")

if not expenses:
    st.info("No expenses found for the selected filters.")
else:
    total = sum(e["amount"] for e in expenses)
    st.metric("Total", f"₹{total:,.2f}")

    for exp in expenses:
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        col1.write(f"**{exp['description'] or '—'}**")
        col2.write(f"`{exp['category']}`  {exp['date']}")
        col3.write(f"₹{exp['amount']:,.2f}")
        if col4.button("🗑", key=f"del_{exp['id']}"):
            try:
                api.delete_expense(exp["id"])
                st.success("Deleted.")
                st.rerun()
            except Exception as e:
                st.error(f"Delete failed: {e}")
