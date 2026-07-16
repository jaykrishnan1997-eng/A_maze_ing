*This project has been created as part of the 42 curriculum by jkrishna, icorrale.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator that reads a configuration file, generates a maze (optionally a *perfect* maze, with exactly one path between entry and exit), writes it to a file using a hexadecimal wall encoding, and displays it visually with an interactive menu.

The project is split into two reusable pieces:

- **`mazegen`** — a standalone, pip-installable package containing the `MazeGenerator` class: maze generation (Kruskal's algorithm), wall-coherence enforcement, the "42" pattern, a corridor-width constraint, and a BFS _solver.
- **`a_maze_ing.py`** — the main entrypoint, tying together config parsing, maze generation, output writing, and terminal display.

## Instructions

### Requirements

- Python 3.10+
- `pip` (or `uv`/`pipx`) for installing the `mazegen` package

### Install

```bash
make install
```

This installs the local `mazegen` package (built from `pyproject.toml`) so it can be imported by `a_maze_ing.py`.

### Run

```bash
make run
```

which is equivalent to:

```bash
python3 a_maze_ing.py config.txt
```

`config.txt` is the default configuration file included in this repository. Any other config file can be passed instead:

```bash
python3 a_maze_ing.py my_other_config.txt
```

### Debug

```bash
make debug
```

Runs the program under Python's built-in debugger (`pdb`).

### Lint

```bash
make lint          # flake8 + mypy with the required flags
make lint-strict    # flake8 + mypy --strict
```

Both `flake8` and `mypy` are configured to skip virtual environments (`.venv`/`venv`), regardless of which naming convention is in use:

- `flake8` is passed `--exclude=.venv,venv` directly on the command line.
- `mypy` reads its `exclude` setting from `pyproject.toml` (`[tool.mypy]`), since it does not accept exclusion patterns as CLI flags in the same way.

### Clean

```bash
make clean
```

Removes build/lint artifacts anywhere in the project tree:

- `__pycache__` directories (found recursively, so this also covers subpackages like `mazegen`)
- `.mypy_cache` directories (found recursively, for the same reason)
- `*.pyc` files
- `.pytest_cache`
- the generated `maze.txt` output file

```bash
make fclean
```

Runs `make clean` and additionally removes packaging/build artifacts and any virtual environment:

- `build/`, `dist/`, `*.egg-info`
- `.venv/`, `venv/`

### Building the `mazegen` package from source

The `mazegen` package is distributed as a wheel (`mazegen-*-py3-none-any.whl`) at the root of this repository. To rebuild it from source:

```bash
python3 -m pip install --user build
python3 -m build
```

This produces `dist/mazegen-1.0.0-py3-none-any.whl` and `dist/mazegen-1.0.0.tar.gz`.

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line. Lines starting with `#` are treated as comments and ignored.

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width (number of cells) | `WIDTH=20` |
| `HEIGHT` | Maze height (number of cells) | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (`x,y`) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (`x,y`) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether the maze must be perfect (`True`/`False`) | `PERFECT=True` |
| `SEED` | *(optional)* Seed for reproducible generation | `SEED=42` |

A default `config.txt` is included at the root of the repository.

## Maze generation algorithm

**Algorithm used: Kruskal's algorithm**, via a `UnionFind` (disjoint-set) data structure with path compression and union by rank.

### Why Kruskal's

- It builds a maze as a **minimum spanning tree** over the grid's cells, which directly matches the subject's definition of a *perfect* maze (a spanning tree = exactly one path between any two cells).
- It naturally produces a more uniformly random maze than simpler approaches (e.g. Binary Tree), avoiding the strong directional bias those algorithms introduce.
- Excluding cells from consideration (used for the "42" pattern, see below) is straightforward: cells simply never enter the candidate wall list, so Kruskal's builds a valid spanning tree *around* them automatically, with no risk of accidentally disconnecting the rest of the maze.
- Rejected walls (walls Kruskal's declined because both sides were already connected) are a natural byproduct of the algorithm and are reused directly to implement `PERFECT=False` (adding a single loop) without any extra computation.

### Key implementation details

- **Wall encoding**: each cell is stored as a 4-bit integer (`bit0=N, bit1=E, bit2=S, bit3=W`; `1` = wall closed).
- **Wall coherence**: a wall between two neighboring cells is only ever cleared on both sides simultaneously, guaranteeing neighboring cells always agree on a shared wall.
- **"42" pattern**: a fixed set of cell coordinates (offset from the maze's midpoint) is computed *before* generation and excluded from the candidate wall list, so Kruskal's naturally leaves those cells fully closed and disconnected from the rest of the maze — satisfying the subject's exception to full connectivity.
- **Corridor-width constraint**: proven structurally impossible to violate under `PERFECT=True` — a fully-open 3×3 block would require 12 internal open walls, but a spanning tree over 9 cells can have at most 8 edges (no cycles), so Kruskal's cannot produce one. Verified programmatically against generated mazes.
- **Entry/exit doorways**: after generation, the outward-facing wall of the entry and exit cells is opened (with a fixed preference for North/South over East/West at corners).
- **`PERFECT=False`**: one rejected wall is randomly selected (with the same seed, for reproducibility) and opened, introducing exactly one loop.
- **_solver**: a breadth-first search (BFS) over the generated grid returns the shortest entry→exit path as a string of `N`/`E`/`S`/`W` characters.

## Reusable module

The `mazegen` package (`mazegen/__init__.py`, `mazegen/maze_generator.py`) is fully standalone and reusable in other projects.

### Installing

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    entry_coord=(0, 0),
    exit_coord=(19, 14),
    perfect=True,
    seed=42,
)

grid = maze._get_grid()      # list[list[int]], one 4-bit wall value per cell
path = maze._solve()         # list[str], shortest path as N/E/S/W moves
```

### Custom parameters

- `width`, `height` — maze dimensions
- `entry_coord`, `exit_coord` — `(x, y)` tuples
- `perfect` — `True` for a spanning-tree maze (one path), `False` to add one extra loop
- `seed` — any integer for reproducible generation, or `None` for non-deterministic generation

### Accessing the structure and a solution

- `_get_grid()` returns a **copy** of the internal grid (`list[list[int]]`, row-major, one 4-bit wall value per cell) — safe to modify without affecting the generator.
- `_solve()` returns the shortest path from entry to exit as a list of single-character direction strings (`"N"`, `"E"`, `"S"`, `"W"`).

## Team and project management

| | jkrishna | icorrale |
|---|---|---|
| Role | `MazeGenerator` core: Kruskal's algorithm, Union-Find, wall coherence, "42" pattern, corridor-width validation, BFS _solver, packaging | Config file parsing, output file writing, ASCII terminal display and interactive menu |

### Planning

Work was split along the same lines as prior collaborative C projects: one person owns the core algorithm as a self-contained module, the other owns I/O and presentation. An `INTERFACES.md` contract was written up front, defining the config shape, the `MazeGenerator` constructor signature, the grid data format, and error-handling ownership, before either side wrote production code.

### What worked well

- Freezing the data contract (grid format, constructor signature) before writing generation code meant the two sides could be built and tested largely independently.
- Building small, standalone verification tools alongside the generator (wall-coherence checker, 3×3 open-block checker) caught real bugs early and gave concrete, reproducible proof that constraints were actually satisfied — rather than relying on visual inspection alone.

### What could be improved

- The integration checkpoint happened later than planned; a mismatch between the subject's output-file format (one blank line before entry/exit/path) and the display code's expected format (two blank lines) was only caught once real integration testing began, rather than at the "done enough to integrate" checkpoint described in `INTERFACES.md`.
- The `parsing/` and `display/` module split agreed on in `INTERFACES.md` was not followed in practice — both ended up combined into `a_maze_ing.py`.

### Tools used

- `flake8` and `mypy` (with the subject's required flags) for linting and static type checking
- `python -m build` for producing the installable `mazegen` wheel
- Manual verification scripts (wall-coherence checker, 3×3 open-area checker, reproducibility tests) built alongside the generator

## Resources

- [Kruskal's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [Disjoint-set (Union-Find) data structure — Wikipedia](https://en.wikipedia.org/wiki/Disjoint-set_data_structure)
- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)

### AI usage

Claude (Anthropic) was used throughout development of the `mazegen` package as a tutor rather than a code generator: explaining Union-Find and Kruskal's algorithm conceptually before any code was written, reviewing hand-written code line by line to catch bugs (rather than rewriting it), and helping design the "42"-pattern exclusion approach (excluding pattern cells from Kruskal's candidate wall list up front, rather than sealing them after generation and risking a disconnected maze). Claude was also used to help draft the `pyproject.toml` packaging configuration (including the `mypy` exclusion for virtual environments), debug a cross-module output-format mismatch between the maze generator and the display code during integration testing, and interpret a `valgrind` memcheck log to confirm the interpreter's "still reachable" startup allocations were not project-code leaks. All resulting code was written and understood by the author, in line with the subject's AI usage guidance.
