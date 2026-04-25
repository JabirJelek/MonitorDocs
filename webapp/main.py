from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Database file may be overridden by MONITORDOCS_DB env var (useful for tests)
DEFAULT_DB = Path(__file__).resolve().parent.parent / "agents.db"
DB_FILE = Path(os.getenv("MONITORDOCS_DB", str(DEFAULT_DB)))
DB_FILE.parent.mkdir(parents=True, exist_ok=True)

# Static assets directory (modular landing page files live here)
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        summary TEXT,
        artifacts TEXT,
        tags TEXT
    )
    """
    )
    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="MonitorDocs Agent Progress API", lifespan=lifespan)


class AgentProgress(BaseModel):
    date: str
    agent_id: str
    summary: Optional[str] = ""
    artifacts: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class AgentProgressPatch(BaseModel):
    date: Optional[str] = None
    agent_id: Optional[str] = None
    summary: Optional[str] = None
    artifacts: Optional[List[str]] = None
    tags: Optional[List[str]] = None


@app.get("/")
def root():
    return {"status": "ok", "db": str(DB_FILE)}


@app.get("/landing", include_in_schema=False)
def landing():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path, media_type="text/html")
    return HTMLResponse(
        "<html><body><h1>MonitorDocs</h1><p>Landing page not installed.</p></body></html>",
        media_type="text/html",
    )


@app.get("/static/{path:path}", include_in_schema=False)
def static_files(path: str):
    requested = (STATIC_DIR / path).resolve()
    if not str(requested).startswith(str(STATIC_DIR.resolve())):
        raise HTTPException(status_code=404, detail="Not found")
    if requested.exists():
        return FileResponse(requested)
    raise HTTPException(status_code=404, detail="Not found")


@app.post("/progress")
def create_progress(item: AgentProgress):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO progress (date, agent_id, summary, artifacts, tags) VALUES (?, ?, ?, ?, ?)",
        (
            item.date,
            item.agent_id,
            item.summary,
            json.dumps(item.artifacts),
            json.dumps(item.tags),
        ),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return {"id": new_id}


@app.get("/progress")
def list_progress(
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    agent_id: Optional[str] = None,
    tag: Optional[str] = None,
):
    conn = get_connection()
    c = conn.cursor()
    params = []
    sql = "SELECT * FROM progress"
    if agent_id:
        sql += " WHERE agent_id = ?"
        params.append(agent_id)
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = c.execute(sql, params).fetchall()
    result = []
    for r in rows:
        item = {
            "id": r["id"],
            "date": r["date"],
            "agent_id": r["agent_id"],
            "summary": r["summary"],
            "artifacts": json.loads(r["artifacts"]) if r["artifacts"] else [],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
        }
        # optional tag filtering (simple, done in Python)
        if tag:
            if tag in item["tags"]:
                result.append(item)
        else:
            result.append(item)
    conn.close()
    return result


@app.patch("/progress/{progress_id}")
def patch_progress(progress_id: int, item: AgentProgressPatch):
    conn = get_connection()
    c = conn.cursor()
    r = c.execute("SELECT * FROM progress WHERE id = ?", (progress_id,)).fetchone()
    if not r:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")

    # existing values
    date = r["date"]
    agent_id = r["agent_id"]
    summary = r["summary"]
    artifacts = json.loads(r["artifacts"]) if r["artifacts"] else []
    tags = json.loads(r["tags"]) if r["tags"] else []

    # apply partial updates
    if item.date is not None:
        date = item.date
    if item.agent_id is not None:
        agent_id = item.agent_id
    if item.summary is not None:
        summary = item.summary
    if item.artifacts is not None:
        artifacts = item.artifacts
    if item.tags is not None:
        tags = item.tags

    c.execute(
        "UPDATE progress SET date = ?, agent_id = ?, summary = ?, artifacts = ?, tags = ? WHERE id = ?",
        (date, agent_id, summary, json.dumps(artifacts), json.dumps(tags), progress_id),
    )
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    conn.close()
    return {"id": progress_id}


@app.get("/progress/{progress_id}")
def get_progress(progress_id: int):
    conn = get_connection()
    c = conn.cursor()
    r = c.execute("SELECT * FROM progress WHERE id = ?", (progress_id,)).fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": r["id"],
        "date": r["date"],
        "agent_id": r["agent_id"],
        "summary": r["summary"],
        "artifacts": json.loads(r["artifacts"]) if r["artifacts"] else [],
        "tags": json.loads(r["tags"]) if r["tags"] else [],
    }


@app.put("/progress/{progress_id}")
def update_progress(progress_id: int, item: AgentProgress):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE progress SET date = ?, agent_id = ?, summary = ?, artifacts = ?, tags = ? WHERE id = ?",
        (
            item.date,
            item.agent_id,
            item.summary,
            json.dumps(item.artifacts),
            json.dumps(item.tags),
            progress_id,
        ),
    )
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    conn.close()
    return {"id": progress_id}


@app.delete("/progress/{progress_id}")
def delete_progress(progress_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM progress WHERE id = ?", (progress_id,))
    conn.commit()
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Not found")
    conn.close()
    return {"deleted": progress_id}
