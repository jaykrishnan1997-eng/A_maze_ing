from maze_generator import MazeGenerator, verify_coherence

maze = MazeGenerator(50, 50, (0, 0), (4, 4), True, seed=1)
grid = maze.get_grid()
errors = verify_coherence(grid)
print(f"Found {len(errors)} coherence objects")
for e in errors:
    print(e)

# for row in grid:
#     print(row)



maze1 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
maze2 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
print("Identical:", maze1.get_grid() == maze2.get_grid())

maze3 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=99)
print("Different seed differs:", maze1.get_grid() != maze3.get_grid())
