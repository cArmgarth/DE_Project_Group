# Project Workflow with `uv` and Workspaces

This document describes how we organize our project using [`uv`](https://github.com/astral-sh/uv) with **workspaces**, so that each component (fetchers, models) can be managed independently but still share a consistent dependency setup.

---

## 📂 Project Structure

```
project-root/
├── pyproject.toml          # workspace root
├── uv.lock                 # shared lockfile across all members
│
├── fetchers/
│   ├── fetcher_a/
│   │   ├── pyproject.toml
│   │   ├── src/fetcher_a/
│   │   │   └── __init__.py
│   │   └── Dockerfile
│   ├── fetcher_b/
│   │   └── ...
│   └── fetcher_c/
│       └── ...
│
├── models/
│   ├── model_x/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── model_y/
│       └── ...
│
└── tests/
```

Each **fetcher** and **model** is its own project (with its own `pyproject.toml` and dependencies), and the root manages them all as a **workspace**.

---

## 🚀 Setting up a new workspace

1. Initialize the root project (once):
   ```bash
   uv init .
   ```

2. Create each member (once per fetcher/model):
   ```bash
   uv init fetchers/fetcher_a
   uv init models/model_x
   ```
   This creates a `pyproject.toml` for each member.

3. Add members to the root `pyproject.toml`:
   ```toml
   [tool.uv.workspace]
   members = [
     "fetchers/fetcher_a",
     "fetchers/fetcher_b",
     "fetchers/fetcher_c",
     "models/model_x",
     "models/model_y",
   ]
   ```

⚠️ **Important:** Running `uv init` inside a subfolder does **not** automatically register it as a workspace member. You must add it manually to `[tool.uv.workspace].members` in the root `pyproject.toml`.

---

## 📦 Managing dependencies

### Migrating from `requirements.txt`
If a member has an existing `requirements.txt`, run:
```bash
uv add -p fetchers/fetcher_a -r fetchers/fetcher_a/requirements.txt
```
This converts it into that member’s `pyproject.toml`.

### Adding new dependencies
To add dependencies to a specific member:
```bash
uv add -p fetchers/fetcher_a requests
uv add -p models/model_x scikit-learn
```

---

## 🔄 Syncing environments

- Install **everything** for all members:
  ```bash
  uv sync
  ```

- Install only for a specific member:
  ```bash
  uv sync -p fetchers/fetcher_a
  ```

- Install for a subset of members:
  ```bash
  uv sync -p fetchers/fetcher_a -p models/model_x
  ```

In all cases, `uv.lock` is updated to keep the whole workspace consistent.

---

## 🐳 Docker usage

Each member (fetcher/model) has its own Dockerfile.  
Inside the Dockerfile for `fetcher_a`, for example, you should run:

```dockerfile
# Install only this member's deps
RUN uv sync -p fetchers/fetcher_a --frozen
```

This ensures the image is reproducible and consistent with the workspace lockfile.

---

## ✅ Summary

- The repo is one **workspace**.  
- Each fetcher/model is a **workspace member**.  
- Use `uv init` in each member folder once.  
- **Always add new members manually** to `[tool.uv.workspace].members` in the root `pyproject.toml`.  
- Dependencies are managed per member, but locked consistently at the root.  
- Use `uv sync` at the root for everything, or `uv sync -p path` for one member.  
- Each member has its own Dockerfile for cloud deployment.
