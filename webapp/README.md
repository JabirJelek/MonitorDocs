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
