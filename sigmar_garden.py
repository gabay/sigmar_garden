import copy
import itertools
from dataclasses import dataclass
from enum import Enum
from functools import cache

_MID_ROW = 5


class Cell(Enum):
    EMPTY = "-"
    FIRE = "F"
    WATER = "W"
    AIR = "A"
    EARTH = "E"
    SALT = "O"
    MORS = "M"
    VITAE = "V"
    QUICKSILVER = "Q"
    LEAD = "L"
    TIN = "T"
    IRON = "I"
    COPPER = "C"
    SILVER = "S"
    GOLD = "G"


ELEMENTS = (Cell.FIRE, Cell.WATER, Cell.AIR, Cell.EARTH)
METALS = (Cell.LEAD, Cell.TIN, Cell.IRON, Cell.COPPER, Cell.SILVER, Cell.GOLD)
METALS_EXCEPT_GOLD = (Cell.LEAD, Cell.TIN, Cell.IRON, Cell.COPPER, Cell.SILVER)
NEXT_METAL = {
    Cell.LEAD: Cell.TIN,
    Cell.TIN: Cell.IRON,
    Cell.IRON: Cell.COPPER,
    Cell.COPPER: Cell.SILVER,
    Cell.SILVER: Cell.GOLD,
    Cell.GOLD: Cell.EMPTY,
}
CELLS_PER_ROW = [6, 7, 8, 9, 10, 11, 10, 9, 8, 7, 6]


@cache
def _get_matches() -> set[tuple[Cell, ...]]:
    matches = set()
    for element in ELEMENTS:
        matches |= {(element, element), (element, Cell.SALT), (Cell.SALT, element)}
    matches |= {(Cell.SALT, Cell.SALT)}
    matches |= {(Cell.MORS, Cell.VITAE), (Cell.VITAE, Cell.MORS)}
    for metal in METALS_EXCEPT_GOLD:
        matches |= {(metal, Cell.QUICKSILVER), (Cell.QUICKSILVER, metal)}
    matches |= {(Cell.GOLD,)}
    return matches


def cells_match(*cells: Cell) -> bool:
    return cells in _get_matches()


@dataclass
class Point:
    row: int
    col: int

    def adj_circle(self) -> list["Point"]:
        top_left_dx = -1 if self.row <= _MID_ROW else 0
        bottom_left_dx = -1 if self.row >= _MID_ROW else 0
        # topleft, topright, right, bottomright, bottomleft, left
        yield Point(self.row - 1, self.col + top_left_dx)
        yield Point(self.row - 1, self.col + top_left_dx + 1)
        yield Point(self.row, self.col + 1)
        yield Point(self.row + 1, self.col + bottom_left_dx + 1)
        yield Point(self.row + 1, self.col + bottom_left_dx)
        yield Point(self.row, self.col - 1)

    @classmethod
    def from_index(cls, index: int) -> "Point":
        for row, cells_in_row in enumerate(CELLS_PER_ROW):
            if index < cells_in_row:
                return cls(row, index)
            index -= cells_in_row
        raise ValueError(f"Cannot convert index to point: {index}")

    def to_index(self) -> int:
        return sum(CELLS_PER_ROW[: self.row]) + self.col


@dataclass
class Move:
    points: list[Point]

    def __str__(self):
        return "Move(" + " + ".join(map(str, self.points)) + ")"


@dataclass
class Board:
    cells: list[list[Cell]]
    active_metal: Cell = Cell.LEAD

    def __post_init__(self):
        assert len(self.cells) == 11
        for i, row in enumerate(self.cells):
            expected_cells = min(6 + i, 16 - i)
            assert len(row) == expected_cells

    def __getitem__(self, point: Point) -> Cell:
        if not 0 <= point.row < len(self.cells):
            return Cell.EMPTY
        if not 0 <= point.col < len(self.cells[point.row]):
            return Cell.EMPTY
        return self.cells[point.row][point.col]

    def __setitem__(self, point: Point, cell: Cell):
        self.cells[point.row][point.col] = cell

    def __str__(self) -> str:
        lines = []
        for i, row in enumerate(self.cells):
            offset = max(0, 5 - i, i - 5)
            line = (" " * offset) + " ".join(cell.value for cell in row)
            lines.append(line)
        return "\n".join(lines)

    def __hash__(self) -> int:
        cells = sum(self.cells, [])
        return hash((self.active_metal, *cells))

    def is_active(self, point: Point) -> bool:
        cell = self[point]
        if cell == Cell.EMPTY:
            return False

        if cell in METALS and cell != self.active_metal:
            return False

        adj_cells = [self[adj] for adj in point.adj_circle()]
        for i in range(len(adj_cells)):
            if (
                adj_cells[i] == Cell.EMPTY
                and adj_cells[i - 1] == Cell.EMPTY
                and adj_cells[i - 2] == Cell.EMPTY
            ):
                return True
        return False

    def get_points(self) -> list[Point]:
        for row, cells in enumerate(self.cells):
            for col in range(len(cells)):
                yield Point(row, col)

    def get_active_points(self) -> list[Point]:
        return filter(self.is_active, self.get_points())

    def get_moves(self) -> list[Move]:
        points = list(self.get_active_points())
        for p in points:
            if cells_match(self[p]):
                yield Move([p])
        for p1, p2 in itertools.combinations(points, 2):
            if cells_match(self[p1], self[p2]):
                yield Move([p1, p2])

    def do_move(self, move: Move) -> "Board":
        new_board = self.copy()
        for p in move.points:
            if new_board.active_metal == new_board[p]:
                new_board.active_metal = NEXT_METAL[new_board[p]]
            new_board[p] = Cell.EMPTY
        return new_board

    @classmethod
    def new_board(cls) -> "Board":
        cells = [[Cell.EMPTY] * i for i in CELLS_PER_ROW]
        return cls(cells)

    def copy(self) -> "Board":
        return Board(copy.deepcopy(self.cells), self.active_metal)

    def is_solved(self) -> bool:
        for row in self.cells:
            for cell in row:
                if cell != Cell.EMPTY:
                    return False
        return True


def main():
    board = Board.new_board()
    board[Point(5, 5)] = Cell.GOLD
    print(board)
    print(f"Active metal: {board.active_metal}")
    print(f"- Moves: {list(board.get_moves())}")
    board.active_metal = Cell.GOLD
    print(f"Active metal: {board.active_metal}")
    print(f"- Moves: {list(board.get_moves())}")
    new_board = board.do_move(next(board.get_moves()))
    print(new_board)


if __name__ == "__main__":
    main()
