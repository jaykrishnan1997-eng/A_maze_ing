import sys
import time
from mazegen import MazeGenerator
# from mazegen.maze_generator import MazeGenerator
from typing import Any


def htod(h: str) -> int:
    """Convert a hexadecimal character into its decimal integer value.

    Supports the hexadecimal digits 0-9 and A-F (case-insensitive).
    Returns the corresponding integer representation.
    """
    if (type(h) is str and h.capitalize() in ['A', 'B', 'C', 'D', 'E', 'F']):
        return (10 + ['A', 'B', 'C', 'D', 'E', 'F'].index(h.capitalize()))
    return (int(h))


# its actually compute_open, i'll fix the names later
def compute_closed(cell: int) -> tuple[int, int, int, int]:
    """Determine the closed walls for a maze cell.

    Decomposes the encoded cell value into the wall bitmasks that
    represent the closed directions (north, east, south, and west).
    Returns the resulting wall values as a tuple.
    """
    fields: list[int] = [0, 8, 4, 2, 1]
    if (cell in fields):
        return (cell, cell, cell, cell)
    else:
        return (f := compute_closed(
            max(list(filter(lambda x: x < cell, fields))))[0],
                s := compute_closed(
                    max(list(filter(lambda x: x <= cell - f, fields))))[0],
                t := compute_closed(
                    max(list(filter(lambda x: x <= cell - f - s, fields))))[0],
                compute_closed(
                    max(list(filter(
                        lambda x: x <= cell - f - s - t, fields))))[0],)


