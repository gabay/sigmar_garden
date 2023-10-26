import glob
import random
import time

import cv2
import numpy as np
import pyautogui as pag
from PIL import Image

# from pynput.mouse import Button, Controller

TL = (1056, 223)
TR = (1384, 220)
ML = (888, 511)
BL = (1057, 791)
NEWGAME_POS = (880, 880)
DELAY = 0.001
CLICKS_PER_BATCH = 30


def get_cells():
    # top row
    row = np.linspace(TL, TR, 6)
    dx = row[1] - row[0]
    # left col1
    col1 = np.linspace(TL, ML, 6)[1:]
    dy1 = col1[1] - col1[0]
    # left col2
    col2 = np.linspace(ML, BL, 6)[1:]
    dy2 = col2[1] - col2[0]
    cells = [row]
    for i, cell in enumerate(col1):
        right = cells[-1][-1] + dy2
        count = 7 + i
        cells.append(np.linspace(cell, right, count))
    for i, cell in enumerate(col2):
        right = cells[-1][-1] + dy1
        count = 10 - i
        cells.append(np.linspace(cell, right, count))

    return np.concatenate(tuple(cells))


CELLS = get_cells()
IMAGES = [Image.open(_f).convert("RGB") for _f in glob.glob("cell_active/*.png")]


def get_active_cells() -> list[pag.Point]:
    pag.moveTo(NEWGAME_POS)
    screen = pag.screenshot()
    points = []
    for image in IMAGES:
        for bbox in pag.locateAll(image, screen, confidence=0.8):
            points.append(pag.center(bbox))
    print(f"Active cells: {len(points)}")
    return sorted(points)


def click(position: pag.Point):
    pag.mouseDown(*position)
    # time.sleep(DELAY)
    pag.mouseUp()


def main():
    print("waiting 2 seconds to start...")
    time.sleep(2)
    print("Starting!")

    active_cells = get_active_cells()
    while True:
        for _ in range(CLICKS_PER_BATCH):
            click(random.choice(active_cells))

        new_active_cells = get_active_cells()
        if active_cells != new_active_cells:
            # record new set of active cells
            active_cells == new_active_cells
        else:
            # state did not change - start a new game
            print("new game!")
            click(NEWGAME_POS)
            time.sleep(5)
            active_cells = get_active_cells()


if __name__ == "__main__":
    main()
