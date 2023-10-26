import sys
from typing import Optional

import cv2
import numpy as np
import pyautogui as pag
from PIL import Image

import sigmar_garden
import vision
import common

def get_cell(image: Image.Image) -> Optional[sigmar_garden.Cell]:
    image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    cv2.imshow("Tag", image_cv2)
    inp = cv2.waitKey(0)
    cv2.destroyAllWindows()
    tag = chr(inp).upper().replace("-", sigmar_garden.Cell.EMPTY.value)
    if tag == "`":
        sys.exit()
    try:
        cell = sigmar_garden.Cell(tag)
        print(tag, cell.name)
        return cell
    except ValueError:
        print(tag, "Skipped")


class Tagger:
    def __init__(self):
        self.seen = {image.tobytes() for _, image in vision.get_cell_images()}

    def tag(self, image: Image.Image):
        image_bytes = image.tobytes()
        if image_bytes in self.seen:
            return
        self.seen.add(image_bytes)
        cell = get_cell(image)
        if cell:
            vision.save_cell_image(cell, image)


def main():
    print("* Looking for game board...")
    pag.moveTo(1, 1)
    board_bbox = pag.locateOnScreen("board.png", minSearchTime=10, confidence=0.9)
    if board_bbox is None:
        print("ERROR: did not find board")
        sys.exit()
    positions = list(common.get_cell_positions(board_bbox))
    tagger = Tagger()
    while True:
        input("press Enter to check the board.")
        screen = pag.screenshot()
        for position in positions:
            cell_image = screen.crop(common.get_cell_region(position, 50, 50))
            tagger.tag(cell_image)


if __name__ == "__main__":
    main()
