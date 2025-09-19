# LAP Pipeline Template Development Instructions
Guidelines for assisting with **generic LAP Pipeline Development**. Follow these rules unless a project’s own docs explicitly say otherwise.

## Purpose
Provide consistent, reliable help on LAP projects. Prefer clarity, safety, and maintainability over cleverness.

## Project Awareness & Context
- At the start of each session:
  - Read `PLANNING.md` to understand architecture, goals, style, constraints.
  - Read `TASK.md` for the active task list. If a task isn’t listed, add it with a one-line description and today’s date.
  - Skim `README.md` and `CONTRIBUTING.md` if available for setup and workflow standards.
- Use the project’s Python environment for any commands.
  - Prefer `uv` if present, else a `.venv` with `python -m venv .venv`.
  - Use the pinned Python version stated in `pyproject.toml` or `.tool-versions` or `.python-version`.

## Environment & Tooling
- Activate the environment before running anything.
  - `uv run <cmd>` or `source .venv/bin/activate` then run commands.
- Prefer `pyproject.toml` for tool config. If tools use their own files, keep them in repo root.
- Provide a `requirements.txt` or `uv.lock`/`poetry.lock` if missing and the project needs one.
- Add a `.env.example` and reference `dotenv`/`pydantic-settings` for configuration.

## Code Structure & Modularity
- Keep files under ~500 lines. If approaching the limit, split into modules.
- Organize by feature or responsibility. Common layout:
```
<pkg>/
├── init.py
├── api/ # web or service endpoints
├── core/ # domain logic
├── db/ # models, migrations, repositories
├── services/ # integrations, external APIs
├── utils/ # helpers with no side effects
└── tests/
```
- Prefer explicit, local imports within packages. Avoid deep relative imports that obscure intent.
- Public interfaces:
- Expose minimal, stable APIs via `__all__` or package `__init__.py`.
- Hide internals in private modules when possible.

## Dependencies
- Default managers: `uv` or `pip` with `pyproject.toml` and PEP 621.
- Pin direct deps for apps; allow ranges for libraries using semver.
- Use `pip-compile`, `uv export`, or Poetry to lock reproducible builds if the project is an application.
- Keep transitive size reasonable. Avoid heavy deps when stdlib or small libs suffice.

## Configuration & Secrets
- Load configuration from environment variables. Provide sane defaults in dev.
- Never commit secrets. Use `.env` for local dev only and add `.env` to `.gitignore`.
- Provide `pydantic-settings` or `dynaconf` for typed config if complexity grows.

## Testing & Reliability
- Use Pytest. Mirror `src/<pkg>` structure inside `tests/`.
- For each new function, class, or route add:
- one expected-use test
- one edge case
- one failure case
- Keep tests fast and hermetic. Mock I/O and networks. Use fixture factories.
- Aim for meaningful coverage (suggested floor: 85%). Do not chase 100% blindly.
- Add regression tests when fixing bugs.

## Quality Gates
- Static checks before commit:
- `ruff` for linting
- `black` for formatting
- `mypy` for type checking (at least `--strict` where feasible on leaf modules)
- Add a `pre-commit` config to enforce the above locally and in CI.
- CI must run: install, type-check, lint, test, and build.

## Logging, Errors, Observability
- Use stdlib `logging` with structured context or `structlog` if needed.
- Never swallow exceptions silently. Wrap external I/O with clear error messages.
- For libraries, raise typed exceptions. For services, map to proper HTTP status codes.
- Add minimal metrics hooks where relevant (timings, counts, errors).

## Style & Conventions
- Python 3.10+ unless project says otherwise.
- Follow PEP 8, use type hints everywhere.
- Format with `black`. Organize imports with `ruff --fix`.
- Data validation: prefer `pydantic` or `pydantic-core` for untrusted inputs.
- Web APIs: prefer FastAPI when a web service is required. ORM: SQLAlchemy or SQLModel if applicable.
- Docstrings use Google style:
```python
def example(param1: str) -> str:
    """
    Brief summary.

    Args:
        param1 (str): Description.

    Returns:
        str: Description.
    """
