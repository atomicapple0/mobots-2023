import cv2
import numpy as np
import logging
from cv import *
from detect_line import detect_line
from pid import pid
from threshold import *
from time import time, sleep
<<<<<<< HEAD
from new_cv import *
=======
>>>>>>> 4322ae29c5e32a1748557a39cf696c2702281361

class MockCvPilot:
    def __init__(self, pid, cfg):
        self.steering = 0
        self.throttle = 0
        self.init_time = time()
        self.elapsed = 0
        pass

    def step(self):
        sleep(.001)
        self.elapsed = time() - self.init_time
    
    def send_w_v(self, w, v):
        self.steering = w
        # self.throttle = v
    
    def time(self):
        return self.elapsed
    
    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        start = time()
        steering, throttle = 0, 0
        # img, steering, throttle = process_img(cam_img)

        # old cv code
        processed, blobs = new_cv(cam_img)
        pid(self,blobs)

        end = time()
        self.steering /= 10
        print(f"done s:{self.steering:.2f} t{self.throttle:.2f} in {end-start:.2f} sec")
        
        return -self.steering, self.throttle, processed









