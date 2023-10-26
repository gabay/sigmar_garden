import functools
import os

import cv2
import numpy as np
from PIL import Image
from sklearn.linear_model import RidgeClassifier

import sigmar_garden


def get_cell_images() -> list[sigmar_garden.Cell, Image.Image]:
    for cell in sigmar_garden.Cell:
        paths = [f"cell_active/{cell.name}.png", f"cell_inactive/{cell.name}.png"]
        for path in paths:
            if os.path.exists(path):
                yield cell, imread(path)


@functools.cache
def imread(path: str) -> cv2.Mat:
    return cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)


def get_features(image: cv2.Mat | Image.Image) -> np.array:
    return transform(image).flatten()


def transform(image: cv2.Mat | Image.Image) -> cv2.Mat:
    image = np.array(image)
    rgb = np.concatenate(
        (
            image[10:-10, 10:-10, 0],
            image[10:-10, 10:-10, 1],
            image[10:-10, 10:-10, 2],
            grayscale(image[10:-10, 10:-10]),
        )
    )
    return threshold(grayscale(image))


def grayscale(image: cv2.Mat) -> cv2.Mat:
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def threshold(image: cv2.Mat) -> cv2.Mat:
    return cv2.adaptiveThreshold(
        image,
        0xFF,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        5,
        -1,
    )


def blur(image: cv2.Mat) -> cv2.Mat:
    return cv2.GaussianBlur(image, (5, 5), 0)


def erode_delate(image: cv2.Mat) -> cv2.Mat:
    kernel = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.uint8)
    return cv2.erode(cv2.dilate(image, kernel), kernel)


class CellRecognizer:
    def __init__(self):
        features = []
        labels = []
        for cell, image in get_cell_images():
            # cv2.imshow(cell.name, transform(image))
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            features.append(get_features(image))
            labels.append(cell.value)
        self.classifier = RidgeClassifier()
        self.classifier.fit(features, labels)

    def recognize(self, image: Image.Image) -> sigmar_garden.Cell:
        label = self.classifier.predict([get_features(image)])[0]
        return sigmar_garden.Cell(label)


def main():
    recognizer = CellRecognizer()
    for cell, image in get_cell_images():
        print(f"Cell: {cell.value}, prediction: {recognizer.recognize(image).value}")


if __name__ == "__main__":
    main()
