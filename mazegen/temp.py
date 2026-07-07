from maze_generator import MazeGenerator

maze = MazeGenerator(5, 5, (0, 0), (4, 4), True, seed=1)
grid = maze.get_grid()
for row in grid:
    print(row)