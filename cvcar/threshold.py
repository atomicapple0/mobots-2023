from time import time
import cv2
import numpy as np
from matplotlib import pyplot as plt
from utils import *

def threshold(img):
    # threshold in yuv space
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

    # threshold in yuv space
    yuv = yuv[:,:,0] / 255.0
    yuv = yuv > .7

    # hmmm
    # yuv2 = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    # yuv2 = yuv[:,:,2] / 255.0
    # yuv2 = relu(1-yuv, .7)
    # return yuv2

    return yuv
