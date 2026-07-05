You — Algorithm side

MazeGenerator class: recursive backtracker, wall coherence, corridor-width (no 3x3 open) check, 42-pattern injection, seed handling
BFS solver (shortest path + direction-string encoding) — this is algorithmic too, so it stays with you rather than getting bolted onto the parsing side
Packaging (mazegen-*.whl) — natural fit since it's your module being packaged

Partner — Parsing/IO side

Config file parsing + validation (mandatory keys, error handling, bad syntax)
Output file writer (hex grid + entry/exit/path formatting)
ASCII display + interactive menu (regen/show-path/colors)

This mirrors push_swap almost exactly: your teammate's parsing work in push_swap didn't know how the sort worked, just what valid input looked like and how to hand it off cleanly — same here, your partner doesn't need to know backtracker internals, just what shape of data comes out of your class.
Where push_swap's split doesn't map perfectly, and why integration is riskier here:
In push_swap, parsing → algorithm was a one-way handoff (parse args, pass array to sort). Here it's two-way: your generator produces a grid → partner's writer/display consumes it, AND your partner's config values (width, height, entry, exit, seed) feed into your generator. That's two integration seams instead of one, which is exactly where things break silently.
To de-risk that, before either of you writes generation or parsing code:

Freeze the data shapes first. Write down (a shared doc, even just a markdown file in the repo) exactly what a Config object looks like (field names, types) and exactly what get_grid() returns (e.g. list[list[int]], hex 0–15, row-major). Both of you sign off before coding.
Agree on the MazeGenerator.__init__ signature now, even before it's implemented — your partner's config parser needs to know exactly what arguments to pass.
Your partner should write against a fake/stub MazeGenerator (returns a hardcoded small grid) for the first day or two, so their parser/writer/display can be built and tested without waiting on your algorithm to be finished. This is the actual fix for the "backloaded integration" problem — decoupling via a stub, not just a written contract.
Integrate early and often, even a rough version — plug your real generator into their real writer on day 2 or 3 with a tiny 5x5 maze, not day 5 with the full thing. Small integration checks catch shape mismatches while they're still cheap to fix.


############################################


Since you're pre-start, here's what you should nail down together before either of you opens an editor:
1. The Config shape
Exact field names and types your partner's parser will produce and hand to your generator. E.g. width: int, height: int, entry: tuple[int,int], exit: tuple[int,int], perfect: bool, seed: int | None, output_file: str. Agree on this now — it's the first handoff point.
2. The MazeGenerator constructor signature
What arguments it takes, in what order/by keyword, and what it does on invalid input (raise? return None? print and exit?). This is the second handoff — your partner's code calls into yours.
3. The grid data format
list[list[int]], row-major (row = y, col = x, or the reverse — pick one and write it down), hex values 0–15, and which bit maps to which direction (subject already fixes this: bit0=N,1=E,2=S,3=W — just confirm you're both reading it the same way).
4. The solver output format
Does solve() return coordinates, or does it return the direction string directly? Decide now so the output writer doesn't have to guess or convert.
5. Error handling contract
Who's responsible for catching what. E.g.: parser catches bad config syntax and missing keys; generator raises a specific exception (not a bare crash) if entry==exit or params are impossible; main script catches everything and prints a clean message. Agree who owns which layer of error handling so you don't both write handlers for the same failure or, worse, neither does.
6. What counts as "done enough to integrate"
Agree on a checkpoint — e.g. "by day 2, I'll have a generator that returns a valid 5x5 grid even if the 42-pattern isn't in yet; you build your parser/writer against that stub." This is the piece most teams skip, and it's the one that actually prevents the day-5 integration surprise.
7. Git workflow
Branch per person, who merges, how often you sync main — trivial to agree on now, painful to figure out mid-project when you're both mid-merge-conflict.
Write these down somewhere in the repo (even a rough INTERFACES.md, like the one I mentioned from another team's project) — not for the grade, but because it's the actual artifact that keeps you both honest about the contract once you're heads-down in your own half.

#######################################

a-maze-ing/
├── a_maze_ing.py          # main entrypoint — ties everything together
├── config.txt             # default config file (mandatory, must be in repo)
├── Makefile               # install / run / debug / clean / lint / lint-strict
├── README.md
├── .gitignore
├── pyproject.toml         # build config for the mazegen package
│
├── mazegen/               # YOUR package — the reusable, pip-installable module
│   ├── __init__.py        # exposes `from mazegen import MazeGenerator`
│   └── maze_generator.py  # MazeGenerator class: backtracker, 42-pattern, BFS solve
│
├── parsing/                # PARTNER's side
│   ├── config_parser.py   # reads config.txt -> validated Config object
│   └── output_writer.py   # writes grid + entry/exit/path to output file
│
├── display/                # PARTNER's side
│   └── ascii_display.py   # terminal rendering + interactive menu
│
└── tests/                  # not submitted/graded, but useful
    ├── test_maze_generator.py
    └── test_config_parser.py