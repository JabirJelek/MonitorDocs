"""Save a minimal session snapshot to MonitorDocs/agents/knowledge/sessions.

Only a small, curated set of fields is stored to keep records focused and compact.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml  # type: ignore

    _HAS_YAML = True
except Exception:
    _HAS_YAML = False

ALLOWED_KEYS = [
    "session_id",
    "date",
    "participants",
    "summary",
    "actions",
    "files_changed",
    "tags",
]


def _listify(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return parts if parts else None


def save_session(
    data: Dict[str, Any], sessions_dir: Optional[Path] = None, current: bool = False
) -> Path:
    if sessions_dir is None:
        sessions_dir = Path(__file__).resolve().parent / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session: Dict[str, Any] = {}
    for k in ALLOWED_KEYS:
        if k in data and data[k] is not None:
            session[k] = data[k]
    if "summary" not in session or not str(session["summary"]).strip():
        raise ValueError("summary is required")
    if "date" not in session or not session["date"]:
        session["date"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if "session_id" not in session or not session["session_id"]:
        session["session_id"] = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    if current:
        out = sessions_dir / "current-session.yaml"
    else:
        safe_id = "".join(
            c for c in session["session_id"] if c.isalnum() or c in ("-", "_")
        )
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out = sessions_dir / f"{ts}-{safe_id}.yaml"
    if _HAS_YAML:
        with open(out, "w", encoding="utf-8") as f:
            yaml.safe_dump(session, f, sort_keys=False)
    else:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
    return out


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Save minimal session to MonitorDocs/agents/knowledge/sessions"
    )
    p.add_argument("--session-id", "-i", help="session id")
    p.add_argument("--date", "-d", help="ISO date string")
    p.add_argument("--participants", help="comma-separated participants")
    p.add_argument("--summary", "-s", required=True, help="short summary (required)")
    p.add_argument("--actions", help="comma-separated actions")
    p.add_argument("--files-changed", help="comma-separated file paths")
    p.add_argument("--tags", help="comma-separated tags")
    p.add_argument(
        "--current",
        action="store_true",
        help="also write sessions/current-session.yaml (overwrite)",
    )
    return p.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    data = {
        "session_id": args.session_id,
        "date": args.date,
        "participants": _listify(args.participants),
        "summary": args.summary,
        "actions": _listify(args.actions),
        "files_changed": _listify(args.files_changed),
        "tags": _listify(args.tags),
    }
    out = save_session(data, current=args.current)
    print(out)


if __name__ == "__main__":
    main()
