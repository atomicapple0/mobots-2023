import cv2
from threshold import threshold
import numpy as np
import os

import cv_utils
from cv_utils import *

cv_utils.IMSHOW_MODE = cv_utils.NO_OP
# cv_utils.IMSHOW_MODE = cv_utils.CV2_SHOW_BLOCKING

RESOLUTION = (320, 240)
CENTER_COL = RESOLUTION[0] // 2
ROW_LO = 125
ROW_HI = 175
# ROW_LO = 75
# ROW_HI = 120
# ROW_LO = 25
# ROW_HI = 75
WINDOW_SIZE = ROW_HI - ROW_LO

class Blob():
    def __init__(self, size, center, col_lo, col_hi):
        self.size = size
        self.center = center
        self.col_lo = col_lo
        self.col_hi = col_hi
        self.row_lo = ROW_LO
        self.row_hi = ROW_HI
    
    def draw_bbox(self, img):
        cv2.rectangle(img, (self.col_lo, self.row_lo), (self.col_hi, self.row_hi), (0,255,0), 2)
        cv2.circle(img, (int(self.center), int((self.row_lo+self.row_hi)/2)), 5, (0,0,255), -1)
    
    def overlapping(self, other):
        return max(self.col_lo, other.col_lo) <= min(self.col_hi, other.col_hi)
    
    def merge(self, other):
        self.centroid = (self.size * self.center + other.size * other.center) / (self.size + other.size)
        self.size = self.size + other.size
        self.col_lo = min(self.col_lo, other.col_lo)
        self.col_hi = max(self.col_hi, other.col_hi)
    
    def __repr__(self):
        return f'Blob(size={self.size}, center={self.center}, col_lo={self.col_lo}, col_hi={self.col_hi})'

def detect_line(img):
    img = img.astype(np.uint8)
    thresh = threshold(img).astype(np.uint8)
    # thresh[:ROW_LO,:] = 0
    # thresh[ROW_HI:,:] = 0

    labels = []
    try:
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
            thresh, connectivity=8
        )
        sizes = stats[:, -1].copy()
        max_label = 1
        max_size = sizes[1]
        for i in range(2, nb_components):
            if sizes[i] > max_size:
                max_label = i
                max_size = sizes[i]
        if max_size > 200:
            labels.append(max_label)

        sizes[max_label] = -1
        max_label = 1
        max_size = sizes[1]
        for i in range(2, nb_components):
            if sizes[i] > max_size:
                max_label = i
                max_size = sizes[i]
        if max_size > 500:
            labels.append(max_label)
        # print(max_size)
    except IndexError:
        pass

    # print(labels)
    
    blobs = []
    for label in labels:
        blob = Blob(
            size=stats[label][4],
            center=centroids[label][0],
            col_lo=stats[label][0],
            col_hi=stats[label][0]+stats[label][2],
        )
        blobs.append(blob)
    if len(blobs) > 1 and blobs[0].overlapping(blobs[1]):
        blobs[0].merge(blobs[1])
        blobs.pop(1)

    thresh = gray2bgr(thresh*255)
    blobs.sort(key=lambda b: b.center)
    if blobs is None:
        print("no blobs")
    for blob in blobs:
        blob.draw_bbox(img)
        blob.draw_bbox(thresh)
    cv2.line(img, (CENTER_COL, RESOLUTION[1]-100), (CENTER_COL, RESOLUTION[1]), (255,255,0), 5)
    out = np.hstack((img,thresh))
    return out, blobs

from utils import save_img, flip_stack_unfloat

if __name__ == '__main__':
    src_dir = "imgs/input/"
    dest_dir = "imgs/final/"
    jpgs = [jpg for jpg in os.listdir(src_dir) if jpg.endswith('jpg') or jpg.endswith('png')]
    for idx,jpg in enumerate(jpgs):
        src_file = src_dir + jpg
        print(f'reading: {src_file}')
        img = cv2.imread(src_file)
        out, _ = detect_line(img)
        save_img(dest_dir + jpg, np.flipud(flip_stack_unfloat(out)))