import cv2
import numpy as np
from simple_pid import PID
import logging

logger = logging.getLogger(__name__)


class MockCvPilot:
    '''
    OpenCV based MOCK controller; just draws a counter and 
    returns 0 for thottle and steering.

    :param pid: a PID controller that can be used to estimate steering and/or throttle
    :param cfg: the vehicle configuration properties
    '''
    def __init__(self, pid, cfg):
        self.pid_st = pid
        self.overlay_image = cfg.OVERLAY_IMAGE
        self.steering = 0
        self.throttle = 0
        self.counter = 0


    def run(self, cam_img):
        '''
        main runloop of the CV controller.

        :param cam_img: the camerate image, an RGB numpy array
        :return: tuple of steering, throttle, and the telemetry image.

        If overlay_image is True, then the output image
        includes an overlay that shows how the 
        algorithm is working; otherwise the image
        is just passed-through untouched. 
        '''
        if cam_img is None:
            return 0, 0, None

        self.counter += 1

        # show some diagnostics
        if self.overlay_image:
            # draw onto a COPY of the image so we don't alter the original
            cam_img = self.overlay_display(np.copy(cam_img))

        return self.steering, self.throttle, cam_img

    def overlay_display(self, img):
        '''
        draw on top the given image.
        show some values we are using for control

        :param img: the image to draw on as a numpy array
        :return: the image with overlay drawn
        '''
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