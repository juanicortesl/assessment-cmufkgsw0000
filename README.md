# scaffold-python-fastapi

Minimal Python 3.11 + FastAPI + SQLAlchemy + Alembic scaffold for AI-generated assessment repos.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Running

```bash
uvicorn app.main:app --reload
```

## Database migrations

```bash
alembic revision --autogenerate -m "<message>"
alembic upgrade head
```

## Tests

```bash
pytest
```
