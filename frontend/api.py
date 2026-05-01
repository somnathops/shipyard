import os
import requests

BASE = os.environ.get("API_URL", "http://localhost:8000")


def get_categories() -> list:
    r = requests.get(f"{BASE}/categories", timeout=5)
    r.raise_for_status()
    return r.json()


def add_expense(amount: float, category: str, description: str, date: str) -> dict:
    r = requests.post(
        f"{BASE}/expenses",
        json={"amount": amount, "category": category, "description": description, "date": date},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


def list_expenses(month: str = None, category: str = None) -> list:
    params = {}
    if month:
        params["month"] = month
    if category:
        params["category"] = category
    r = requests.get(f"{BASE}/expenses", params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def delete_expense(expense_id: int):
    r = requests.delete(f"{BASE}/expenses/{expense_id}", timeout=5)
    r.raise_for_status()
    return r.json()


def get_summary(month: str = None) -> dict:
    params = {"month": month} if month else {}
    r = requests.get(f"{BASE}/summary", params=params, timeout=5)
    r.raise_for_status()
    return r.json()


def get_monthly_trend() -> list:
    r = requests.get(f"{BASE}/monthly-trend", timeout=5)
    r.raise_for_status()
    return r.json()
