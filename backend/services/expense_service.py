# backend/services/expense_service.py
from db_config import get_connection

def fetch_expense_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
          COALESCE(SUM(amount),0) AS totalBalance,
          COALESCE(SUM(CASE WHEN MONTH(date)=MONTH(CURDATE()) AND amount>=0 THEN amount ELSE 0 END),0) AS monthlyIncome,
          COALESCE(SUM(CASE WHEN MONTH(date)=MONTH(CURDATE()) AND amount<0 THEN ABS(amount) ELSE 0 END),0) AS monthlyExpenses
        FROM expenses
        WHERE user_id=%s
    """, (user_id,))
    row = cursor.fetchone() or {}
    cursor.close()
    conn.close()
    row['remainingBudget'] = row.get('monthlyIncome', 0) - row.get('monthlyExpenses', 0)
    return row

def fetch_expense_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT category, COALESCE(SUM(ABS(amount)), 0) AS total
        FROM expenses
        WHERE user_id=%s AND amount < 0
        GROUP BY category
        ORDER BY total DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fetch_monthly_series(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT MONTH(date) AS m, DATE_FORMAT(date, '%b') AS month,
            SUM(CASE WHEN amount >= 0 THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS expenses
        FROM expenses
        WHERE user_id=%s AND YEAR(date) = YEAR(CURDATE())
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    labels = [r['month'] for r in rows]
    income = [r['income'] for r in rows]
    expenses = [r['expenses'] for r in rows]
    return {"labels": labels, "income": income, "expenses": expenses}

def fetch_transactions(user_id, limit=200):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT date, description, category, amount,
            CASE WHEN amount >= 0 THEN 'Credit' ELSE 'Debit' END AS type
        FROM expenses
        WHERE user_id=%s
        ORDER BY date DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def add_transaction(user_id, description, amount, category, date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, description, amount, category, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, description, amount, category, date))
    conn.commit()
    cursor.close()
    conn.close()
    return True
