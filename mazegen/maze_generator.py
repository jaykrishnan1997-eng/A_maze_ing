#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   maze_generator.py                                    :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: jkrishna <jkrishna@student.42.fr>            +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/07/07 09:19:10 by jkrishna            #+#    #+#            #
#   Updated: 2026/07/07 14:08:31 by jkrishna           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import random


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


class MazeGenerator:
    def __init__(self, width: int, height: int, entry_coord: tuple[int, int], exit_coord: tuple[int, int], perfect: bool, seed: int | None):
        self._width = width
        self._height = height
        self._entry_coord = entry_coord
        self._exit_coord = exit_coord
        self._perfect = perfect
        self._seed = seed
        self._grid = [[15] * width for _ in range(height)]
        removed_walls = self._run_kruskal()
        self._apply_walls(removed_walls)

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
    def build_walls(self) -> list[tuple[int, int]]:
        walls = []
        for y in range(self._height):
            for x in range(self._width):
                # for the east wall
                if x < self._width - 1:
                    walls.append((self.cell_id(x, y), self.cell_id(x + 1, y)))
                # for the soth wall
                if y < self._height - 1:
                    walls.append((self.cell_id(x, y), self.cell_id(x, y + 1)))
        return walls

    def _run_kruskal(self) -> list[tuple[int, int]]:
        uf = UnionFind(self._width * self._height)
        walls = self.build_walls()
        rng = random.Random(self._seed)
        rng.shuffle(walls)
        removed_walls = []
        for a, b in walls:
            if uf.union(a, b):
                removed_walls.append((a, b))
        return removed_walls

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


# maze = MazeGenerator(3, 3, (0, 0), (2, 2), True, None)
# grid = maze.get_grid()
# grid[0][0] = 99
# print(maze.get_grid())
