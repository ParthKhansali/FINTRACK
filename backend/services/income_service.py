# backend/services/income_service.py
from db_config import get_connection

def fetch_income_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT category, COALESCE(SUM(amount), 0) AS total
        FROM income
        WHERE user_id=%s
        GROUP BY category
        ORDER BY total DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fetch_monthly_income(user_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT DATE_FORMAT(date, '%b') AS month, SUM(amount) AS income
        FROM income
        WHERE user_id=%s AND YEAR(date) = YEAR(CURDATE())
        GROUP BY MONTH(date)
        ORDER BY MONTH(date)
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
