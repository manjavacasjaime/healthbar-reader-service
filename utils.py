from PIL import Image
import numpy as np
import sys
from matplotlib import pyplot as plt

"""
These methods were used during the development process in order to check the API's
proper behavior.
"""

def show_binarized_image(img: Image, threshold: int):
    image_gray = img.convert('L')
    image_bin = image_gray.point( lambda p: 255 if p > threshold else 0 )
    image_bin.show()

def show_image_from_array(img: np.ndarray, mode: str):
    plt.imshow(img, mode)
    plt.show()

#Line gets marked with threshold color
def show_binarized_image_with_marked_line(img: np.ndarray, line: int, threshold: int):
    for i in range(len(img)):
        for j in range(len(img[i])):
            if i == line and img[i][j] > threshold:
                img[i][j] = threshold
            elif img[i][j] > threshold:
                img[i][j] = 255
            else:
                img[i][j] = 0
    show_image_from_array(img, 'gray')

#Column gets marked with threshold color
def show_binarized_image_with_marked_column(img: np.ndarray, column: int, threshold: int):
    for i in range(len(img)):
        for j in range(len(img[i])):
            if j == column and img[i][j] > threshold:
                img[i][j] = threshold
            elif img[i][j] > threshold:
                img[i][j] = 255
            else:
                img[i][j] = 0
    show_image_from_array(img, 'gray')

#Requires the script to run as administrator
def log(message: str):
    old_stdout = sys.stdout
    log_file = open('message.log', 'w')
    sys.stdout = log_file
    print(message)
    sys.stdout = old_stdout
    log_file.close()
