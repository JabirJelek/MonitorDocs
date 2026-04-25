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


def test_patch_and_partial_update(tmp_path: Path):
    app, _ = load_app_with_db(tmp_path)
    with TestClient(app) as client:
        payload = {
            "date": "2026-04-25",
            "agent_id": "patch-agent",
            "summary": "orig",
            "artifacts": ["a"],
            "tags": ["x"],
        }
        res = client.post("/progress", json=payload)
        assert res.status_code == 200
        pid = res.json()["id"]

        # partial update: only summary
        patch = {"summary": "patched"}
        p = client.patch(f"/progress/{pid}", json=patch)
        assert p.status_code == 200

        g = client.get(f"/progress/{pid}")
        assert g.status_code == 200
        assert g.json()["summary"] == "patched"


def test_list_filters_and_pagination(tmp_path: Path):
    app, _ = load_app_with_db(tmp_path)
    with TestClient(app) as client:
        # create entries
        for i in range(5):
            payload = {
                "date": f"2026-04-2{i}",
                "agent_id": "agent-a" if i % 2 == 0 else "agent-b",
                "summary": f"s{i}",
                "artifacts": [],
                "tags": ["t1"] if i == 2 else [],
            }
            client.post("/progress", json=payload)

        # filter by agent_id
        r = client.get("/progress", params={"agent_id": "agent-a"})
        assert r.status_code == 200
        data = r.json()
        assert all(item["agent_id"] == "agent-a" for item in data)

        # tag filter
        r2 = client.get("/progress", params={"tag": "t1"})
        assert r2.status_code == 200
        assert any("t1" in item.get("tags", []) for item in r2.json())

        # pagination
        r3 = client.get("/progress", params={"limit": 2, "offset": 0})
        assert r3.status_code == 200
        assert len(r3.json()) == 2
