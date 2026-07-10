import sys


def htod(h: str):
    if (type(h) is str and h.capitalize() in ['A', 'B', 'C', 'D', 'E', 'F']):
        return (10 + ['A', 'B', 'C', 'D', 'E', 'F'].index(h.capitalize()))
    return (int(h))


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
    # WALL_COLOR = ''
    # WALL_CHARACTER = ''
    # ENTRY_COLOR = ''
    # ENTRY_CHARACTER = ''
    # EXIT_COLOR = ''
    # EXIT_CHARACTER = ''
    ENTRY = '\x1b[32m██\x1b[0m'
    EXIT = '\x1b[31m██\x1b[0m'
    WALLS = '\x1b[38;2;140;140;140m██\x1b[0m'
    CELL = '██'

    def draw(mazed: list[list[str]]):
        # Actual printing
        for line in mazed:
            for cell in line:
                print(cell[0], end='')
            print()

    def blank_maze(mazed: list[list[str]]):
        pass

    def apply_walls(mazed: list[list[str]], lines: list[str], entry: tuple[int], exit: tuple[int]):
        # this function is only closing non-zero values which prints the
        # correct maze but does not ensure consistency of output
        # so it will always print a correct maze correctly, but it may
        # also print an incorrect maze
        for line in range(0, len(lines)):
            for cell in range(0, len(lines[line - 1])):
                try:
                    closed = compute_closed(15 - htod(lines[line - 1][cell - 1]))
                except Exception:
                    pass
                mline = (line * 2) + 1
                mcell = (cell * 2) + 1
                if ({1, 2, 4, 8} == set(closed)):
                    mazed[mline][mcell] = [WALLS]
                for c in closed:
                    if (c == 1):
                        mazed[mline - 1][mcell] = [CELL]
                    if (c == 2):
                        mazed[mline][mcell + 1] = [CELL]
                    if (c == 4):
                        mazed[mline + 1][mcell] = [CELL]
                    if (c == 8):
                        mazed[mline][mcell - 1] = [CELL]
                for o in ({1, 2, 4, 8} - set(closed)):
                    if (o == 1):
                        mazed[mline - 1][mcell] = [WALLS]
                    if (o == 2):
                        mazed[mline][mcell + 1] = [WALLS]
                    if (o == 4):
                        mazed[mline + 1][mcell] = [WALLS]
                    if (o == 8):
                        mazed[mline][mcell - 1] = [WALLS]

    # preliminary parsing of ooutput file
    splat: list[str] = maze.split("\n\n")
    hex: str = splat[0]
    entry: tuple[int] = tuple([int(x)
                               for x in splat[1].split("\n")[0].split(",")])
    exit: tuple[int] = tuple([int(x)
                              for x in splat[1].split("\n")[1].split(",")])
    lines: list[str] = hex.split('\n')
    width: int = len(lines[0])
    height: int = len(lines)
    mazed: list[str] = []

    # Making an array of arrays that stores a blank maze of desired
    # dimensions
    for i in range((2 * height) + 1):
        mazed.append([])
        for j in range((2 * width) + 1):
            # if (i, j) == entry:
            #     mazed[i].append([f'{ENTRY}'])
            # elif (i, j) == exit:
            #     mazed[i].append([f'{EXIT}'])
            if (i % 2 == 0 or j % 2 == 0):
                mazed[i].append([f"{WALLS}"])
            else:
                if (((i - 1) / 2, (j - 1) / 2) == entry):
                    mazed[i].append([f"{ENTRY}"])
                elif (((i - 1) / 2, (j - 1) / 2) == exit):
                    mazed[i].append([f"{EXIT}"])
                else:
                    mazed[i].append([f"{CELL}"])
    # Applying lines from output file to the blank maze
    apply_walls(mazed, lines, entry, exit)
    # draw maze!!
    draw(mazed)


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
