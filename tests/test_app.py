from datetime import date

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def add(client, **overrides):
    data = {"amount": "12.50", "category": "Food",
            "description": "Lunch", "date": date.today().isoformat()}
    data.update(overrides)
    return client.post("/add", data=data, follow_redirects=True)


def test_home_page_loads(client):
    assert client.get("/").status_code == 200


def test_add_expense_shows_up(client):
    resp = add(client)
    assert b"Expense added" in resp.data
    assert b"Lunch" in resp.data
    assert b"12.50" in resp.data


@pytest.mark.parametrize("bad", [
    {"amount": "abc"}, {"amount": "-5"}, {"amount": "0"},
    {"category": "Nope"}, {"date": "31-12-2025"},
])
def test_invalid_input_rejected(client, bad):
    resp = add(client, **bad)
    assert b"flash error" in resp.data
    assert client.get("/api/expenses").get_json() == []


def test_delete_expense(client):
    add(client)
    expense_id = client.get("/api/expenses").get_json()[0]["id"]
    client.post(f"/delete/{expense_id}")
    assert client.get("/api/expenses").get_json() == []


def test_breakdown_percentages(client):
    add(client, amount="75", category="Food")
    add(client, amount="25", category="Transport")
    html = client.get("/").data.decode()
    assert "75%" in html and "25%" in html
    assert "100.00" in html


def test_month_filter(client):
    add(client, date="2020-01-15", description="old thing")
    assert b"old thing" not in client.get("/").data
    assert b"old thing" in client.get("/?month=2020-01").data


def test_csv_export(client):
    add(client)
    resp = client.get("/export.csv")
    assert resp.mimetype == "text/csv"
    assert resp.data.decode().startswith("date,category,description,amount")
    assert "Lunch" in resp.data.decode()
