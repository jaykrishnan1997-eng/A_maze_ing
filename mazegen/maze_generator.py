class UnionFind:
    def __init__(self, size: int):
        pass

    def find(self, x: int) -> int:
        pass

    def union(self, x: int, y: int) -> bool:
        pass

class MazeGenerator:
    def __init__(self, width: int, height: int, entry_coord: tuple[int, int], exit_coord: tuple[int, int], perfect: bool, seed: int | None):
        self._width = width
        self._height = height
        self._entry_coord = entry_coord
        self._exit_coord = exit_coord
        self._perfect = perfect
        self._seed = seed
        self._grid = [[15] * width for _ in range(height)]
        #actual generation
        
    def get_grid(self) -> list[list[int]]:
        #make a copy of the maze
        return [row[:] for row in self._grid]

maze = MazeGenerator(3, 3, (0, 0), (2, 2), True, None)
grid = maze.get_grid()
grid[0][0] = 99
print(maze.get_grid())