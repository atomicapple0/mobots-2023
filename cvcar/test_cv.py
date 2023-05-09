import os
import cv2
from matplotlib import pyplot as plt
import numpy as np
from time import time
from cv import THRESHOLDED_DIR, process_img, save_img, flip_stack_unfloat
from new_cv import new_cv
from threshold import *
from utils import *
from cv import *

src_dir = "imgs/input/"
misc_dir = "imgs/misc/"
jpgs = [jpg for jpg in os.listdir(src_dir) if jpg.endswith('jpg') or jpg.endswith('png')]
jpgs.sort()
if len(jpgs) == 0:
    print("no jpgs in imgs dir")

print(jpgs)

FINAL_DIR = "imgs/final/"
for idx,jpg in enumerate(jpgs):
    src_file = src_dir + jpg

    img = cv2.imread(src_file)

    print(f"---- processing {jpg} ----")
    # res, _ = new_cv(img)
    # save_img(FINAL_DIR + jpg, res)
    thresh = threshold(np.array(img))
    save_img(THRESHOLDED_DIR + jpg, np.flipud(flip_stack_unfloat(thresh)))

    start_time = time()
    res, steering, throttle = process_img(img, filename=jpg)
    end_time = time()
    print(f"{end_time - start_time} seconds elpased")
    # print(f"processed {jpg} steering {steering} and throttle {throttle}")

    # print("dims of img: ", img.shape)
    # print("dims of res: ", res.shape)

    # exit(1)

    # plt.imshow(res)
    # plt.show()
    