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
    return app, db_file


def test_tabs_and_filtering(tmp_path: Path):
    app, _ = load_app_with_db(tmp_path)
    with TestClient(app) as client:
        payload1 = {
            "date": "2026-04-25",
            "agent_id": "tab-agent-1",
            "summary": "tab1",
            "artifacts": [],
            "tags": [],
            "tab": "alpha",
        }
        payload2 = {
            "date": "2026-04-25",
            "agent_id": "tab-agent-2",
            "summary": "tab2",
            "artifacts": [],
            "tags": [],
            "tab": "beta",
        }
        r1 = client.post("/progress", json=payload1)
        assert r1.status_code == 201
        id1 = r1.json()["id"]
        r2 = client.post("/progress", json=payload2)
        assert r2.status_code == 201
        _id2 = r2.json()["id"]

        # list tabs
        t = client.get("/tabs")
        assert t.status_code == 200
        tabs = t.json()
        assert "alpha" in tabs and "beta" in tabs

        # filter by tab
        fa = client.get("/progress", params={"tab": "alpha"})
        assert fa.status_code == 200
        data = fa.json()
        assert all(item.get("tab") == "alpha" for item in data)

        # patch change tab
        p = client.patch(f"/progress/{id1}", json={"tab": "gamma"})
        assert p.status_code == 200
        g = client.get(f"/progress/{id1}")
        assert g.status_code == 200
        assert g.json().get("tab") == "gamma"
