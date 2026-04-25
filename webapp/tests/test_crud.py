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


def test_full_crud_cycle(tmp_path: Path):
    app, db_file = load_app_with_db(tmp_path)
    with TestClient(app) as client:
        # health
        r = client.get("/")
        assert r.status_code == 200

        # create
        payload = {
            "date": "2026-04-25",
            "agent_id": "pytest-agent",
            "summary": "create",
            "artifacts": ["a"],
            "tags": ["t"],
        }
        res = client.post("/progress", json=payload)
        assert res.status_code == 200
        pid = res.json()["id"]

        # get
        g = client.get(f"/progress/{pid}")
        assert g.status_code == 200
        assert g.json()["agent_id"] == "pytest-agent"

        # list
        lst = client.get("/progress")
        assert lst.status_code == 200
        assert any(item["id"] == pid for item in lst.json())

        # update
        upd = {
            "date": "2026-04-26",
            "agent_id": "pytest-agent",
            "summary": "updated",
            "artifacts": ["b"],
            "tags": ["u"],
        }
        up = client.put(f"/progress/{pid}", json=upd)
        assert up.status_code == 200
        assert up.json()["id"] == pid

        # verify update
        g2 = client.get(f"/progress/{pid}")
        assert g2.status_code == 200
        assert g2.json()["summary"] == "updated"

        # delete
        d = client.delete(f"/progress/{pid}")
        assert d.status_code == 200
        assert d.json()["deleted"] == pid

        # not found
        g3 = client.get(f"/progress/{pid}")
        assert g3.status_code == 404
