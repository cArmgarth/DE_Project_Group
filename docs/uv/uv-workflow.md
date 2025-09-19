# OBS! ChatGPT blir ibland lite förvirrad, så några av dessa kommandon är lite knasiga. Ska försöka rensa upp i dem, men något fel kan förekomma vad gäller olika flaggor.

# uv workspace quick reference (monorepo: fetchers + models + frontend)

_Last updated: 2025-09-19_

This repo uses a **uv workspace**: multiple packages (fetchers, models, frontend) in one repo that share **one lockfile** and usually **one virtual environment** at the workspace root.

---

## Glossary

- **Workspace**: collection of packages managed together with a single `uv.lock`.
- **Member**: a package (has its own `pyproject.toml`) listed in the root’s `[tool.uv.workspace].members`.

---

## Directory layout (example)

```
.
├── pyproject.toml                # Workspace root (may host your FastAPI app)
├── uv.lock
├── fetchers/
│   ├── reddit_api/
│   │   ├── pyproject.toml
│   │   └── src/reddit_api/...
│   └── twitter_api/
│       ├── pyproject.toml
│       └── src/twitter_api/...
├── models/
│   └── my_model/
│       ├── pyproject.toml
│       └── src/my_model/...
└── frontend/
    ├── pyproject.toml
    └── streamlit_app.py
```

Root `pyproject.toml` (snippet):

```toml
[project]
name = "root-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = [
  "fetchers/*",
  "models/*",
  "frontend",
]
```

> **Note:** The table is `[tool.uv.workspace]` (singular). Using `[tool.uv.workspaces]` is invalid.

---

## Creating members

From the repo root:

```bash
uv init fetchers/reddit_api
uv init models/my_model
uv init frontend
```

You can also `mkdir` + `cd` into a folder and run `uv init`; if a parent already has a `pyproject.toml`, uv treats it as part of that workspace automatically (unless you pass `--no-workspace`).

---

## Adding & removing dependencies

**Best practice:** run these commands **inside the target member directory**.

```bash
# add to root project
cd /path/to/repo
uv add fastapi uvicorn

# add to a member
cd fetchers/reddit_api
uv add httpx pydantic

# remove from a member
cd fetchers/reddit_api
uv remove pydantic
```

### Importing from `requirements.txt` (migration)
```bash
cd fetchers/reddit_api
uv add -r requirements.txt
```

> Advanced (no `cd`): you can target a directory with the global `--project` option:
> `uv --project fetchers/reddit_api add httpx` (same for `remove`, `run`, `lock`, etc.).

---

## Syncing (installing) dependencies

- **Whole workspace** (from root):
  ```bash
  uv sync
  ```

- **Just one member’s declared deps** (from **any** directory):
  ```bash
  uv sync --package reddit_api
  ```
  > `reddit_api` here is the member’s `project.name` string from its `pyproject.toml`.

Useful flags for CI/Docker:
```bash
uv sync --package reddit_api --no-install-local --frozen
uv sync --package reddit_api --frozen
```

---

## Running commands

- **Inside a member (simple & recommended):**
  ```bash
  cd frontend
  uv run streamlit run streamlit_app.py

  cd fetchers/reddit_api
  uv run python -m reddit_api.cli  # example
  ```

- **From root, without cd (two options):**
  - Use the global `--project` to point at the member directory:
    ```bash
    uv run --project frontend -- streamlit run streamlit_app.py
    uv run --project fetchers/reddit_api -- python -m reddit_api.cli
    ```
  - Or use the workspace-aware switch (also valid):
    ```bash
    uv run --package reddit_api -- python -m reddit_api.cli
    uv run --package frontend -- streamlit run streamlit_app.py
    ```

> Tip: Put `--` before your program’s args so uv doesn’t parse them.

---

## Locking & exporting

- Update the **workspace** lockfile:
  ```bash
  uv lock
  ```

- Export requirements for a **single member** (helpful when another system expects `requirements.txt`):
  ```bash
  uv export --package reddit_api > requirements.txt
  ```

- Export for the **entire workspace**:
  ```bash
  uv export --all-packages > requirements.txt
  ```

---

## Workspace configuration checklist

- Root `pyproject.toml`:
  - Has `[tool.uv.workspace].members` listing all subprojects (globs OK).
  - Each listed directory contains a valid `pyproject.toml`.

- Each member’s `pyproject.toml`:
  - Has a unique `[project].name` (this is what `--package` targets).
  - Uses `src/` layout for libraries (`uv init --lib` creates it).

---

## Common pitfalls

- **Using `-p <path>`** with modern uv commands — that flag no longer means “project path”.
- **Expecting per-member venvs** — a workspace shares **one** `.venv` at the root by default.
- **Forgetting `--`** before app args with `uv run`.

---

## Quick recipes

### Migrate a fetcher that has `requirements.txt`
```bash
uv init fetchers/reddit_api --lib
cd fetchers/reddit_api
uv add -r requirements.txt
uv sync --package reddit_api
```

### Start a Streamlit frontend
```bash
uv init frontend --app
cd frontend
uv add streamlit
uv run streamlit run streamlit_app.py
```

### Run the FastAPI app at root
```bash
cd /path/to/repo
uv add fastapi uvicorn
uv run -- uvicorn app.main:app --reload
```
