import pyautogui as pag
import pyscreeze


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


def get_cell_region(point: pag.Point, width: int, height: int) -> tuple[int, int, int, int]:
    # Returns (left, top, right, bottom) tuple.
    left = int(point.x - (width / 2))
    top = int(point.y - (height / 2))
    return (left, top, left + width, top + height)

