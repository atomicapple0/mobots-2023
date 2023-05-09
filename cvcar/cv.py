from time import time
import cv2
import numpy as np
import math
from my_cv_pilot import *
from matplotlib import pyplot as plt
from threshold import threshold
from utils import *

INPUT_DIR = "imgs/input/"
WARPED_DIR = "imgs/warped/"
YUV_DIR = "imgs/yuv/"
THRESHOLDED_DIR = "imgs/thresholded/"
TOPHAT_DIR = "imgs/tophat/"
RELUD_DIR = "imgs/relud/"
FINAL_DIR = "imgs/final/"

LOOK_FOR_SPLIT = 0

GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
CYAN_OR_YELLOW = (0, 255, 255)

CURR_BIAS_IDX = 1

LEFT_30 = 12
RIGHT_30 = 18
BIAS_LEFT_RIGHT_DIFF = 1

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

def process_img(img, filename = None):
    global LOOK_FOR_SPLIT, CURR_BIAS_IDX
    # assume img is 1024 x 768
    assert math.isclose(1024 / 768, img.shape[1] / img.shape[0], rel_tol=.1)

    LOOK_FOR_SPLIT -= 1
    
    resize = img.shape[1] / 1024

    # order: tr, tl, bl, br
    src = [(675,384), (338,384), (0,700), (1023,730)]
    src = [(int(resize*x), int(resize*y)) for (x,y) in src]
    dst = [(10, 34), (-10, 34), (-10, 0), (10, 0)]
    dst = [(int(10*(x + 30)), int(10*y)) for (x,y) in dst]
    dst = [(int(x//10*3), int(y//10*3)) for (x,y) in dst]

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
    # cloned_img = np.array(img)
    cloned_img = img
    warped = cv2.warpPerspective(cloned_img, M, (600//10*3, 1000//10*3), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=GREEN)
    out_of_bounds = warped[:,:] == GREEN

    # if filename:
    #     save_img(WARPED_DIR + filename, assemble_imgs([img, np.flipud(warped)]))

    # threshold in yuv space
    yuv = threshold(warped)
    relud = yuv

    # if filename:
    #     save_img(THRESHOLDED_DIR + filename, (yuv * 255).astype('uint8'))

    # resize image to (30,50), then crop to (30,10)
    # resized = cv2.resize(yuv, (30,50), interpolation = cv2.INTER_AREA)
    # resized = resized[:20,:]

    # out_of_bounds = cv2.resize(out_of_bounds.astype("uint8"), (30,50), interpolation = cv2.INTER_NEAREST)
    # out_of_bounds = out_of_bounds[:10,:]

    # # tophat convolve
    # tophat = np.array([-1, -1, 2, 2, -1, -1])
    # conv = cv2.filter2D(src=resized, ddepth=-1, kernel=tophat)

    # conv[out_of_bounds] = 0

    # if filename:
    #     save_img(TOPHAT_DIR + filename, (conv * 255).astype('uint8'))

    # # relu out negative response from kernel
    # relud = relu(conv, 0)

    # if filename:
    #     save_img(RELUD_DIR + filename, (relud * 255).astype('uint8'))

    # # depending on bias eliminate left or right pixels
    # bias = BIASES[CURR_BIAS_IDX]

    # def is_peak(img, r, c):
    #     if c == 0 or c == img.shape[1] - 1:
    #         return False
    #     return img[r,c] > .08 and img[r,c-1] < .9*img[r,c] and img[r,c+1] < .9*img[r,c]

    # left_off = LEFT_30 + BIAS_LEFT_RIGHT_DIFF if bias == RIGHT else LEFT_30
    # right_off = RIGHT_30 - BIAS_LEFT_RIGHT_DIFF if bias == LEFT else RIGHT_30
    # col_iter = list(range(left_off,right_off))
    # # if robot is biased to the left
    # if bias == LEFT:
    #     # iterate from left to right
    #     pass
    # else:
    #     # iterate from left to right
    #     col_iter = [relud.shape[1] - c - 1 for c in col_iter]
    
    # centerline = relud.shape[1] / 2
    # col_center_by_rows = []
    # num_is_peaked = 0
    # iterate through the rows
    # for r in range(relud.shape[0]):
    #     # have we found a peak corresponding to a lane
    #     is_peaked = 0
    #     col_center_by_row = 0
    #     col_weights_by_row = 0

    #     for c in col_iter:
    #         if is_peaked:
    #             is_peaked += 1
    #         if is_peak(relud,r,c):
    #             log(f"found first peak on col {r} in row {c}")
    #             is_peaked += 1
    #         if is_peaked > 3:
    #             relud[r,c] = 0
    #         col_center_by_row += relud[r,c] * c
    #         col_weights_by_row += relud[r,c]
    #     log(f"{col_center_by_row}")
    #     log(f"{col_weights_by_row}")
    #     col_center = col_center_by_row / col_weights_by_row
    #     # if col_center is NaN, then set to middle
    #     if math.isnan(col_center):
    #         col_center = centerline
    #     col_center_by_rows.append(col_center)
    #     if is_peaked:
    #         num_is_peaked += 1
    
    # if LOOK_FOR_SPLIT <= 0 and num_is_peaked > 3:
    #     CURR_BIAS_IDX += 1
    #     LOOK_FOR_SPLIT = 100

    
    # fit a quadratic
    crop = relud[:100,:]
    flattened = crop.reshape(-1)
    indices = list(np.ndindex(crop.shape[:]))
    pts = np.c_[indices, flattened]

    coeffs = np.polyfit(x=pts[:,0],y=pts[:,1],w=pts[:,2], deg=2)
    poly = np.poly1d(coeffs)

    yp = np.linspace(0,100,100) # 100 pts between (0,30)
    xp = poly(yp)

    curve = np.column_stack((xp.astype(np.int32), yp.astype(np.int32)))
    relud = np.stack((relud, relud, relud), axis=-1).astype(np.float32)
    cv2.polylines(relud, [curve], False, (1.0,0,1.0), thickness=2)
    cv2.polylines(warped, [curve], False, (0,255,255), thickness=2)

    # compute curvilinear position and curvature at 0
    # self.offset = poly(0)
    a,b,c = coeffs
    # self.curv = (1 + b ** 2) ** 1.5 / abs(2*a)

    plt.imshow(crop, origin='lower')
    plt.show()
    plt.imshow(relud, origin='lower')
    plt.show()
    plt.imshow(warped, origin='lower')
    plt.show()
        
    avg_col = int(np.mean(col_center_by_rows))
    
    abs_pct_offset = avg_col / relud.shape[1]
    offset_from_center = abs_pct_offset - .5

    steering = offset_from_center * 100
    throttle = 0

    log(col_center_by_rows)
    log(img.shape)
    log(relud.shape)

    # height = int(img.shape[0] / relud.shape[0] * relud.shape[1])
    # relud_flipped = np.flipud(relud)
    # relud_three_channel = (np.stack((relud_flipped,)*3, axis=-1) * 255).astype('uint8')
    # print(f"avg col is {avg_col} of {relud.shape[1]}")
    # relud_three_channel[:,avg_col] = (255,255,0)
    # relud_big = cv2.resize(relud_three_channel, dsize=(height,img.shape[0]), interpolation=cv2.INTER_NEAREST)

    log(f"hmm is {offset_from_center}")
    avg_col_warped = int(abs_pct_offset * warped.shape[1])
    log(f"avg col is {avg_col} of {relud.shape[1]}")
    print(f"avg col is {avg_col_warped} of {warped.shape[1]}")
    
    
    # dims are 100 x 20
    # horizontal no look further bar
    warped[20,:] = MAGENTA
    # vertical left right bars
    warped[:,left_off * warped.shape[1] //30] = MAGENTA
    warped[:,right_off *warped.shape[1] // 30] = MAGENTA
    # vertical centerline bar
    warped[:10,warped.shape[1]//2] = MAGENTA
    # left right bias circle
    warped[-15:-5,5:10] = MAGENTA if bias == LEFT else GREEN
    # looking for split line
    split = max(0,LOOK_FOR_SPLIT)
    split = min(50,split)
    log(f"split is {split} and {LOOK_FOR_SPLIT}")
    warped[-2,:split] = CYAN_OR_YELLOW

    warped[:,avg_col_warped] = GREEN

    # log(relud_big.shape)
    # plt.imshow(relud)
    # plt.show()
    final_img = assemble_imgs_horiz([yuv, relud, warped])

    if filename:
        save_img(FINAL_DIR + filename, final_img)

    return final_img, steering, throttle
