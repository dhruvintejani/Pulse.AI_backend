# Pulse AI Backend

FastAPI backend for Pulse AI.

## Run locally

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

API runs at:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/api/v1/health
```

For first local run without MongoDB, set this in `.env`:

```env
SKIP_DATABASE_INIT=true
```

For production, keep:

```env
SKIP_DATABASE_INIT=false
```

## Quality checks

```bash
python -m ruff check .
pytest
```
