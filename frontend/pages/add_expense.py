import streamlit as st
from datetime import date
import api

st.title("➕ Add Expense")

try:
    categories = api.get_categories()
except Exception as e:
    st.error(f"Cannot reach backend: {e}")
    st.stop()

with st.form("add_expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    amount      = col1.number_input("Amount (₹)", min_value=0.01, step=0.50, format="%.2f")
    category    = col2.selectbox("Category", categories)
    description = st.text_input("Description", placeholder="e.g. Lunch at Subway")
    exp_date    = st.date_input("Date", value=date.today())
    submitted   = st.form_submit_button("Save Expense 💾", use_container_width=True)

    if submitted:
        if amount <= 0:
            st.warning("Amount must be greater than 0.")
        else:
            try:
                api.add_expense(
                    amount=amount,
                    category=category,
                    description=description.strip(),
                    date=exp_date.isoformat(),
                )
                st.success(f"✅ Saved ₹{amount:.2f} under **{category}**")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to save: {e}")

st.divider()
st.caption("Tip: Use descriptions like 'Petrol', 'Groceries', 'Netflix' so your history is readable.")
