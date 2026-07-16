#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   maze_generator.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: jkrishna <jkrishna@student.42.fr>            +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/07 09:19:10 by jkrishna            #+#    #+#            #
#   Updated: 2026/07/16 13:29:08 by jkrishna           ###   ########.fr      #
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
    """Disjoint-set (Union-Find) data structure with path compression
    and union by rank.

    Cells are identified by integer IDs (0..size-1), not spatial (x, y)
    coordinates. Used by :class:`MazeGenerator` to run Kruskal's
    algorithm over the maze grid.
    """

    def __init__(self, size: int) -> None:
        """Initialize `size` disjoint singleton sets.

        Args:
            size: Number of elements to track (must be positive).

        Raises:
            ValueError: If `size` is zero or negative.
        """
        if size <= 0:
            raise ValueError("Size must be positive")
        self._parent = list(range(size))
        #  approximate measure of trees height
        self._rank = size * [0]

    #  find the leader/ root and update the chain and
    #  new nodes root as the leader.
    #  conquer, submit and say u shall praise the lord's name forever
    def find(self, x: int) -> int:
        """Find the representative (root) of the set containing `x`.

        Applies path compression, so every node visited along the way
        is re-parented directly to the root, speeding up future calls.

        Args:
            x: ID of the element to find the root of.

        Returns:
            The ID of the root element representing `x`'s set.
        """
        #  find with path compression
        if self._parent[x] != x:
            #  recursively update all nodes
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    #  merge two branch into one containing both
    def union(self, x: int, y: int) -> bool:
        """Merge the sets containing `x` and `y`, if not already merged.

        Uses union by rank: the tree with the smaller rank is attached
        under the root of the tree with the larger rank, keeping the
        overall structure shallow.

        Args:
            x: ID of the first element.
            y: ID of the second element.

        Returns:
            True if `x` and `y` were in different sets and are now
            merged; False if they were already in the same set (i.e.
            already connected, so no union was performed).
        """
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


