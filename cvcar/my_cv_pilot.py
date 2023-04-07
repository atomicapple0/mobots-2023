import cv2
import numpy as np
import logging
import math

logger = logging.getLogger(__name__)

class BasicController:
    def __init__(self):
        self.k_p = 1
    
    # given offset from centerline, return steering and throttle
    def calculate_cmd(self, offset):
        steering = -self.k_p * offset
        throttle = .1 if abs(steering) < .1 else .05
        return steering, throttle

def relu(img, thresh):
    assert img.dtype == np.float64
    diff = img - thresh
    relud = (diff * (diff > 0))
    return relud + thresh

class MockCvPilot:
    def __init__(self, pid, cfg):
        self.pid_st = pid
        self.overlay_image = cfg.OVERLAY_IMAGE
        self.steering = 0
        self.throttle = 0
        self.counter = 0
        self.offset = 0
        self.curv = 0

    def run(self, cam_img):
        if cam_img is None:
            return 0, 0, None

        self.counter += 1

        cam_img = self.process_img(cam_img)
        cam_img = self.annotate_img(cam_img)

        # # run controller
        # self.steering, self.throttle = self.cntrl.calculate_cmd(self.offset)

        return self.steering, self.throttle, cam_img

    def annotate_img(self, img, **kwargs):
        img = np.copy(img)

        # some text to show on the overlay
        display_str = []
        display_str.append(f"STEERING:{self.steering:.1f}")
        display_str.append(f"THROTTLE:{self.throttle:.2f}")
        display_str.append(f"OFFSET:{self.offset:.1f}")
        display_str.append(f"CURV:{self.curv:.1f}")

        lineheight = 25
        y = lineheight
        x = lineheight
        for s in display_str:
            # green text with black outline so it shows up on any background
            cv2.putText(img, s, color=(0, 0, 0), org=(x ,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=3)
            cv2.putText(img, s, color=(0, 255, 0), org=(x ,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, thickness=1)
            y += lineheight

        return img

    def process_img(self, img):
        # assume img is 1024 x 768
        assert math.isclose(1024 / 768, img.shape[1] / img.shape[0], rel_tol=.1)

        resize = img.shape[1] / 1024

        # order: tr, tl, bl, br
        src = [(650,370), (370,370), (0,700), (1000,730)]
        src = [(int(resize*x), int(resize*y)) for (x,y) in src]
        dst = [(10, 34), (-10, 34), (-10, 0), (10, 0)]
        dst = [(int(10*(x + 30)), int(10*y)) for (x,y) in dst]

        src_np = np.array(src, dtype=np.float32)
        dst_np = np.array(dst, dtype=np.float32)

        # colors = [
        #     (0, 0, 255),  # green
        #     (0, 255, 0),  # blue
        #     (255, 0, 0),  # red
        #     (255, 255, 0),  # yellow
        # ]
        # for cnr_idx, (x, y) in enumerate(src):
        #     cv2.circle(img, (x, y), 10, colors[cnr_idx], -1)

        # inverse projective map
        M = cv2.getPerspectiveTransform(src_np, dst_np)
        warped_viz = cv2.warpPerspective(img, M, (600, 1000), flags=cv2.INTER_LINEAR)
        warped = cv2.warpPerspective(img, M, (600, 1000), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

        # threshold in yuv space
        yuv = cv2.cvtColor(warped, cv2.COLOR_BGR2YUV)
        yuv = yuv[:,:,0] / 255.0
        yuv = relu(yuv, .7)

        # resize image to (30,50), then crop to (30,20)
        resized = cv2.resize(yuv, (30,50), interpolation = cv2.INTER_AREA)
        resized = resized[:20,:]

        # tophat convolve
        tophat = np.array([-1, -1, 2, 2, -1, -1])
        conv = cv2.filter2D(src=resized, ddepth=-1, kernel=tophat)

        # relu out negative response from kernel
        relud = relu(conv, 0)

        # fit a quadratic
        flattened = relud.reshape(-1)
        indices = list(np.ndindex(relud.shape[:]))
        pts = np.c_[indices, flattened]

        coeffs = np.polyfit(x=pts[:,0],y=pts[:,1],w=pts[:,2], deg=2)
        poly = np.poly1d(coeffs)

        yp = np.linspace(0,30,100) # 100 pts between (0,30)
        xp = poly(yp)

        xp = 20 * xp
        yp = 20 * yp
        
        curve = np.column_stack((xp.astype(np.int32), yp.astype(np.int32)))
        cv2.polylines(warped_viz, [curve], False, (0,255,255), thickness=2)

        # compute curvilinear position and curvature at 0
        self.offset = poly(0)
        a,b,c = coeffs
        self.curv = (1 + b ** 2) ** 1.5 / abs(2*a)

        return cv2.flip(warped_viz, 0)










