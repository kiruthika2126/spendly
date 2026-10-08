import csv
import io
from datetime import date, datetime

from flask import (Blueprint, Response, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)

from .db import get_db

bp = Blueprint("main", __name__)

CATEGORIES = ["Food", "Transport", "Housing", "Entertainment",
              "Health", "Shopping", "Other"]


def parse_expense(form) -> tuple[dict | None, str | None]:
    """Validate form data. Returns (clean_data, error_message)."""
    try:
        amount = round(float(form.get("amount", "")), 2)
    except ValueError:
        return None, "Amount must be a number."
    if amount <= 0:
        return None, "Amount must be greater than zero."

    category = form.get("category", "")
    if category not in CATEGORIES:
        return None, "Please choose a valid category."

    try:
        day = datetime.strptime(form.get("date", ""), "%Y-%m-%d").date()
    except ValueError:
        return None, "Date must look like YYYY-MM-DD."

    description = form.get("description", "").strip()[:200]
    return {"amount": amount, "category": category,
            "description": description, "date": day.isoformat()}, None


def selected_month() -> str:
    month = request.args.get("month", "")
    try:
        datetime.strptime(month, "%Y-%m")
        return month
    except ValueError:
        return date.today().strftime("%Y-%m")


@bp.route("/")
def index():
    db = get_db()
    month = selected_month()
    expenses = db.execute(
        "SELECT * FROM expenses WHERE strftime('%Y-%m', date) = ? "
        "ORDER BY date DESC, id DESC", (month,)).fetchall()
    breakdown = db.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE strftime('%Y-%m', date) = ? GROUP BY category "
        "ORDER BY total DESC", (month,)).fetchall()
    total = sum(row["total"] for row in breakdown)
    bars = [{"category": r["category"], "total": r["total"],
             "percent": round(r["total"] / total * 100) if total else 0}
            for r in breakdown]
    return render_template("index.html", expenses=expenses, bars=bars,
                           total=total, month=month, categories=CATEGORIES,
                           today=date.today().isoformat(),
                           currency=current_app.config["CURRENCY"])


@bp.route("/add", methods=["POST"])
def add():
    data, error = parse_expense(request.form)
    if error:
        flash(error, "error")
        return redirect(url_for("main.index"))
    db = get_db()
    db.execute("INSERT INTO expenses (amount, category, description, date) "
               "VALUES (:amount, :category, :description, :date)", data)
    db.commit()
    flash("Expense added.", "ok")
    return redirect(url_for("main.index", month=data["date"][:7]))


@bp.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id: int):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    flash("Expense deleted.", "ok")
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/export.csv")
def export_csv():
    rows = get_db().execute(
        "SELECT date, category, description, amount FROM expenses "
        "ORDER BY date").fetchall()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "category", "description", "amount"])
    writer.writerows([tuple(r) for r in rows])
    return Response(out.getvalue(), mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=expenses.csv"})


@bp.route("/api/expenses")
def api_expenses():
    rows = get_db().execute(
        "SELECT * FROM expenses ORDER BY date DESC, id DESC").fetchall()
    return jsonify([dict(r) for r in rows])
