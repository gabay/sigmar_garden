import random
import time
from datetime import datetime
from functools import partial

import pyautogui as pag
import pyscreeze

import common
import sigmar_garden
import vision


def click(position: pag.Point):
    pag.moveTo(*position, duration=0.2)
    pag.mouseDown(duration=0.1)
    pag.mouseUp()


def solve(board: sigmar_garden.Board) -> list[sigmar_garden.Move]:
    moves = []
    if _solve(board, moves, set()):
        return moves
    return []


def _solve(
    board: sigmar_garden.Board, moves: list[sigmar_garden.Move], seen: set
) -> bool:
    if board.is_solved():
        return True

    if board in seen:
        return False
    seen.add(board)

    next_moves = board.get_moves()
    for move in sorted(next_moves, key=partial(get_move_score, board), reverse=True):
        moves.append(move)
        if _solve(board.do_move(move), moves, seen):
            return True
        moves.pop()
    return False


def get_move_score(board: sigmar_garden.Board, move: sigmar_garden.Move) -> int:
    cells = [board[point] for point in move.points]
    if cells.count(sigmar_garden.Cell.SALT) == 1:
        return 1  # discourage salt + element
    return sum(map(get_cell_score, cells))


def get_cell_score(cell: sigmar_garden.Cell) -> int:
    if cell in sigmar_garden.ELEMENTS:
        return 4
    if cell in (sigmar_garden.Cell.VITAE, sigmar_garden.Cell.MORS):
        return 3
    if cell in (sigmar_garden.Cell.SALT, sigmar_garden.Cell.QUICKSILVER):
        return 3
    if cell in sigmar_garden.METALS:
        return 2
    return 0


def play_single_game(cell_recognizer: vision.CellRecognizer):
    print(datetime.now(), "- Looking for game board...")
    pag.moveTo(1, 1)
    board_bbox = pag.locateOnScreen("board.png", minSearchTime=10, confidence=0.9)
    if board_bbox is None:
        print("ERROR: could not find game board")
        return
    print(datetime.now(), f"- Found (at {board_bbox})")

    print(datetime.now(), "- Reading board cells...")
    positions = list(common.get_cell_positions(board_bbox))
    screen = pag.screenshot()
    board = sigmar_garden.Board.new_board()
    for index, position in enumerate(positions):
        cell = cell_recognizer.recognize(
            screen.crop(common.get_cell_region(position, 40, 40))
        )
        point = sigmar_garden.Point.from_index(index)
        board[point] = cell
    print(datetime.now(), "- Done. Board:")
    print(board)

    print(datetime.now(), "- Solving...")
    moves = solve(board)

    print(datetime.now(), "- Playing...")
    for move in moves:
        print(move)
        for point in move.points:
            click(positions[point.to_index()])


def main():
    print(datetime.now(), "- Starting...")
    time.sleep(2)

    print("* Looking for newgame button...")
    pag.moveTo(1, 1)
    newgame_pos = pag.locateCenterOnScreen("newgame.png", confidence=0.9)
    if newgame_pos is None:
        print("ERROR: could not find newgame button")
        return
    print(f"* Found (at {newgame_pos})")

    cell_recognizer = vision.CellRecognizer()

    while True:
        play_single_game(cell_recognizer)
        time.sleep(1)

        print("* Starting a new game!")
        click(newgame_pos)
        time.sleep(10)


if __name__ == "__main__":
    main()
