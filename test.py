# from mazegen import MazeGenerator
# from mazegen.maze_generator import count_open_connections

# maze = MazeGenerator(15, 15, (4, 1), (13, 5), False, seed=42)
# grid = maze._get_grid()

# # count reachable cells (total minus 42-pattern exclusions)
# excluded = maze._forty_two_cells()
# reachable_cells = 15 * 15 - len(excluded)

# connections = count_open_connections(grid)
# print(f"Reachable cells: {reachable_cells}")
# print(f"Open connections: {connections}")
# print(f"Expected for perfect (tree): {reachable_cells - 1}")
# print(f"Has a loop: {connections > reachable_cells - 1}")

from mazegen import MazeGenerator
from mazegen.maze_generator import count_open_connections

maze = MazeGenerator(15, 15, (4, 1), (13, 5), False, seed=42)
grid = maze._get_grid()
path_cells = maze._path_cell_ids()
print(f"Path cells: {len(path_cells)}")