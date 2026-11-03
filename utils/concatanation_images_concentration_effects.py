import os
from pathlib import Path
import cv2
from PIL import Image

class ConcatenationImagesConcEffects:
    def __init__(self, path_conc):
        self.path_conc = path_conc

    def get_images(self):
        figure_list = []
        path = f"{Path.cwd().as_posix()}/{self.path_conc}"
        figures = os.listdir(path)
        for figure in figures:
            if figure.endswith('.png'):
                img_bgr = cv2.imread(f"{path}/{figure}")
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                figure_list.append(img_rgb)
        return figure_list


    def resize_to_same_height(self, img1, img2):
        h = min(img1.shape[0], img2.shape[0])

        def resize(img):
            ratio = h / img.shape[0]
            new_w = int(img.shape[1] * ratio)
            return cv2.resize(img, (new_w, h))

        return resize(img1), resize(img2)


    def perform_hconcat(self, figure_list):
        result = []

        for i in range(0, 8, 2):
            img1, img2 = self.resize_to_same_height(figure_list[i], figure_list[i+1])
            result.append(cv2.hconcat([img1, img2]))
        return result


    def resize_to_same_width(self, img1, img2):
        w = min(img1.shape[1], img2.shape[1])

        def resize(img):
            ratio = w / img.shape[1]
            new_h = int(img.shape[0] * ratio)
            return cv2.resize(img, (w, new_h))

        return resize(img1), resize(img2)
    
    def perform_vconcat(self, figure_list):
        result = []

        for i in range(0, len(figure_list), 2):
            img1, img2 = self.resize_to_same_width(figure_list[i], figure_list[i+1])
            result.append(cv2.vconcat([img1, img2]))

        return result


    def save_img(self, figure_list):
        for id, img in enumerate(figure_list):
            PILImage = Image.fromarray(img, mode="RGB")
            path_to_save = f'{self.path_conc}/concat'
            os.makedirs(path_to_save, exist_ok=True)
            PILImage.save(f'{path_to_save}/population_curves_concat_{id}.png', dpi=(300, 300))
