#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   maze_generator.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: jkrishna <jkrishna@student.42.fr>            +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/07 09:19:10 by jkrishna            #+#    #+#            #
#   Updated: 2026/07/13 09:59:44 by jkrishna           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import random
from collections import deque

DIRECTIONS = [
    ("N", 1, (0, -1)),
    ("E", 2, (1, 0)),
    ("S", 4, (0, 1)),
    ("W", 8, (-1, 0)),
]


# x and y are NOT spatial coordinate but are generic cell
# IDs like 0,1,2,.., width * height - 1
class UnionFind:
    def __init__(self, size: int) -> None:
        self._parent = list(range(size))
        #  approximate measure of trees height
        self._rank = size * [0]

    #  find the leader/ root and update the chain and
    #  new nodes root as the leader.
    #  conquer, submit and say u shall praise the lord's name forever
    def find(self, x: int) -> int:
        #  find with path compression
        if self._parent[x] != x:
            #  recursively update all nodes
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    #  merge two branch into one containing both
    def union(self, x: int, y: int) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)

        #  already connected
        if root_x == root_y:
            return False
        #  create union by rank (attach the smaller depth to the tree)
        if self._rank[root_x] < self._rank[root_y]:
            root_x, root_y = root_y, root_x

        self._parent[root_y] = root_x
        #  if same rank, choose any as root and increment rank
        if self._rank[root_x] == self._rank[root_y]:
            self._rank[root_x] += 1
        return True