def print_maze(maze: str, pconfig: dict[str, Any]) -> None:
    """Display the generated maze in the terminal.

    Parses the maze data, renders a graphical representation using ANSI
    escape sequences, and provides an interactive interface for
    generating new mazes, displaying the solution path, and changing the
    visual style of the maze.
    """
    # CLEAR_SCREEN_ONE = "\x1b[H"
    CLEAR_SCREEN_TWO = '\x1b[2J\x1b[H'
    CLEAR_SCREEN = CLEAR_SCREEN_TWO
    ENTRY = '\x1b[32m██\x1b[0m'
    EXIT = '\x1b[31m██\x1b[0m'
    WALLS_ONE = '\x1b[38;2;140;140;140m██\x1b[0m'
    WALLS_TWO = '\033[38;5;46m██\x1b[0m'
    WALLS = WALLS_ONE
    CELL_ONE = '██'
    CELL_TWO = '  '
    CELL = CELL_ONE
    # PATH_ONE = '\x1b[94m██\x1b[0m'
    PATH_TWO = '\x1b[1;96m██\x1b[0m'
    PATH = PATH_TWO
    # FT_ONE = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    # FT_TWO = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    # FT_THREE = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    BLINK_FT = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    # FTT = '\x1b[38;5;117m██\x1b[0m'
    PRINTING_PATH_ASCII = r"""
    ██████╗ ██████╗ ██╗███╗   ██╗████████╗██╗███╗   ██╗ ██████╗
    ██╔══██╗██╔══██╗██║████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝
    ██████╔╝██████╔╝██║██╔██╗ ██║   ██║   ██║██╔██╗ ██║██║  ███╗
    ██╔═══╝ ██╔══██╗██║██║╚██╗██║   ██║   ██║██║╚██╗██║██║   ██║
    ██║     ██║  ██║██║██║ ╚████║   ██║   ██║██║ ╚████║╚██████╔╝
    ╚═╝     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝

    ██████╗  █████╗ ████████╗██╗  ██╗
    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
    ██████╔╝███████║   ██║   ███████║
    ██╔═══╝ ██╔══██║   ██║   ██╔══██║
    ██║     ██║  ██║   ██║   ██║  ██║
    ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
    """
    HIDING_PATH_ASCII = r"""
    ██╗  ██╗██╗██████╗ ██╗███╗   ██╗ ██████╗
    ██║  ██║██║██╔══██╗██║████╗  ██║██╔════╝
    ███████║██║██║  ██║██║██╔██╗ ██║██║  ███╗
    ██╔══██║██║██║  ██║██║██║╚██╗██║██║   ██║
    ██║  ██║██║██████╔╝██║██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝

    ██████╗  █████╗ ████████╗██╗  ██╗
    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
    ██████╔╝███████║   ██║   ███████║
    ██╔═══╝ ██╔══██║   ██║   ██╔══██║
    ██║     ██║  ██║   ██║   ██║  ██║
    ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
    """
    CHANGING_WALLS = r"""
     ██████╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗ ██╗███╗   ██╗ ██████╗
    ██╔════╝██║  ██║██╔══██╗████╗  ██║██╔════╝ ██║████╗  ██║██╔════╝
    ██║     ███████║███████║██╔██╗ ██║██║  ███╗██║██╔██╗ ██║██║  ███╗
    ██║     ██╔══██║██╔══██║██║╚██╗██║██║   ██║██║██║╚██╗██║██║   ██║
    ╚██████╗██║  ██║██║  ██║██║ ╚████║╚██████╔╝██║██║ ╚████║╚██████╔╝
     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝

    ██╗    ██╗ █████╗ ██╗     ██╗     ███████╗
    ██║    ██║██╔══██╗██║     ██║     ██╔════╝
    ██║ █╗ ██║███████║██║     ██║     ███████╗
    ██║███╗██║██╔══██║██║     ██║     ╚════██║
    ╚███╔███╔╝██║  ██║███████╗███████╗███████║
     ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝
    """

    def blank_maze(height: int, width: int) -> list[list[list[str]]]:
        """Create an empty maze grid.

        Builds a maze of the requested dimensions containing walls, cells,
        and the configured entry and exit points.
        """
        mazed: list[list[list[str]]] = []
        for i in range((2 * height) + 1):
            mazed.append([])
            for j in range((2 * width) + 1):
                if (i % 2 == 0 or j % 2 == 0):
                    mazed[i].append([WALLS])
                else:
                    if (((j - 1) / 2, (i - 1) / 2) == pconfig["ENTRY"]):
                        mazed[i].append([ENTRY])
                    elif (((j - 1) / 2, (i - 1) / 2) == pconfig["EXIT"]):
                        mazed[i].append([EXIT])
                    else:
                        mazed[i].append([CELL])
        return mazed

    def draw(mazed: list[list[list[str]]], msg: str = "") -> None:
        """Render the current maze state.

        Draws the maze to the terminal, restores the entry and exit markers,
        and optionally displays a status message below the maze.
        """
        mazed[(pconfig["ENTRY"][1] * 2) + 1][
            (pconfig["ENTRY"][0] * 2) + 1] = [ENTRY]
        mazed[(pconfig["EXIT"][1] * 2) + 1][
            (pconfig["EXIT"][0] * 2) + 1] = [EXIT]
        # Actual printing
        print(CLEAR_SCREEN)
        for line in mazed:
            for cell in line:
                print(cell[0], end='')
            print()
        print()
        print(WALLS * len(mazed[0]))
        print(
            "\n" + msg + "\n\n" + WALLS * len(mazed[0])
            ) if msg != "" else None

    def move(mazed: list[list[list[str]]], entry: list[int] | None, path: str,
             sleep: float = 0.01) -> list[int] | None:
        """Animate traversal of the solution path.

        Follows the supplied path from the starting position, updating the
        maze display after each movement to visualize the solution.
        """
        if entry is not None:
            _entry: list[int] = list(entry)
        if (len(path) == 0):
            return []
        if (len(path) == 1 and _entry is not None):
            _entry[1] = _entry[1] - 1 if path == 'N' else _entry[1]
            _entry[0] = _entry[0] - 1 if path == 'W' else _entry[0]
            _entry[1] = _entry[1] + 1 if path == 'S' else _entry[1]
            _entry[0] = _entry[0] + 1 if path == 'E' else _entry[0]
            mazed[(_entry[1] * 2) + 1][(_entry[0] * 2) + 1] = [PATH]

            # Repaint the exit after drawing path
            # mazed[(pconfig["ENTRY"][1])]
            # mazed[(pconfig["EXIT"][1] * 2) + 1][
            #     (pconfig["EXIT"][0] * 2) + 1] = [EXIT]
            draw(mazed, msg=PRINTING_PATH_ASCII)
            time.sleep(sleep)
            return _entry
        if (len(path) > 1):
            move(mazed, move(mazed, _entry, path[0]), path[1:])
        return []

    def is_pathed(mazed: list[list[list[str]]]) -> bool:
        """Check whether the solution path is currently visible.

        Returns:
        True if the maze contains visible path markers, otherwise False.
        """
        for line in mazed:
            for cell in line:
                if cell[0] == PATH:
                    return True
        return False

    def unpath(mazed: list[list[list[str]]],
               replace: tuple[str, str] = (PATH, CELL),
               sleep: float = 0.01, msg: str = HIDING_PATH_ASCII) -> None:
        """Remove or replace the displayed solution path.

        Replaces all path markers with the requested cell representation and
        redraws the maze to update the display.
        """
        for line in mazed:
            for cell in line:
                if cell[0] == replace[0]:
                    cell[0] = replace[1]
            draw(mazed, msg)
            time.sleep(sleep)
        mazed[(pconfig["ENTRY"][1] * 2) + 1][
            (pconfig["ENTRY"][0] * 2) + 1] = [ENTRY]
        # Repaint the exit after drawing path
        mazed[(pconfig["EXIT"][1] * 2) + 1][
            (pconfig["EXIT"][0] * 2) + 1] = [EXIT]

    def apply_walls(
        mazed: list[list[list[str]]], lines: list[str],
        entry: list[int], exit: list[int]
    ) -> None:
        """Apply wall information to the rendered maze.

        Decodes each maze cell and updates the display grid with walls,
        passages, and special markers based on the encoded cell values.
        """
        for line in range(0, len(lines)):
            for cell in range(0, len(lines[0])):
                ft = False
                try:
                    closed = compute_closed(15 - htod(lines[line][cell]))
                except Exception:
                    pass
                mline = (line * 2) + 1
                mcell = (cell * 2) + 1
                for c in closed:
                    if (c == 8):
                        mazed[mline][mcell - 1] = [CELL]
                    elif (c == 4):
                        mazed[mline + 1][mcell] = [CELL]
                    elif (c == 2):
                        mazed[mline][mcell + 1] = [CELL]
                    elif (c == 1):
                        mazed[mline - 1][mcell] = [CELL]
                open = {1, 2, 4, 8} - set(closed)
                if ({1, 2, 4, 8} == open):
                    mazed[mline][mcell] = [BLINK_FT]
                    ft = True
                for o in open:
                    if (o == 8):
                        mazed[mline][mcell - 1] = [
                            WALLS if not ft else BLINK_FT]
                    elif (o == 4):
                        mazed[mline + 1][mcell] = [WALLS]
                    elif (o == 2):
                        mazed[mline][mcell + 1] = [WALLS]
                    elif (o == 1):
                        mazed[mline - 1][mcell] = [WALLS]

    def parse_maze(
        maze: str
    ) -> dict[str, Any]:
        """Parse a maze description.

        Extracts the maze dimensions, wall data, entry and exit coordinates,
        and solution path from the maze file contents and returns them in a
        dictionary.
        """
        # preliminary parsing of output file
        splat: list[str] = maze.split("\n\n")
        hex: str = splat[0]
        lines_after = splat[1].split("\n")
        entry: list[int] = [int(x) for x in lines_after[0].split(",")]
        exit: list[int] = [int(x) for x in lines_after[1].split(",")]
        path: str = lines_after[2]
        lines: list[str] = hex.split('\n')
        width: int = len(lines[0])
        height: int = len(lines)
        return {'HEIGHT': height, 'WIDTH': width, 'ENTRY': entry,
                'EXIT': exit, 'PATH': path, 'LINES': lines}
    # Making an array of arrays that stores a blank maze of desired
    # dimensions
    pmaze = parse_maze(maze)
    mazed: list[list[list[str]]] = blank_maze(pmaze['HEIGHT'], pmaze['WIDTH'])
    # Applying walls from output file to the blank maze
    apply_walls(mazed, pmaze['LINES'], pmaze['ENTRY'], pmaze['EXIT'])
    command = ""
    while (command.capitalize() != "Q" and command != '5'):
        draw(mazed)
        print("\n1:\tnew maze\t\t"
              "2:\tprint path / hide path\n3:\tchange walls"
              "\t\t\t\n\n5/Q:\tquit\n")
        print(WALLS * len(mazed[0]))
        print("\x1b[38;5;117malgorithms:"
              " @jkrishna\ngraphics: @icorrale\x1b[0m")
        command = input()
        perfect_value = pconfig["PERFECT"] == "True"
        if command == '1' or command.capitalize() == 'N':
            m: MazeGenerator = MazeGenerator(
                    pconfig["WIDTH"], pconfig["HEIGHT"],
                    tuple(pconfig["ENTRY"]), tuple(pconfig["EXIT"]),
                    perfect_value,
                    pconfig["SEED"] if pconfig["SEED"] != "0" else None
            )
            grid = m._get_grid()
            path = m._solve()
            _write_output(grid, pconfig["ENTRY"], pconfig["EXIT"],
                          path, pconfig["OUTPUT_FILE"])
            with open(pconfig["OUTPUT_FILE"]) as file:
                pmaze = parse_maze(file.read())
                mazed = blank_maze(pmaze['HEIGHT'], pmaze['WIDTH'])
            apply_walls(mazed, pmaze['LINES'], pmaze['ENTRY'], pmaze['EXIT'])
        # PRINT/HIDE PATH
        if command == '2' or command.capitalize() == "P":
            if not is_pathed(mazed):
                # ent: list[int, int] = list(pmaze["ENTRY"])
                move(mazed, pmaze["ENTRY"], pmaze["PATH"])
            elif is_pathed(mazed):
                unpath(mazed, replace=(PATH, CELL))
        if command == '3':
            if WALLS == WALLS_ONE:
                unpath(mazed, replace=(WALLS_ONE, WALLS_TWO),
                       msg=CHANGING_WALLS, sleep=0.01)
                unpath(mazed, replace=(CELL_ONE, CELL_TWO),
                       msg=CHANGING_WALLS, sleep=0.01)
                WALLS = WALLS_TWO
                CELL = CELL_TWO
            else:
                unpath(mazed, replace=(WALLS_TWO, WALLS_ONE),
                       msg=CHANGING_WALLS, sleep=0.01)
                unpath(mazed, replace=(CELL_TWO, CELL_ONE),
                       msg=CHANGING_WALLS, sleep=0.01)
                WALLS = WALLS_ONE
                CELL = CELL_ONE


