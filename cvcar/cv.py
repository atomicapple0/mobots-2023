import cv2
import numpy as np
import math
from my_cv_pilot import *

CURR_BIAS_IDX = 0

LEFT = 0
RIGHT = 1
BIASES = [
    LEFT,
    RIGHT,
    LEFT,
    RIGHT,
    RIGHT,
    LEFT,
    RIGHT,
    RIGHT,
    LEFT,
    RIGHT,
]

def relu(img, thresh):
    assert img.dtype == np.float64
    diff = img - thresh
    relud = (diff * (diff > 0))
    return relud + thresh

def process_img(img):
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

    # depending on bias eliminate left or right pixels
    bias = BIASES[CURR_BIAS_IDX]

    col_iter = list(range(0,relud.shape[1]))

    def is_peak(row, j):
        if j == 0 or j == len(row) - 1:
            return False
        return row[j] > .08 and row[j-1] < .9*row[j] and row[j+1] < .9*row[j]

    # if robot is biased to the left
    if bias == LEFT:
        # iterate from left to right
        pass
    else:
        # iterate from left to right
        col_iter = [relud.shape[1] - c - 1 for c in range(col_iter)]

    col_center_by_rows = []
    # iterate through the rows
    for r in range(relud.shape[0]):
        # have we found a peak corresponding to a lane
        is_peaked = 0
        col_center_by_row = 0

        for c in col_iter:
            if is_peaked:
                is_peaked += 1
            if is_peak(relud[r],c):
                print(f"found first peak on col {r} in row {c}")
                is_peaked += 1
            if is_peaked > 3:
                relud[r][c] = 0
            col_center_by_row = relud[r][c] * c

        col_center_by_rows.append(col_center_by_row / relud.shape[1])
    
    avg_col = np.avg(np.array(col_center_by_rows))
            
    relud[:,avg_col] = 1
    offset_from_center = (relud.shape[1] / 2 - avg_col) / relud.shape[1]

    steering = offset_from_center * 100

    return relud, steering