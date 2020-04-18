import numpy as np
import cv2
from tft import utils


def show_image(img, window_name, wait=25):
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, utils.onMouseClick)
    cv2.imshow(window_name, cv2.cvtColor(img, cv2.COLOR_RGB2RGBA))
    cv2.waitKey(wait)


def close_window(window_name):
    cv2.destroyWindow(window_name)


def draw_shapes(img, vertices):
    for vertices in vertices:
        draw_shape(img, vertices)


def draw_shape(img, vertices):
    pts = np.array(vertices, np.int32)
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (0, 255, 255))


def crop_shape(img, vertex, scale_percent=100):
    ref_point = vertex
    crop_img = img[ref_point[1][1] + 2:ref_point[2][1], ref_point[0][0] + 2:ref_point[1][0]]
    if scale_percent != 100:
        width = int(crop_img.shape[1] * scale_percent / 100)
        height = int(crop_img.shape[0] * scale_percent / 100)
        dim = (width, height)
        return cv2.resize(crop_img, dim)
    return crop_img


def crop_shapes(img, vertices, scale_percent=100):
    imgs = []
    for vertex in vertices:
        imgs.append(crop_shape(img, vertex, scale_percent))
    return imgs


def wait():
    cv2.waitKey(25)