def config_parse(
    config: str
) -> dict[str, Any]:
    """Parse and validate the configuration file.

    Reads the required configuration values, converts them to their
    appropriate types, verifies that all mandatory fields are present,
    and returns the parsed configuration as a dictionary.
    """
    rconfig: dict[str, Any] = {}
    lines: list[str] = config.split("\n")
    lines = [line for line in lines if not line.startswith("#")]
    mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                 "OUTPUT_FILE", "PERFECT", "SEED"]
    if (not set(mandatory) <= {line.split("=")[0] for line in lines}):
        exc = f"\x1b[43m\nMissing mandatory fields in '{sys.argv[1]}':\n"
        f"{set(mandatory) - {line.split('=')[0] for line in lines}}\x1b[0m"
        raise Exception(exc)
    rconfig['WIDTH'], rconfig['HEIGHT'] = [
        int(v) for v in
        [line.split("=")[1] for line in lines
         if line.split("=")[0] in mandatory[:2]]]
    rconfig['ENTRY'], rconfig['EXIT'] = [
        [int(x), int(y)] for x, y in
        [line.split("=")[1].split(",")
         for line in lines if line.split("=")[0] in mandatory[2:4]]]
    rconfig['OUTPUT_FILE'] = [
        x for x in
        [line.split("=")[1] for line in lines if
         line.split("=")[0] == mandatory[4]]][0]
    rconfig['PERFECT'] = [
        line.split("=")[1] for line in lines
        if line.split("=")[0] == mandatory[5]
    ][0].capitalize()
    rconfig["SEED"] = str([
        x.split("=")[1] for x in lines if x.split("=")[0] == "SEED"][0])
    return (rconfig)


