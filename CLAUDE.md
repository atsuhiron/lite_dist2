# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

LiteDist2 is a LAN-only distributed computing library. A **table node** hands out fragments of a large parameter-sweep job to **worker nodes** over HTTP and aggregates their results; a **management node** (any client) registers the job and later retrieves results. See `README.md` for the full user-facing API/schema reference — this file focuses on internals.

## Commands

Uses [uv](https://docs.astral.sh/uv/) (>=0.7) and Python >=3.13. The development environment (`.python-version`) is 3.14; CI runs the gate on {ubuntu, windows} x {3.13, 3.14}, so keep `ruff.toml`'s `target-version` at the *minimum* supported version (`py313`).

```bash
uv sync                                    # install dev environment
uv run ruff format                         # format
uv run ruff check --fix                    # lint (rule set = ALL, see ruff.toml)
uv run ty check                            # type check (astral's `ty`)
uv run pytest                              # run tests
uv run pytest --cov --cov-config=pyproject.toml   # tests with coverage
```

Run the full gate (format + lint + type + test) with `./check.sh` (Unix) or `.\check.bat` (Windows).

Single test / subset:

```bash
uv run pytest tests/value_models/test_point.py                 # one file
uv run pytest tests/value_models/test_point.py::test_name      # one test
uv run pytest -k "jagged"                                       # by keyword
```

Async tests use explicit `@pytest.mark.asyncio` markers (pytest-asyncio strict mode; there is no `asyncio_mode` config and no `conftest.py`).

Start a table node locally: `uv run start-table [-c path/to/table_config.json]`. Runnable end-to-end examples (table + worker in one process) live in `example/` — e.g. `python example/generate_mandelbrot_set.py`.

## Architecture

### Node roles (all HTTP, FastAPI)
- **Table node** — the only stateful server; exactly one per cluster. `table_node_api/` defines the FastAPI `app` (`api.py`), request/response Pydantic models (`table_param.py` / `table_response.py`), and startup (`start_table_api.py`). Does **not** know the actual computation.
- **Worker node** — `worker_node/`. `Worker` loops: reserve a `Trial` → run it via a `TrialRunner` → register the result. Talks to the table node only through `TableNodeClient` (httpx2).
- **Management node** — also just a `TableNodeClient`; registers a `Study` and polls `/study` for the result.

Typical flow: `/study/register` → workers repeatedly `/trial/reserve` + `/trial/register` → management `/study` retrieves the aggregated result.

### Domain aggregate: Curriculum → Study → Trial (`curriculum_models/`)
- `Curriculum` is the entire table-node state: a list of in-flight `Study` plus finished `StudyStorage`. Held as a process-global singleton via `CurriculumProvider` (async `get()` lazy-loads from `curriculum.json`).
- A `Study` owns a `parameter_space`, a `StudyStrategy`, a `SuggestStrategy`, a `TrialTable`, and a `TrialRepository`.
- A `Trial` is a subspace of the study's parameter space assigned to one worker. `TrialTable` tracks reserved/running/done trials and, in `aggregated_parameter_space`, the union of completed subspaces (kept minimal via `simplify`/`remap_space` in `value_models/parameter_aligned_space_helper.py`). Free regions are found with `FlattenSegment` arithmetic in `find_least_division`.

### Domain / Model duality (pervasive pattern)
Behavioral classes are plain Python; their serialized twins are Pydantic `BaseModel`s. Nearly every domain class exposes `to_model()` / `from_model()` (and study registration has extra variants: `*Registry` for input, `*Model` for internal/persisted, `*Storage`/`*Summary` for output). When adding a field to a domain class you must thread it through its model(s) and both converters. `curriculum_models/study_portables.py` holds the study-side models.

### Portable values (`common.py`, `type_definitions.py`)
JSON only carries `bool` or hex strings (`PortableValueType`) so numbers survive across heterogeneous processors; in-memory they are `PrimitiveValueType` (`int|float|bool`). Convert with `numerize`/`portablize` (or `int2hex`/`hex2int`/`float2hex`/`hex2float`). `value_models/` builds parameter spaces from these: `LineSegment` (one axis) → `ParameterAlignedSpace` (hyper-rectangle, the common case) or `ParameterJaggedSpace` (enumerated points); `point.py` holds `ScalarValue`/`VectorValue`. Only the **first** axis may be an infinite half-line, and only when the study strategy is not `all_calculation`.

### Strategy + factory pattern
`study_strategies/` (`all_calculation`, `find_exact`, `minimize`=**not implemented**) and `suggest_strategies/` (`sequential`, `random`=**not implemented**, `designated`=**not implemented**) each have a `base_*`, concrete classes, a `*_factory.py`, and a Pydantic `*Model`. `trial_repositories/` follows the same shape (only `normal` implemented). `match` on the `type` literal, dispatching unimplemented arms to `NotImplementedError` and closing with `case _ as unreachable: assert_never(unreachable)`.

### TrialRunner (`worker_node/trial_runner.py`) — the user extension point
Users subclass one of `AutoMPTrialRunner` (self-managed `multiprocessing.Pool`), `SemiAutoMPTrialRunner` (caller injects a `Pool`/`ProcessPoolExecutor`), or `ManualMPTrialRunner` (implement `batch_func` yourself), implementing `func(self, parameters, *args, **kwargs) -> RawResultType`. `Study.const_param` is delivered into `func` as `kwargs` (see `Worker._step`); read it type-safely with `self.get_typed(key, T, kwargs)`.

### Concurrency & background work
Table-node mutable state is guarded by `threading.Lock` (`Curriculum._lock`, `Study._table_lock`) because FastAPI handlers and background threads touch it concurrently. `start_table_api.start()` spawns two daemon threads for periodic curriculum save and trial-timeout checks, then runs uvicorn.

## Conventions
- Every module uses `from __future__ import annotations`; imports used only for typing go under `if TYPE_CHECKING:`.
- Custom exceptions are `LD2*Error` classes in **`expections.py`** (note the misspelled filename — it is intentional/load-bearing, not `exceptions.py`).
- Ruff selects `ALL`; line length 119, double quotes. Per-directory ignores (tests, `example/`, `docker_example/`, `__init__.py`) live in `ruff.toml` — check there before suppressing a rule inline.
- The `app` `version=` in `table_node_api/api.py` and `version` in `pyproject.toml` are hand-kept in sync on release; update `CHANGELOG.md` (Keep a Changelog format) too.
