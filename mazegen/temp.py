# from maze_generator import MazeGenerator, find_open_3x3_blocks
# from maze_generator import verify_coherence

# maze = MazeGenerator(20, 15, (0, 0), (19, 14), False, seed=None)
# grid = maze.get_grid()

# errors = verify_coherence(grid)
# print(f"Found {len(errors)} coherence objects")
# for e in errors:
#   print(e)

# for row in grid:
#   print(row)


# maze1 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
# maze2 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
# print("Identical:", maze1.get_grid() == maze2.get_grid())

# maze3 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=99)
# print("Different seed differs:", maze1.get_grid() != maze3.get_grid())

# print("Coherence errors:", len(verify_coherence(grid)))
# violations = find_open_3x3_blocks(maze)
# print(f"Found {len(violations)} open 3x3 blocks")
# for v in violations:
#     print(v)

# coherence_errors = verify_coherence(grid)
# print(f"Coherence errors: {len(coherence_errors)}")

# open_blocks = find_open_3x3_blocks(maze)
# print(f"Open 3x3 blocks: {len(open_blocks)}")

# path = maze.solve()
# print(f"Path length: {len(path)}")
# print(f"Path: {''.join(path)}")

# print("Coherence errors:", len(verify_coherence(grid)))
# path = maze.solve()
# print("Path:", "".join(path))


from maze_generator import MazeGenerator

maze1 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=1)
maze2 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=1)

print("Identical grids:", maze1.get_grid() == maze2.get_grid())
print("Path 1:", "".join(maze1.solve()))
print("Path 2:", "".join(maze2.solve()))
