from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://admin:secret@localhost:5432/expenses")

CATEGORIES = ["Food", "Transport", "Shopping", "Health", "Entertainment", "Bills", "Education", "Other"]


def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id        SERIAL PRIMARY KEY,
            amount    DECIMAL(10,2) NOT NULL,
            category  VARCHAR(50)   NOT NULL,
            description TEXT        DEFAULT '',
            date      DATE          NOT NULL DEFAULT CURRENT_DATE,
            created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Expense Tracker API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str = ""
    date: str = ""          # YYYY-MM-DD; defaults to today if blank


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def get_categories():
    return CATEGORIES


@app.post("/expenses", status_code=201)
def add_expense(payload: ExpenseCreate):
    exp_date = payload.date if payload.date else date.today().isoformat()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (amount, category, description, date) VALUES (%s, %s, %s, %s) RETURNING *",
        (payload.amount, payload.category, payload.description, exp_date),
    )
    row = dict(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()
    row["amount"] = float(row["amount"])
    row["date"] = str(row["date"])
    row["created_at"] = str(row["created_at"])
    return row


@app.get("/expenses")
def list_expenses(month: Optional[str] = None, category: Optional[str] = None):
    """month format: YYYY-MM"""
    conn = get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND TO_CHAR(date, 'YYYY-MM') = %s"
        params.append(month)
    if category:
        query += " AND category = %s"
        params.append(category)
    query += " ORDER BY date DESC, id DESC"
    cur.execute(query, params)
    rows = []
    for r in cur.fetchall():
        r = dict(r)
        r["amount"] = float(r["amount"])
        r["date"] = str(r["date"])
        r["created_at"] = str(r["created_at"])
        rows.append(r)
    cur.close()
    conn.close()
    return rows


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=%s RETURNING id", (expense_id,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"deleted": expense_id}


@app.get("/summary")
def get_summary(month: Optional[str] = None):
    """Returns total + breakdown by category for the given month (default: current month)."""
    if not month:
        month = datetime.now().strftime("%Y-%m")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT category, SUM(amount) as total FROM expenses WHERE TO_CHAR(date, 'YYYY-MM')=%s GROUP BY category ORDER BY total DESC",
        (month,),
    )
    by_category = [{"category": r["category"], "total": float(r["total"])} for r in cur.fetchall()]

    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE TO_CHAR(date, 'YYYY-MM')=%s",
        (month,),
    )
    total = float(cur.fetchone()["total"])

    cur.close()
    conn.close()
    return {"month": month, "total": total, "by_category": by_category}


@app.get("/monthly-trend")
def monthly_trend():
    """Last 6 months total spending."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT TO_CHAR(date, 'YYYY-MM') as month, SUM(amount) as total
        FROM expenses
        GROUP BY month
        ORDER BY month ASC
        LIMIT 6
    """)
    rows = [{"month": r["month"], "total": float(r["total"])} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return rows