def _write_output(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path: list[str],
    filename: str,
) -> None:
    """Write the generated maze to an output file.

    Stores the hexadecimal maze representation together with the entry
    point, exit point, and solution path using the project's output
    format.
    """
    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")


def main() -> None:
    """Run the maze generator application.

    Loads the configuration file, generates and solves the maze, writes
    the output file, and launches the interactive terminal viewer.
    """
    if (len(sys.argv) != 2):
        print("\x1b[41mUsage: python3 a-maze-ing.py config.txt")
        exit(1)
    config: str
    pconfig: dict[str, Any]
    try:
        with open(sys.argv[1]) as file:
            config = file.read()
            pconfig = config_parse(config)
            print(pconfig)  # fully parsed config for Jay
    except Exception as e:
        print(e)
        exit(1)
    try:
        perfect_value = pconfig["PERFECT"] == "True"
        maze: MazeGenerator = MazeGenerator(
                pconfig["WIDTH"], pconfig["HEIGHT"],
                tuple(pconfig["ENTRY"]), tuple(pconfig["EXIT"]), perfect_value,
                pconfig["SEED"] if pconfig["SEED"] != '0' else None)
        grid = maze._get_grid()
        path = maze._solve()
    except Exception as e:
        print(f"\x1b[33mERROR[config.txt]: {e}\x1b[0m")
        exit()
    _write_output(grid, tuple(pconfig["ENTRY"]), tuple(pconfig["EXIT"]),
                  path, pconfig["OUTPUT_FILE"])
    with open(pconfig["OUTPUT_FILE"]) as file:
        try:
            print_maze(file.read(), pconfig)
        except Exception:
            print("\x1b[33mERROR[config.txt]: ENTRY and EXIT "
                  "points can't be the same\x1b[0m")


if __name__ == "__main__":
    main()
