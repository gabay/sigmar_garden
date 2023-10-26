import random
import time

import pyautogui as pag
import pyscreeze

import sigmar_garden
import vision
import common


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

    for move in board.get_moves():
        moves.append(move)
        if _solve(board.do_move(move), moves, seen):
            return True
        moves.pop()
    return False


def play_single_game(cell_recognizer: vision.CellRecognizer):
    print("* Looking for game board...")
    pag.moveTo(1, 1)
    board_bbox = pag.locateOnScreen("board.png", minSearchTime=10, confidence=0.9)
    if board_bbox is None:
        print("ERROR: could not find game board")
        return
    print(f"* Found (at {board_bbox})")

    print("* Reading board cells...")
    positions = list(common.get_cell_positions(board_bbox))
    screen = pag.screenshot()
    board = sigmar_garden.Board.new_board()
    for index, position in enumerate(positions):
        cell = cell_recognizer.recognize(
            screen.crop(common.get_cell_region(position, 40, 40))
        )
        point = sigmar_garden.Point.from_index(index)
        board[point] = cell
    print("* Done. Board:")
    print(board)

    # print("* Solving...")
    # moves = solve(board)

    print("* Playing...")
    # for move in moves:
    moves = list(board.get_moves())
    while moves:
        move = random.choice(moves)
        print(move)
        for point in move.points:
            click(positions[point.to_index()])
        board = board.do_move(move)
        moves = list(board.get_moves())


def main():
    print("* Starting...")
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
        time.sleep(15)


if __name__ == "__main__":
    main()
