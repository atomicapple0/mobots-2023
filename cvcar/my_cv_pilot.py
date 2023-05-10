import cv2
import numpy as np
from detect_line import CENTER_COL
from time import time, sleep
from detect_line import detect_line

def resizer(img):
    h,w,z = img.shape
    crop = img[int(.85*h):int(1*h),int(.3*w):int(.7*w),:]
    # resize to (320, 240)
    res = cv2.resize(crop, (320, 240))
    # print(f"img shape {img.shape}, crop.shape {crop.shape}, res.shape {res.shape}")
    return res

class MockCvPilot:
    def __init__(self, pid, cfg):
        self.steering = 0
        self.throttle = 0
        self.init_time = time()
        self.elapsed = 0
        self.errs = []
        pass
    
    def time(self):
        return self.elapsed
    
    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        start = time()

        img = resizer(cam_img)
        processed, blobs = detect_line(img)
        if blobs:
            blob = blobs[0]
        else:
            self.steering = self.steering
            self.throttle = self.throttle
            err = CENTER_COL - blob.center
            self.errs.append(err)

            p_err = self.errs[-1]
            d_err = self.errs[-1] - self.errs[-2]
            i_err = np.mean(self.errs[max(len(self.errs)-10,0):]) / 10

            k_p, k_d, k_i = 0, 0, 0
            k_p = 28 / 100
            k_i = 0 / 100
            k_d = 12  / 100
            self.steering = k_p * p_err + k_d * d_err + k_i * i_err

        end = time()
        sleep(.001)
        print(f"done steering:{self.steering:.2f} throttle:{self.throttle:.2f} in err:{self.errs[-1]} {end-start:.2f} sec")
        
        return self.steering, self.throttle, processed