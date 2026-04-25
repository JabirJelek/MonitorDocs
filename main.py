"""Convenience module to allow running `uvicorn main:app` from the project root.

Usage (from `MonitorDocs/`):
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

This simply re-exports the FastAPI `app` defined in `webapp/main.py`.
"""

from webapp.main import app  # re-export app for uvicorn

__all__ = ["app"]
