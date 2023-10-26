import functools
import glob

import cv2
import numpy as np
from PIL import Image
from sklearn.linear_model import RidgeClassifier

import sigmar_garden


def get_cell_images() -> list[sigmar_garden.Cell, Image.Image]:
    for cell in sigmar_garden.Cell:
        for path in get_cell_image_paths(cell):
            yield cell, imread(path)


def get_cell_image_paths(cell: sigmar_garden.Cell) -> list[str]:
    return glob.glob(f"data/{cell.name}_*.png")


def save_cell_image(cell: sigmar_garden.Cell, image: Image.Image):
    index = len(get_cell_image_paths(cell))
    image.save(f"data/{cell.name}_{index}.png")


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



class CellRecognizer:
    def __init__(self):
        self.labels = []
        # features = []
        images = []
        for cell, image in get_cell_images():
            self.labels.append(cell.value)
            # features.append(get_features(image))
            images.append(np.array(image))
        # self.classifier = RidgeClassifier()
        # self.classifier.fit(features, self.labels)
        self.images = np.concatenate(images)

    def recognize(self, image: Image.Image) -> sigmar_garden.Cell:
        # label = self.classifier.predict([get_features(image)])[0]
        match = cv2.matchTemplate(self.images, np.array(image), cv2.TM_SQDIFF_NORMED)
        _, _, loc, _ = cv2.minMaxLoc(match)
        label = self.labels[(loc[1] + (image.height // 2)) // 50]
        return sigmar_garden.Cell(label)


def main():
    recognizer = CellRecognizer()
    for cell, image in get_cell_images():
        print(f"Cell: {cell.value}, prediction: {recognizer.recognize(image).value}")


if __name__ == "__main__":
    main()
