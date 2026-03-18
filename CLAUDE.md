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
  - All documation on the LAP Pipeline can be found in the `docs` directory, specifically:
    - `docs/LAP_SYNTAX_GUIDE.md`: Provides documentation on the syntax of the LAP Pipeline configuration files.
    - `docs/TEMPLATE_USAGE_GUIDE.md`: This repository started as part of a template, and you can see what that state is like.
    - `docs/WORKFLOW_DEVELOPMENT_GUIDE.md`: Our opinionated way of developing LAP Pipelines.
  - There may be other guides in the `context` directory that also might give you insights into specific details about the current repository.
    - Feel free to add other documentation as necessary to that context folder.

## Environment & Tooling
**IMPORTANT:** You are in a mounted environment, so `uv` and normal `python` commands will not work as expected. Please do not run any command that would trigger the virtual envirnoment in this repo otherwise headaches will ensue. Only run such commands if explicictly asked.

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

## Keep CLAUDE.md Updated
Upon finishing implementation on a task ensure, CLAUDE.md is updated in the appropriate way so that future agents know what is going on in this project.

## Dependencies
- Default managers: `uv` or `pip` with `pyproject.toml` and PEP 621.
- If you require a new dependency that is not installed or seen in the `pyproject.toml` or `requirements.txt`, ask the user to install for you as you are in a mounted environment! Once users says they've installed then proceed with additonal implementation.
- **Broad Cluster Note:** PyTorch and packages requiring pre-built binaries (e.g. sentence-transformers) may not work when distributed across cluster nodes running RedHat 7. They may work on the local VM but fail on worker nodes. Consider external service APIs or RedHat 7-compatible wheels for such dependencies.

## Configuration & Secrets
- Load configuration from environment variables. Provide sane defaults in dev.
- Never commit secrets. Use `.env` for local dev only and add `.env` to `.gitignore`.
- Provide `pydantic-settings` or `dynaconf` for typed config if complexity grows.

## Testing & Reliability
- All testing will be handled by the developer, because you are in this mounted environment. Further, this pipelining generally doesn't require unittesting because we are doing research here which is already an iterative process.

## Quality Gates
I wish we could do static checks automatically, but since we are in a mounted environment we can't instead, provide the following to the user:
- Once your implementation is complete, provide the static type checks that should be run and prepare to recieve those error outputs.
- Prefer `mypy` and `ruff` checks as those are what I have installed on our cluster.

## Logging, Errors, Observability
- Use stdlib `logging` with structured context or `structlog` if needed.
- Never swallow exceptions silently. Wrap external I/O with clear error messages.
- For libraries, raise typed exceptions. For services, map to proper HTTP status codes.
- Add minimal metrics hooks where relevant (timings, counts, errors).

## Style & Conventions
- Python 3.9 unless project says otherwise.
- Follow PEP 8, use type hints everywhere.
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
