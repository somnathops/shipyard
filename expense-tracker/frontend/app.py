import streamlit as st

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide",
)

st.markdown("""
<style>
/* Sidebar dark gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d1a 0%, #111827 60%, #0d1117 100%);
}
[data-testid="stSidebar"] * {
    color: #cbd5e0 !important;
}
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    border-left: 3px solid #63b3ed;
    background: rgba(99,179,237,0.08);
    color: #63b3ed !important;
}
[data-testid="stSidebarNav"]::before {
    content: "MENU";
    display: block;
    color: #4a5568;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    padding: 1rem 1rem 0.4rem;
}
</style>
""", unsafe_allow_html=True)

pg = st.navigation([
    st.Page("pages/dashboard.py",   title="Dashboard",   icon="🏠"),
    st.Page("pages/add_expense.py", title="Add Expense", icon="➕"),
    st.Page("pages/history.py",     title="History",     icon="📋"),
    st.Page("pages/analytics.py",   title="Analytics",   icon="📊"),
])
pg.run()
