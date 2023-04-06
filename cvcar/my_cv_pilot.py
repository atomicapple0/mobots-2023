import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BasicController:
    def __init__(self):
        self.k_p = 1
    
    # given offset from centerline, return steering and throttle
    def calculate_cmd(self, offset):
        steering = -self.k_p * offset
        throttle = .1 if abs(steering) < .1 else .05
        return steering, throttle


class MockCvPilot:
    def __init__(self, pid, cfg):
        self.pid_st = pid
        self.overlay_image = cfg.OVERLAY_IMAGE
        self.steering = 0
        self.throttle = 0
        self.counter = 0
        self.offset = 0


    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        self.counter += 1

        # run segmentation
        if self.overlay_image:
            cam_img, self.offset = self.compute_offset(cam_img)
            cam_img = self.annotate_img(cam_img)

        # run controller
        self.steering, self.throttle = self.cntrl.calculate_cmd(self.offset)

        return self.steering, self.throttle, cam_img

    def annotate_img(self, img):
        img = np.copy(img)

        # some text to show on the overlay
        display_str = []
        display_str.append(f"STEERING:{self.steering:.1f}")
        display_str.append(f"THROTTLE:{self.throttle:.2f}")
        display_str.append(f"COUNTER:{self.counter}")

        lineheight = 25
        y = lineheight
        x = lineheight
        for s in display_str:
            # green text with black outline so it shows up on any background
            cv2.putText(img, s, color=(0, 0, 0), org=(x ,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=3)
            cv2.putText(img, s, color=(0, 255, 0), org=(x ,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=1)
            y += lineheight

        return img

    def compute_offset(self, img):
        