# Daedalus and Theseus
class MazeGenerator:
    """Generates a maze on a rectangular grid using Kruskal's algorithm.

    Builds the maze as a minimum spanning tree over the grid's cells
    (guaranteeing a *perfect* maze when `perfect=True`), carves out a
    fixed "42" pattern of permanently disconnected cells, opens entry
    and exit doorways, and can solve the resulting maze with BFS.
    """

    def __init__(
        self, width: int, height: int, entry_coord: tuple[int, int],
        exit_coord: tuple[int, int], perfect: bool, seed: int | None = None
    ) -> None:
        """Build and generate a new maze.

        Args:
            width: Maze width in cells (must be positive).
            height: Maze height in cells (must be positive).
            entry_coord: (x, y) coordinate of the maze entry cell.
            exit_coord: (x, y) coordinate of the maze exit cell.
            perfect: If True, generate a perfect maze (exactly one
                path between any two cells). If False, one extra loop
                is added by reopening a single rejected wall.
            seed: Seed for reproducible generation, or None for
                non-deterministic generation.

        Raises:
            ValueError: If `width` or `height` is not positive, if
                either coordinate lies outside the grid, or if either
                coordinate falls inside the excluded "42" pattern.
        """
        if width <= 0 or height <= 0:
            raise ValueError(
                "Maze dimensions must be positive"
            )
        self._width = width
        self._height = height
        self._validate_coord(entry_coord)
        self._validate_coord(exit_coord)

        self._excluded = self._forty_two_cells()

        if entry_coord in self._excluded:
            raise ValueError(
                "Entry cannot be inside 42"
            )

        if exit_coord in self._excluded:
            raise ValueError(
                "Exit cannot be inside 42"
            )
        self._entry_coord = entry_coord
        self._exit_coord = exit_coord
        self._perfect = perfect
        self._seed = seed
        self._grid = [[15] * width for _ in range(height)]
        removed_walls, rejected_walls = self._run_kruskal()
        self._apply_walls(removed_walls)  # apply walls
        loop_walls = self._add_loop(rejected_walls)  # BFS see the real maze
        self._apply_walls(loop_walls)  # apply loop walls separately

    #  make a copy of the maze
    def _get_grid(self) -> list[list[int]]:
        """Return a copy of the internal maze grid.

        Returns:
            A row-major `list[list[int]]` copy of the grid, where each
            cell is a 4-bit wall bitmask (bit0=N, bit1=E, bit2=S,
            bit3=W; 1 = wall closed). Safe to mutate without affecting
            the generator's internal state.
        """
        return [row[:] for row in self._grid]

    #  to validate if coordinate within the range
    def _validate_coord(self, coord: tuple[int, int]) -> None:
        """Validate that a coordinate lies within the maze bounds.

        Args:
            coord: (x, y) coordinate to validate.

        Raises:
            ValueError: If the coordinate falls outside the maze's
                width/height range.
        """
        x, y = coord

        if not (
            0 <= x < self._width and
            0 <= y < self._height
        ):
            raise ValueError(
                f"Coordinate {coord} outside maze"
            )

    #  convert grid coordinate to cell ID
    def _cell_id(self, x: int, y: int) -> int:
        """Convert an (x, y) grid coordinate to a flat cell ID.

        Args:
            x: Column index.
            y: Row index.

        Returns:
            The unique integer cell ID for (x, y), used by
            :class:`UnionFind` and the wall list.
        """
        return (y * self._width) + x

    #  id to coordinate
    def _cell_coords(self, cell_id: int) -> tuple[int, int]:
        """Convert a flat cell ID back into an (x, y) grid coordinate.

        Args:
            cell_id: Integer cell ID, as produced by `_cell_id`.

        Returns:
            The (x, y) coordinate corresponding to `cell_id`.
        """
        return (cell_id % self._width, cell_id // self._width)

    #  Candidate wall list
    def _build_walls(
        self, excluded: set[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """Build the candidate list of walls Kruskal's algorithm may open.

        Every wall between two orthogonally adjacent cells is included,
        except walls touching any cell in `excluded` (e.g. the "42"
        pattern cells), which are skipped so those cells remain fully
        sealed off and disconnected from the rest of the maze.

        Args:
            excluded: Set of (x, y) coordinates to exclude from wall
                candidacy.

        Returns:
            A list of (cell_id_a, cell_id_b) pairs, one per candidate
            wall between two adjacent, non-excluded cells.
        """
        walls = []
        for y in range(self._height):
            for x in range(self._width):
                # skip cells making 42
                if (x, y) in excluded:
                    continue
                # for the east wall
                if x < self._width - 1 and (x + 1, y) not in excluded:
                    walls.append(
                        (self._cell_id(x, y),
                         self._cell_id(x + 1, y)))
                # for the soth wall
                if y < self._height - 1 and (x, y + 1) not in excluded:
                    walls.append(
                        (self._cell_id(x, y),
                         self._cell_id(x, y + 1)))
        return walls

    def _run_kruskal(
        self
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
        """Run randomized Kruskal's algorithm to build the maze's
        spanning tree.

        Shuffles the candidate wall list (seeded by `self._seed` for
        reproducibility) and processes each wall in order, opening it
        whenever its two cells are not yet connected.

        Returns:
            A tuple `(removed_walls, rejected_walls)`:
                - `removed_walls`: walls that were opened because they
                  connected two previously separate components (i.e.
                  the maze's spanning tree edges).
                - `rejected_walls`: walls that were left closed because
                  both cells were already connected; reused later to
                  add a single loop when `perfect=False`.
        """
        # initiate the maze
        uf = UnionFind(self._width * self._height)
        walls = self._build_walls(self._excluded)
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
        """Open the given walls in the grid's bitmask representation.

        For each (a, b) cell-ID pair, clears the matching wall bit on
        both sides simultaneously (e.g. a's East bit and b's West bit),
        ensuring neighboring cells always agree on a shared wall.

        Args:
            removed_walls: List of (cell_id_a, cell_id_b) pairs whose
                shared wall should be opened. Pairs must correspond to
                orthogonally adjacent cells.
        """
        for a, b in removed_walls:
            ax, ay = self._cell_coords(a)
            bx, by = self._cell_coords(b)
            if bx - ax == 1:
                # a's E wall open and b's W wall open
                self._grid[ay][ax] &= ~2  # clear E bit on a
                self._grid[by][bx] &= ~8  # clear W bit on b
            elif by - ay == 1:
                # a's S wall open and b's N wall open
                self._grid[ay][ax] &= ~4  # clear S bit on a
                self._grid[by][bx] &= ~1  # clear N bit on b

    # setting 42 symbol constrain
    def _forty_two_cells(self) -> set[tuple[int, int]]:
        """Compute the set of cells forming the fixed "42" pattern.

        The pattern is centered on the maze's midpoint and only applied
        if the maze is large enough to fit it (height > 7 and
        width > 9); otherwise the pattern is skipped entirely.

        Returns:
            A set of (x, y) coordinates to exclude from Kruskal's
            candidate wall list, or an empty set if the maze is too
            small for the pattern to fit.
        """
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

    # BFS: Theseus
    def _bfs_came_from(
        self
    ) -> dict[tuple[int, int], tuple[tuple[int, int], str]]:
        """Run BFS from the entry cell and build a predecessor map.

        Explores the maze breadth-first from `self._entry_coord`,
        following only open walls, until `self._exit_coord` is reached
        or the search space is exhausted.

        Returns:
            A dict mapping each visited (x, y) coordinate (except the
            entry) to a `(parent_coord, direction)` tuple, where
            `direction` is the single-character move ("N"/"E"/"S"/"W")
            taken from `parent_coord` to reach that cell. Used to
            reconstruct the shortest path via backtracking.

        Raises:
            ValueError: If no path exists between the entry and exit
                cells.
        """
        start = self._entry_coord
        end = self._exit_coord
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

        if end not in came_from and start != end:
            raise ValueError(f"No path found between {start} and {end}")
        return came_from

    def _solve(self) -> list[str]:
        """Compute the shortest path from entry to exit.

        Returns:
            A list of single-character direction strings ("N", "E",
            "S", "W") describing the shortest entry-to-exit path, in
            order of traversal. Returns an empty list if entry and
            exit are the same cell.
        """
        start = self._entry_coord
        end = self._exit_coord
        if start == end:
            return []
        came_from = self._bfs_came_from()
        path: list[str] = []
        current = end
        while current != start:
            parent, direction = came_from[current]
            path.append(direction)
            current = parent

        path.reverse()
        return path

    def _path_cell_ids(self) -> set[int]:
        """Compute the set of cell IDs lying on the entry-to-exit path.

        Returns:
            A set of cell IDs for every cell on the shortest
            entry-to-exit path, including both endpoints. Used to
            restrict loop-adding candidates to walls along the actual
            solution path.
        """
        start = self._entry_coord
        end = self._exit_coord
        if start == end:
            return {self._cell_id(*start)}
        came_from = self._bfs_came_from()
        cells = {end}
        current = end
        while current != start:
            parent, _ = came_from[current]
            cells.add(parent)
            current = parent
        return {self._cell_id(x, y) for (x, y) in cells}

    # making a perfect maze imperfect. U monster!
    def _add_loop(
        self, rejected_walls: list[tuple[int, int]]
    ) -> list[tuple[int,  int]]:
        """Select one wall to reopen, adding a single loop to the maze.

        Only applies when `self._perfect` is False. Restricts the
        candidate walls to those connecting two cells that both lie on
        the entry-to-exit path, so the added loop is guaranteed to be
        relevant to the solution route.

        Args:
            rejected_walls: Walls that Kruskal's algorithm declined to
                open because both cells were already connected.

        Returns:
            A list containing zero or one (cell_id_a, cell_id_b) wall
            to open: empty if the maze is perfect, if there are no
            rejected walls, or if none of the rejected walls lie along
            the entry-to-exit path; otherwise a single randomly chosen
            (seeded) wall from the valid candidates.
        """
        if self._perfect or not rejected_walls:
            return []

        # get the entry-exit path cells as a set of cell IDs
        path_cells = self._path_cell_ids()

        candidates = [
            (a, b) for a, b in rejected_walls
            if a in path_cells and b in path_cells
        ]

        if not candidates:
            return []  # no valid loop found in this path

        rng = random.Random(self._seed)
        return [rng.choice(candidates)]


# the part that forwards the output to parser in Hex form
def _write_output(
    grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int],
    path: list[str], filename: str
) -> None:
    """Write the generated maze to a file in hexadecimal wall encoding.

    The output format is: one line per grid row (each cell written as
    a single hex digit of its 4-bit wall bitmask), a blank line, the
    entry coordinate, the exit coordinate, and finally the solution
    path as a concatenated string of direction characters.

    Args:
        grid: Row-major maze grid, one 4-bit wall bitmask per cell.
        entry: (x, y) coordinate of the entry cell.
        exit: (x, y) coordinate of the exit cell.
        path: Solution path as a list of direction characters
            ("N"/"E"/"S"/"W").
        filename: Path of the file to write the output to.
    """
    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit[0]},{exit[1]}\n")
        f.write("".join(path) + "\n")
