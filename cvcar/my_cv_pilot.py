import cv2
import numpy as np
import logging
from cv import *
from threshold import *
from time import time

class MockCvPilot:
    def __init__(self, pid, cfg):
        pass

    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        start = time()
        steering, throttle = 0, 0
        # img, steering, throttle = process_img(cam_img)
        img = threshold(cam_img)

        end = time()
        print(f"done in {end-start} sec")

        return steering, throttle, img









