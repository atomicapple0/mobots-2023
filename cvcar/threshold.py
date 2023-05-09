from time import time
import cv2
import numpy as np
from matplotlib import pyplot as plt
from utils import *

def threshold(img):
    # ksize
    ksize = (5, 5)
    
    # Using cv2.blur() method 
    img = cv2.blur(img, ksize) 

    # threshold in yuv space
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)

    # threshold in yuv space
    # plt.imshow(yuv[:,:,0]); plt.show()
    # plt.imshow(yuv[:,:,1]); plt.show()
    hmm = 255-yuv[:,:,1]
    yuv = hmm / 255.0
    yuv = yuv > .75
    
    # hmmm
    # yuv2 = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    # yuv2 = yuv[:,:,2] / 255.0
    # yuv2 = relu(1-yuv, .7)
    # return yuv2

    return yuv.astype('float32')