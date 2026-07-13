# a-maze-ing — Interfaces & Work Split

This document is the contract between the two of us. Sign off on it before writing generation or parsing code — it's what prevents silent breakage at integration time.

## Role Split

| | You — Algorithm side | Partner — Parsing/IO side |
|---|---|---|
| Core work | `MazeGenerator` class: recursive backtracker, wall coherence, corridor-width check (no 3×3 open areas), 42-pattern injection, seed handling | Config file parsing + validation (mandatory keys, error handling, bad syntax) |
| Also owns | BFS _solver — shortest path + direction-string encoding (stays algorithmic, not bolted onto parsing) | Output file writer (hex grid + entry/exit/path formatting) |
| Also owns | Packaging (`mazegen-*.whl`) | ASCII display + interactive menu (regenerate / show path / colors) |

**Analogy:** same split as push_swap — your partner's parsing didn't need to know how the sort worked, just what valid input looked like and how to hand it off. Same here: your partner doesn't need backtracker internals, just the shape of data coming out of `MazeGenerator`.

### Why this is riskier than push_swap

push_swap's data flow was one-way: parse args → pass array to sort. Here it's **two-way**:

- Your generator produces a grid → partner's writer/display consumes it
- Partner's config values (width, height, entry, exit, seed) feed **into** your generator

Two integration seams instead of one — exactly where things break silently. The mitigations below exist to de-risk that.

## De-risking Integration

1. **Freeze data shapes first.** Write down the exact `Config` fields/types and exactly what `_get_grid()` returns, before either of you codes. Both sign off.
2. **Agree on `MazeGenerator.__init__` now**, even unimplemented — the config parser needs the exact signature to call into.
3. **Partner builds against a stub first.** A fake `MazeGenerator` that returns a hardcoded small grid, so parsing/writing/display can be built and tested without waiting on the real algorithm. This is the actual fix for backloaded integration — decoupling via a stub, not just a written contract.
4. **Integrate early, on a tiny maze.** Plug the real generator into the real writer by day 2–3 with a 5×5 maze — not day 5 with the full thing. Small checks catch shape mismatches while they're cheap to fix.

## The Contract

### 1. Config shape

```python
width: int
height: int
entry: tuple[int, int]
exit: tuple[int, int]
perfect: bool
seed: int | None
output_file: str
```

### 2. `MazeGenerator` constructor

- Exact arguments, order/keyword convention — TBD, agree before coding
- Behavior on invalid input: raise? return `None`? print and exit? — **pick one**

### 3. Grid data format

- `list[list[int]]`, row-major (confirm: row = y, col = x — or the reverse)
- Hex values `0–15`
- Bit → direction mapping (subject fixes this): `bit0=N, bit1=E, bit2=S, bit3=W` — confirm both reading it the same way

### 4. _solver output format

- `_solve()` returns coordinates, **or** the direction string directly? Decide now so the writer doesn't have to guess or convert.

### 5. Error handling ownership

| Failure | Owner |
|---|---|
| Bad config syntax / missing keys | Parser |
| `entry == exit` / impossible params | Generator (raises a specific exception, not a bare crash) |
| Everything else | Main script (catches, prints a clean message) |

Agree on this so you don't both write handlers for the same failure — or neither does.

### 6. "Done enough to integrate" checkpoint

Example: *by day 2, generator returns a valid 5×5 grid even without the 42-pattern; partner builds parser/writer against that stub.*

The checkpoint most teams skip — and the one that actually prevents the day-5 integration surprise.

### 7. Git workflow

- Branch per person
- Who merges, how often `master`/`main` gets synced

Trivial to agree now, painful to sort out mid-merge-conflict.

## Repo Structure

```
a-maze-ing/
├── a_maze_ing.py          # main entrypoint — ties everything together
├── config.txt             # default config file (mandatory, must be in repo)
├── Makefile                # install / run / debug / clean / lint / lint-strict
├── README.md
├── .gitignore
├── pyproject.toml          # build config for the mazegen package
│
├── mazegen/                 # YOUR package — reusable, pip-installable
│   ├── __init__.py          # exposes `from mazegen import MazeGenerator`
│   └── maze_generator.py    # MazeGenerator class: backtracker, 42-pattern, BFS _solve
│
├── parsing/                 # PARTNER's side
│   ├── config_parser.py     # reads config.txt -> validated Config object
│   └── output_writer.py     # writes grid + entry/exit/path to output file
│
├── display/                 # PARTNER's side
│   └── ascii_display.py     # terminal rendering + interactive menu
│
└── tests/                    # not submitted/graded, but useful
    ├── test_maze_generator.py
    └── test_config_parser.py
```
