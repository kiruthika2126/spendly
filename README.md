# 💸 Spendly

!\[CI](https://github.com/kiruthika2126/spendly/actions/workflows/ci.yml/badge.svg)

A small, self-hosted expense tracker built with **Flask** and **SQLite**.
Log your spending, see where the money goes, and export it whenever you like.

!\[Spendly dashboard](docs/screenshot.png)

## Features

* Add and delete expenses with category, description, and date
* Monthly dashboard with total and per-category breakdown bars
* Month filter
* CSV export (`/export.csv`) and JSON API (`/api/expenses`)
* Input validation, responsive layout, automatic dark mode
* No JavaScript frameworks and no external services
* Tested with `pytest`, CI with GitHub Actions, Docker-ready

## Quick start

```bash
git clone https://github.com/kiruthika2126/spendly.git
cd spendly
python -m venv .venv \&\& source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000

## Run with Docker

```bash
docker build -t spendly .
docker run -p 8000:8000 -v spendly-data:/data spendly
```

Open http://localhost:8000

## Configuration

|Variable|Default|Purpose|
|-|-|-|
|`SPENDLY\_DB`|`spendly.db`|SQLite file path|
|`SPENDLY\_CURRENCY`|`$`|Currency symbol shown in the UI|
|`SECRET\_KEY`|`dev-change-me`|Flask secret (set this in production)|

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Project structure

```
spendly/
├── app/
│   ├── \_\_init\_\_.py      # app factory
│   ├── db.py            # SQLite connection and schema
│   ├── routes.py        # pages, validation, CSV and JSON endpoints
│   ├── templates/
│   └── static/style.css
├── tests/test\_app.py
├── Dockerfile
└── .github/workflows/ci.yml
```

## Roadmap ideas

* Monthly budgets with warnings
* Edit existing expenses
* Recurring expenses
* User accounts

## License

MIT, see [LICENSE](LICENSE).

