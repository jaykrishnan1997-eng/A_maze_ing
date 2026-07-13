import sys
import time


def htod(h: str):
    if (type(h) is str and h.capitalize() in ['A', 'B', 'C', 'D', 'E', 'F']):
        return (10 + ['A', 'B', 'C', 'D', 'E', 'F'].index(h.capitalize()))
    return (int(h))


# its actually compute_open, i'll fix the names later
def compute_closed(cell: int) -> tuple:
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


def print_maze(maze: str):
    CLEAR_SCREEN_ONE = "\x1b[H"
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
    PATH_ONE = '\x1b[94m██\x1b[0m'
    PATH_TWO = '\x1b[1;96m██\x1b[0m'
    PATH = PATH_TWO
    FT_ONE = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    FT_TWO = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    FT_THREE = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    BLINK_FT = '\x1b[5m\x1b[94m██\x1b[25m\x1b[0m'
    FTT = '\x1b[38;5;117m██\x1b[0m'
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

    def blank_maze(height: int, width: int):
        mazed: list[list[str]] = []
        for i in range((2 * height) + 1):
            mazed.append([])
            for j in range((2 * width) + 1):
                if (i % 2 == 0 or j % 2 == 0):
                    mazed[i].append([WALLS])
                else:
                    if (((i - 1) / 2, (j - 1) / 2) == entry):
                        mazed[i].append([ENTRY])
                    elif (((i - 1) / 2, (j - 1) / 2) == exit):
                        mazed[i].append([EXIT])
                    else:
                        mazed[i].append([CELL])
        return mazed

    def draw(mazed: list[list[str]], msg: str = ""):
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

    def move(mazed: list[list[str]], entry: list[int], path: str,
             sleep: float = 0.01):
        if (len(path) == 0):
            return
        if (len(path) == 1):
            entry[0] = entry[0] - 1 if path == 'N' else entry[0]
            entry[1] = entry[1] - 1 if path == 'W' else entry[1]
            entry[0] = entry[0] + 1 if path == 'S' else entry[0]
            entry[1] = entry[1] + 1 if path == 'E' else entry[1]
            mazed[(entry[0] * 2) + 1][(entry[1] * 2) + 1] = [PATH]
            draw(mazed, msg=PRINTING_PATH_ASCII)
            time.sleep(sleep)
            return entry
        if (len(path) > 1):
            move(mazed, move(mazed, entry, path[0]), path[1:])

    def is_pathed(mazed: list[list[str]]):
        for line in mazed:
            for cell in line:
                if cell[0] == PATH:
                    return True
        return False

    def unpath(mazed: list[list[str]], replace: tuple = (PATH, CELL),
               sleep: float = 0.01, msg: str = HIDING_PATH_ASCII):
        for line in mazed:
            for cell in line:
                if cell[0] == replace[0]:
                    cell[0] = replace[1]
            draw(mazed, msg)
            time.sleep(sleep)

    def apply_walls(mazed: list[list[str]], lines: list[str], entry: tuple[int], exit: tuple[int]):
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
                        mazed[mline][mcell - 1] = [WALLS if not ft else BLINK_FT]
                    elif (o == 4):
                        mazed[mline + 1][mcell] = [WALLS]
                    elif (o == 2):
                        mazed[mline][mcell + 1] = [WALLS]
                    elif (o == 1):
                        mazed[mline - 1][mcell] = [WALLS]

    # preliminary parsing of ooutput file
    splat: list[str] = maze.split("\n\n")
    hex: str = splat[0]
    resplat = splat[1].split("\n")
    entry: tuple[int] = tuple([int(x) for x in resplat[0].split(",")])
    exit: tuple[int] = tuple([int(x) for x in resplat[1].split(",")])
    path: str = splat[2].split('\n')[0]
    lines: list[str] = hex.split('\n')
    width: int = len(lines[0])
    height: int = len(lines)
    # Making an array of arrays that stores a blank maze of desired
    # dimensions
    mazed: list[list[str]] = blank_maze(height, width)
    # Applying walls from output file to the blank maze
    apply_walls(mazed, lines, entry, exit)
    command = ""
    while (command.capitalize() != "Q" and command != '5'):
        draw(mazed)
        print("\n\t1:\tnew maze\t\t"
              "\t2:\tprint path / hide path\n\t3:\tchange walls"
              "\t\t\t\n\n5/Q:\tquit\n")
        print(WALLS * len(mazed[0]))
        command = input()
        # PRINT/HIDE PATH
        if command == '2' or command.capitalize() == "P":
            if not is_pathed(mazed):
                move(mazed, list(entry), path)
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


def config_parse(config: str):
    rconfig = {}
    lines: list[str] = config.split("\n")
    lines = [line for line in lines if not line.startswith("#")]
    mandatory = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    if (not set(mandatory) <= {line.split("=")[0] for line in lines}):
        raise Exception(
            f"Missing mandatory fields in '{sys.argv[1]}':\n"
            f"{set(mandatory) - {line.split('=')[0] for line in lines}}")
    rconfig['WIDTH'], rconfig['HEIGHT'] = [
        int(v) for v in
        [line.split("=")[1] for line in lines
         if line.split("=")[0] in mandatory[:2]]]
    rconfig['ENTRY'], rconfig['EXIT'] = [
        (int(x), int(y)) for x, y in
        [line.split("=")[1].split(",")
         for line in lines if line.split("=")[0] in mandatory[2:4]]]
    rconfig['OUTPUT_FILE'] = [
        x for x in
        [line.split("=")[1] for line in lines if
         line.split("=")[0] == mandatory[4]]]
    rconfig['PERFECT'] = [
        x.capitalize() for x in
        [line.split("=")[1] for line in lines
         if line.split("=")[0] == mandatory[5]]
        if x.capitalize() == "true".capitalize() or
        x.capitalize == "false".capitalize() or
        x in (0, 1)]
    return (rconfig)


def main():
    if (len(sys.argv) != 2):
        print("\x1b[41mUsage: python3 a-maze-ing.py config.txt")
        exit(1)
    config: str
    pconfig: dict
    try:
        with open(sys.argv[1]) as file:
            config = file.read()
            pconfig = config_parse(config)
            print(pconfig)  # fully parsed config for Jay
    except Exception as e:
        print(e)
        exit(1)
    # with open("output_test_5x5.txt") as file:
    with open("output_25x20.txt") as file:
        print_maze(file.read())


if __name__ == "__main__":
    main()
