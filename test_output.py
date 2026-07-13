# # test_output.py — at repo root
# from mazegen import MazeGenerator


# def write_output(grid, entry, exit, path, filename):
#     with open(filename, "w") as f:
#         for row in grid:
#             f.write("".join(format(cell, "X") for cell in row) + "\n")
#         f.write("\n")
#         f.write(f"{entry[0]},{entry[1]}\n")
#         f.write(f"{exit[0]},{exit[1]}\n")
#         f.write("".join(path) + "\n")


# maze = MazeGenerator(5, 5, (0, 0), (4, 4), True, seed=1)
# grid = maze.get_grid()
# path = maze.solve()
# write_output(grid, (0, 0), (4, 4), path, "test_output.txt")

# with open("test_output.txt") as f:
#     content = f.read()
# print(content)

from mazegen import MazeGenerator


def write_output(grid, entry, exit, path, filename):
    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")


maze = MazeGenerator(20, 20, (0, 0), (19, 14), False, seed=1)
grid = maze.get_grid()
path = maze.solve()
write_output(grid, (0, 0), (19, 14), path, "test_output.txt")

with open("test_output.txt") as f:
    content = f.read()
print(content)

import sys
sys.path.insert(0, ".")
from a_maze_ing import print_maze
print_maze(content)
