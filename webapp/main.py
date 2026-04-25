from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Database file may be overridden by MONITORDOCS_DB env var (useful for tests)
DEFAULT_DB = Path(__file__).resolve().parent.parent / "agents.db"
DB_FILE = Path(os.getenv("MONITORDOCS_DB", DEFAULT_DB))
DB_FILE.parent.mkdir(parents=True, exist_ok=True)


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


@app.get("/")
def root():
    return {"status": "ok", "db": str(DB_FILE)}


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
def list_progress():
    conn = get_connection()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM progress ORDER BY id DESC").fetchall()
    result = []
    for r in rows:
        result.append(
            {
                "id": r["id"],
                "date": r["date"],
                "agent_id": r["agent_id"],
                "summary": r["summary"],
                "artifacts": json.loads(r["artifacts"]) if r["artifacts"] else [],
                "tags": json.loads(r["tags"]) if r["tags"] else [],
            }
        )
    conn.close()
    return result


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
