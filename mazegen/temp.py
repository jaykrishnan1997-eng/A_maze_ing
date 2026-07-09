from maze_generator import MazeGenerator, verify_coherence

maze = MazeGenerator(20, 15, (0, 0), (19, 14), True, seed=None)
grid = maze.get_grid()
errors = verify_coherence(grid)
print(f"Found {len(errors)} coherence objects")
for e in errors:
    print(e)

for row in grid:
    print(row)

height = len(grid)
width = len(grid[0])

has_open_room = any(
    maze._has_open_3x3(x, y)
    for x in range(width - 2)
    for y in range(height - 2)
)

if has_open_room:
    print("Jay, what have you done! its broken")
else:
    print("Jay, its done!")

# maze1 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
# maze2 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=7)
# print("Identical:", maze1.get_grid() == maze2.get_grid())

# maze3 = MazeGenerator(10, 10, (0, 0), (9, 9), True, seed=99)
# print("Different seed differs:", maze1.get_grid() != maze3.get_grid())
