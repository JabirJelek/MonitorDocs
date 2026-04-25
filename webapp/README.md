# MonitorDocs FastAPI Webapp

This is a minimal FastAPI scaffold for storing agent progress in a local SQLite database.


Quick start (Windows PowerShell):

From the project root (`MonitorDocs/`) — recommended:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r webapp/requirements.txt
# run from project root (helper present):
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively, run from the `webapp/` folder directly:

```powershell
cd webapp
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You can also run without the top-level helper by pointing to the module path:

```powershell
uvicorn webapp.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `GET /` — health check
- `POST /progress` — create a progress entry (JSON body)
- `GET /progress` — list entries
- `GET /progress/{id}` — fetch entry by id

The SQLite file is created at `MonitorDocs/agents.db`.

Frontend (landing page)
- The modular landing page is available at `/landing` and static assets under `/static/`.
- From project root run:

```powershell
uvicorn webapp.main:app --reload --host 0.0.0.0 --port 8000
# then open http://127.0.0.1:8000/landing
```

Frontend smoke tests
- A lightweight smoke test that requests `/landing` is present in `webapp/tests/test_frontend_smoke.py`.
- Run all webapp tests with:

```powershell
pytest -q webapp/tests
```
