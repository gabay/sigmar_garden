import sys
import time

import cv2
import numpy as np
import pyautogui as pag
import pyscreeze

import common
import sigmar_garden
import vision


def show(image: cv2.Mat, title=""):
    cv2.imshow(title, np.array(image))
    if cv2.waitKey(0) == ord("q"):
        sys.exit()
    cv2.destroyAllWindows()


def main():
    cell_recognizer = vision.CellRecognizer()

    print("* Starting...")
    screen = pag.screenshot()

    print("* Looking for game board...")
    pag.moveTo(1, 1)
    board_bbox = pag.locateOnScreen("data/board.png", minSearchTime=10, confidence=0.9)
    if board_bbox is None:
        print("ERROR: could not find game board")
        return
    print(f"* Found (at {board_bbox})")

    print("* Reading board cells...")
    positions = list(common.get_cell_positions(board_bbox))
    board = sigmar_garden.Board.new_board()
    for index, position in enumerate(positions):
        cell_image = screen.crop(common.get_cell_region(position, 40, 40))
        cell = cell_recognizer.recognize(cell_image)
        # show(vision.transform(cell_image), cell.name)
        board[sigmar_garden.Point.from_index(index)] = cell
    print("* Done. Board:")
    print(board)
    show(vision.transform(screen))


if __name__ == "__main__":
    main()
