import cv2
import numpy as np
import logging
from cv import *
from detect_line import detect_line
from threshold import *

def new_cv(cam_img):
    img = resizer(cam_img)
    processed, blobs = detect_line(img)
    return processed, blobs