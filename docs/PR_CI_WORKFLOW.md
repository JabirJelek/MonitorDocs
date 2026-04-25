# PR & CI Workflow — MonitorDocs

Purpose
- Show step-by-step how the PR was created, what the CI does, and how to reproduce or debug locally.

Overview
- Repository: `MonitorDocs`
- PR opened: https://github.com/JabirJelek/MonitorDocs/pull/1
- CI workflow file: `.github/workflows/ci.yml` — runs `ruff` and `pytest` on push/PR.

Branching and PR flow
- Branch naming: use `feature/your-desc-<timestamp>` (e.g. `feature/monitordocs-scaffold-20260425T...`).
- Typical steps to create a branch and push:

```bash
git checkout -b feature/your-desc-$(date +%s)
git add -A
git commit -m "feat: short description"
git push -u origin HEAD
```

- Create PR via GitHub UI or `gh` CLI:

```bash
gh pr create --title "Short title" --body "Description" --base main --head feature/your-desc-123
```

Special case: unrelated histories / missing `main`
- If the remote repository had no `main` branch you may need to create one first. In our run we created an initial `main` branch on remote, then created a PR branch by merging `main` into the feature branch (to produce a common history). That produced the PR at the link above.

What the CI does
- Location: `.github/workflows/ci.yml`.
- Steps performed on each push/PR:
  1. Set up Python (3.11)
  2. Install `MonitorDocs/webapp/requirements.txt` and `ruff`
  3. Run `ruff check MonitorDocs/webapp`
  4. Run `pytest -q MonitorDocs/webapp/tests`

Interpreting CI results
- On the PR page, open the **Checks** tab to see `ruff` and `pytest` job runs.
- If `ruff` fails: fix reported styling/type issues locally and push a new commit.
- If `pytest` fails: open the job logs to see failing tests and stack traces; run tests locally to iterate.

Reproducing CI locally
- Create and activate a venv, then install requirements and run the same commands:

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\Activate.ps1 on Windows
pip install -r MonitorDocs/webapp/requirements.txt
pip install ruff
ruff check MonitorDocs/webapp
pytest -q MonitorDocs/webapp/tests
```

Testing the `tab` feature locally
- The API supports a `tab` field for categorising entries. CI includes tests that cover `tab` behaviour (see `webapp/tests/test_tabs.py`).
- Quick curl example to create and verify a tabbed entry:

```bash
curl -X POST http://127.0.0.1:8000/progress \
  -H 'Content-Type: application/json' \
  -d '{"date":"2026-04-25","agent_id":"me","summary":"tab-test","tags":[],"tab":"mytab"}'

curl 'http://127.0.0.1:8000/progress?tab=mytab'
```

Troubleshooting common issues
- "Could not import module 'main'" when running `uvicorn main:app`:
  - Either run `uvicorn webapp.main:app` from the repo root, or run `uvicorn main:app` from the `MonitorDocs/` directory (a top-level `main.py` re-exporting `webapp.main:app` exists).

- Database or file permissions:
  - The service uses a local SQLite DB at `MonitorDocs/agents.db`. Ensure the process user has write permission.

How to update the PR
- Make changes on your feature branch, commit, and push. The PR will update automatically.
- If you need to change the PR base or create a clean history, you can create a new branch from `main`, cherry-pick commits, and open a fresh PR.

Cleaning up local artifacts
- If a temporary worktree was created during maintenance, remove it with:

```bash
git worktree remove ../monitor_worktree_<timestamp>
```

Merging
- After CI passes and reviews are satisfied, merge via GitHub (Squash/Merge or Merge commit as preferred). Then update local `main`:

```bash
git checkout main
git pull origin main
git branch -d feature/your-branch
```

Extras
- Session snapshots and agent notes are stored under `MonitorDocs/agents/knowledge/sessions/`.
- The PR created by the agent in this run: https://github.com/JabirJelek/MonitorDocs/pull/1

If you want, I can also add a short `CONTRIBUTING.md` that contains these commands and a checklist for reviewers.
