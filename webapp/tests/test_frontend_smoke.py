import os
from pathlib import Path
import runpy
from fastapi.testclient import TestClient


def load_app_with_db(tmp_path: Path):
    db_file = tmp_path / "agents.db"
    os.environ["MONITORDOCS_DB"] = str(db_file)
    module_loc = str(Path(__file__).resolve().parents[1] / "main.py")
    module_globals = runpy.run_path(module_loc)
    app = module_globals.get("app")
    return app


def test_landing_served(tmp_path: Path):
    app = load_app_with_db(tmp_path)
    with TestClient(app) as client:
        r = client.get("/landing")
        assert r.status_code == 200
        assert "MonitorDocs" in r.text