# Daedalun and Theseus
class MazeGenerator:
    def __init__(
        self, width: int, height: int, entry_coord: tuple[int, int],
        exit_coord: tuple[int, int], perfect: bool, seed: int | None
    ):
        self._width = width
        self._height = height
        self._entry_coord = entry_coord
        self._exit_coord = exit_coord
        self._perfect = perfect
        self._seed = seed
        self._grid = [[15] * width for _ in range(height)]
        removed_walls, rejected_walls = self._run_kruskal()
        loop_walls = self._add_loop(rejected_walls)
        self._apply_walls(removed_walls + loop_walls)
        self._open_entry_exit()

    #  make a copy of the maze
    def get_grid(self) -> list[list[int]]:
        return [row[:] for row in self._grid]

    #  convert grid coordinate to cell ID
    def cell_id(self, x: int, y: int) -> int:
        return (y * self._width) + x

    #  id to coordinate
    def cell_coords(self, id: int) -> tuple[int, int]:
        return (id % self._width, id // self._width)

    #  Candidate wall list
    def build_walls(
        self, excluded: set[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        walls = []
        for y in range(self._height):
            for x in range(self._width):
                # skip cells making 42
                if (x, y) in excluded:
                    continue
                # for the east wall
                if x < self._width - 1 and (x + 1, y) not in excluded:
                    walls.append((self.cell_id(x, y), self.cell_id(x + 1, y)))
                # for the soth wall
                if y < self._height - 1 and (x, y + 1) not in excluded:
                    walls.append((self.cell_id(x, y), self.cell_id(x, y + 1)))
        return walls

    def _run_kruskal(
        self
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        uf = UnionFind(self._width * self._height)
        walls = self.build_walls(self._forty_two_cells())
        rng = random.Random(self._seed)
        rng.shuffle(walls)
        removed_walls = []
        rejected_walls = []
        for a, b in walls:
            if uf.union(a, b):
                removed_walls.append((a, b))
            else:
                rejected_walls.append((a, b))
        return (removed_walls, rejected_walls)

    #  translate removed walls into _grid bitmask:
    def _apply_walls(self, removed_walls: list[tuple[int, int]]) -> None:
        for a, b in removed_walls:
            ax, ay = self.cell_coords(a)
            bx, by = self.cell_coords(b)
            if b - a == 1:
                # a's E wall open and b's W wall open
                self._grid[ay][ax] &= ~2  # clear E bit on a
                self._grid[by][bx] &= ~8  # clear W bit on b
            elif b - a == self._width:
                # a's S wall open and b's N wall open
                self._grid[ay][ax] &= ~4  # clear S bit on a
                self._grid[by][bx] &= ~1  # clear N bit on b
            # this remaining elif is optional a is always < b in the pair
            elif b - a == -1:
                # a's W wall open and b's E wall open
                self._grid[ay][ax] &= ~8  # clear W bit on a
                self._grid[by][bx] &= ~2  # clear E bit on b
            elif b - a == -self._width:
                # a's N wall open and b's S wall open
                self._grid[ay][ax] &= ~1  # clear N bit on a
                self._grid[by][bx] &= ~4  # clear S bit on b

    # giving opening for the entry cell and exit cell
    def _open_entry_exit(self) -> None:
        for x, y in [self._entry_coord, self._exit_coord]:
            if y == 0:
                self._grid[y][x] &= ~1  # open North
            elif y == self._height - 1:
                self._grid[y][x] &= ~4  # open South
            elif x == 0:
                self._grid[y][x] &= ~8  # open West
            elif x == self._width - 1:
                self._grid[y][x] &= ~2  # open East

    # setting 42 symbol constrain
    def _forty_two_cells(self) -> set[tuple[int, int]]:
        if self._height > 7 and self._width > 9:
            x0 = self._width // 2
            y0 = self._height // 2
            ftset = {
                (-3 + x0, -2 + y0), (-3 + x0, -1 + y0), (-3 + x0, 0 + y0),
                (-2 + x0, 0 + y0), (-1 + x0, 0 + y0), (-1 + x0, 1 + y0),
                (-1 + x0, 2 + y0), (1 + x0, -2 + y0), (2 + x0, -2 + y0),
                (3 + x0, -2 + y0), (3 + x0, -1 + y0), (3 + x0, 0 + y0),
                (2 + x0, 0 + y0), (1 + x0, 0 + y0), (1 + x0, 1 + y0),
                (1 + x0, 2 + y0), (2 + x0, 2 + y0), (3 + x0, 2 + y0)
            }
            return ftset
        else:
            print("Maze too small for '42' pattern, skipping")
            return set()

    # 3x3 or more ccoridor validator
    def _has_open_3x3(self, x0: int, y0: int) -> bool:
        # Check horizontal connections
        for dy in range(3):
            for dx in range(2):
                # East wall exist
                if self._grid[y0 + dy][x0 + dx] & 2:
                    return False
        # Check vertical connections
        for dx in range(3):
            for dy in range(2):
                # South wall exist
                if self._grid[y0 + dy][x0 + dx] & 4:
                    return False
        return True

    # BFS: Theseus
    def solve(self) -> list[str]:
        start = self._entry_coord
        end = self._exit_coord
        path: list[str] = []
        if start == end:
            return path
        queue = deque([start])
        visited = {start}
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        while queue:
            current = queue.popleft()
            if current == end:
                break
            x, y = current
            for dir, bit, (dx, dy) in DIRECTIONS:
                # open wall check. if yes wall is open so walkable
                if self._grid[y][x] & bit == 0:
                    neighbor = (x + dx, y + dy)
                    # skipping off grid (entry and exit doorway)
                    if not (
                        0 <= neighbor[0] < self._width and
                        0 <= neighbor[1] < self._height
                    ):
                        continue
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        came_from[neighbor] = (current, dir)

        if end not in came_from:
            raise ValueError(f"No path found between {start} and {end}")
        current = end
        while current != start:
            parent, direction = came_from[current]
            path.append(direction)
            current = parent

        path.reverse()
        return path

    # making a perfect maze imperfect. U monster!
    def _add_loop(
        self, rejected_walls: list[tuple[int, int]]
    ) -> list[tuple[int,  int]]:
        if self._perfect or not rejected_walls:
            return []
        rng = random.Random(self._seed)
        return [rng.choice(rejected_walls)]


# check for 3x3 open block to run through every possible cases
def find_open_3x3_blocks(maze: MazeGenerator) -> list[tuple[int, int]]:
    violations = []
    for x0 in range(maze._width - 2):
        for y0 in range(maze._height - 2):
            if maze._has_open_3x3(x0, y0):
                violations.append((x0, y0))
    return violations


#  method to verify if the created maze is consistent, ie the properties
#  of each cell agrees with the nearby cell
def verify_coherence(grid: list[list[int]]) -> list[str]:
    """Returns a list of error messages for any incoherent wall pairs found."""
    errors = []
    width = len(grid[0])
    height = len(grid)
    for y in range(height):
        for x in range(width):
            #  checking east neighbor
            if x < width - 1:
                east_cell = grid[y][x + 1]
                current_cell = grid[y][x]
                if bool(current_cell & 2) != bool(east_cell & 8):
                    errors.append(f"E wall of ({x},{y}) is broken")
            #  checking south neightbor
            if y < height - 1:
                south_cell = grid[y + 1][x]
                curr_cell = grid[y][x]
                if bool(curr_cell & 4) != bool(south_cell & 1):
                    errors.append(f"S wall of ({x},{y}) is broken")
    return errors


def write_output(
    grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int],
    path: list[str], filename: str
) -> None:
    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")
