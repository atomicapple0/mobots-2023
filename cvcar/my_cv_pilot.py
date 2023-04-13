import cv2
import numpy as np
import logging
from cv import *

class MockCvPilot:
    def __init__(self, pid, cfg):
        pass

    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        cam_img, steering, throttle = self.process_img(cam_img)

        return steering, throttle, cam_img









