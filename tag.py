import sys
import time

import cv2
import numpy as np
import pyautogui as pag
import pyscreeze
from PIL import Image

import sigmar_garden
import vision

CELL_HEIGHT = 50
CELL_WIDTH = 50


def get_cell_positions(board_bbox: pyscreeze.Box) -> list[pag.Point]:
    height_padding = 20
    dx = board_bbox.width / 11
    dy = (board_bbox.height - height_padding) / 11
    center = pag.Point(
        board_bbox.left + (board_bbox.width / 2),
        board_bbox.top + (board_bbox.height / 2),
    )
    for row_number in range(11):
        row_number_relative_to_center = row_number - 5
        y = int(center.y + (dy * (row_number_relative_to_center)))

        cells_in_row = min(6 + row_number, 16 - row_number)
        for cell_number in range(cells_in_row):
            cell_number_relative_to_center = cell_number - ((cells_in_row - 1) / 2)
            x = int(center.x + (dx * cell_number_relative_to_center))
            yield pag.Point(x, y)


def get_cell_region(point: pag.Point) -> tuple[int, int, int, int]:
    # Returns (left, top, right, bottom) tuple.
    left = int(point.x - (CELL_WIDTH / 2))
    top = int(point.y - (CELL_HEIGHT / 2))
    return (left, top, left + CELL_WIDTH, top + CELL_HEIGHT)


def show(image: cv2.Mat, title=""):
    cv2.imshow(title, np.array(image))
    if cv2.waitKey(0) == ord("q"):
        sys.exit()
    cv2.destroyAllWindows()

def get_label(image: Image.Image) -> sigmar_garden.Cell:
    pass

def main():
    print("* Looking for game board...")
    pag.moveTo(1, 1)
    board_bbox = pag.locateOnScreen("board.png", minSearchTime=10, confidence=0.9)
    positions = list(get_cell_positions(board_bbox))
    seen = set()
    while True:
        time.sleep(5)
        screen = pag.screenshot()
        for position in enumerate(positions):
            cell_image = screen.crop(get_cell_region(position))
            cell_bytes = cell_image.tobytes()
            if cell_bytes not in seen:
                seen.add(cell_bytes)
                get_label(cell_image)

            cell = cell_recognizer.recognize(cell_image)
            # show(vision.transform(cell_image), cell.name)
            board[sigmar_garden.Point.from_index(index)] = cell




    cell_recognizer = vision.CellRecognizer()


    while True:

    print("* Starting...")
    time.sleep(1)
    screen = Image.open(
        "/home/roi/Pictures/Screenshots/Screenshot from 2023-10-24 00-47-16.png"
    )

    print("* Looking for game board...")
    pag.moveTo(1, 1)
    # board_bbox = pag.locateOnScreen("board.png", minSearchTime=10, confidence=0.9)
    board_bbox = pag.locate("board.png", screen, confidence=0.9)
    if board_bbox is None:
        print("ERROR: could not find game board")
        return
    print(f"* Found (at {board_bbox})")

    print("* Reading board cells...")
    positions = list(get_cell_positions(board_bbox))
    board = sigmar_garden.Board.new_board()
    for index, position in enumerate(positions):
        cell_image = screen.crop(get_cell_region(position))
        cell = cell_recognizer.recognize(cell_image)
        # show(vision.transform(cell_image), cell.name)
        board[sigmar_garden.Point.from_index(index)] = cell
    print("* Done. Board:")
    print(board)
    show(vision.transform(screen))


if __name__ == "__main__":
    main()
