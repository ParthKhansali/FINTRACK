# backend/app.py
import io, csv, sys, os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# load .env in backend dir
base_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(base_dir, ".env"))

from services.expense_service import (
    fetch_expense_summary,
    fetch_expense_categories,
    fetch_monthly_series,
    fetch_transactions,
    add_transaction,
)
from services.income_service import fetch_income_categories, fetch_monthly_income

app = Flask(__name__)


CORS(app, supports_credentials=True)

# -------------------------
# Auth — demo simple routes
# -------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "email & password required"}), 400
    # DEMO: accept any credentials
    return jsonify({"ok": True, "email": email})

@app.route("/api/logout", methods=["POST"])
def logout():
    return jsonify({"ok": True})

# -------------------------
# Dashboard
# -------------------------
@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    user_id = request.args.get("user_id", 1)
    try:
        user_id = int(user_id)
    except:
        user_id = 1
    summary = fetch_expense_summary(user_id)
    return jsonify(summary)

# -------------------------
# Charts / data
# -------------------------
@app.route("/api/expenses/categories", methods=["GET"])
def expenses_categories():
    user_id = int(request.args.get("user_id", 1))
    rows = fetch_expense_categories(user_id)
    return jsonify(rows)

@app.route("/api/series/monthly", methods=["GET"])
def series_monthly():
    user_id = int(request.args.get("user_id", 1))
    data = fetch_monthly_series(user_id)
    return jsonify(data)

@app.route("/api/transactions", methods=["GET"])
def api_transactions():
    user_id = int(request.args.get("user_id", 1))
    rows = fetch_transactions(user_id)
    return jsonify(rows)

@app.route("/api/transactions", methods=["POST"])
def api_add_transaction():
    data = request.json or {}
    user_id = int(data.get("user_id", 1))
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category", "Misc")
    date = data.get("date")
    if not description or amount is None or not date:
        return jsonify({"error": "description, amount and date required"}), 400
    add_transaction(user_id, description, amount, category, date)
    return jsonify({"ok": True})

# -------------------------
# Exports
# -------------------------
@app.route("/api/export/transactions.csv", methods=["GET"])
def export_transactions_csv():
    user_id = int(request.args.get("user_id", 1))
    rows = fetch_transactions(user_id, limit=10000)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "description", "category", "amount"])
    for r in rows:
        writer.writerow([r['date'], r['description'], r['category'], r['amount']])
    output.seek(0)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="transactions.csv")

# -------------------------
# Health
# -------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "env": os.getenv("FLASK_ENV", "development")})

# -------------------------
# Run (port via --port=N)
# -------------------------
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    # check cli args for --port=#
    for arg in sys.argv[1:]:
        if arg.startswith("--port="):
            try:
                port = int(arg.split("=", 1)[1])
            except:
                pass
    print(f"🚀 Starting backend on port {port}...")
    app.run(host=os.getenv("FLASK_HOST", "0.0.0.0"), port=port, debug=True)
