import cv2
import numpy as np
from utils import *
import os
from matplotlib import pyplot as plt

def threshold(img):
    # ksize
    ksize = (5, 5)
    
    # Using cv2.blur() method 
    img = cv2.blur(img, ksize) 

    # threshold in yuv space
    yuv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # threshold in yuv space
    # plt.imshow(yuv[:,:,0]); plt.show()
    # plt.imshow(yuv[:,:,1]); plt.show()
    # hmm = 255-yuv[:,:,1]
    # yuv = hmm / 255.0
    # yuv = yuv > .65
    nice = yuv[:,:,0] > 80
    plt.imshow(nice); plt.show()

    return nice
    
    # hmmm
    # yuv2 = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    # plt.imshow(yuv[:,:,0]); plt.show()
    # plt.imshow(yuv[:,:,1]); plt.show()
    # plt.imshow(yuv[:,:,2]); plt.show()
    # yuv2 = yuv[:,:,0] / 255.0
    # yuv2 = relu(1-yuv, .7)
    # return yuv2[:,:,0] > .8

    return yuv.astype('float32')

from utils import save_img, flip_stack_unfloat

if __name__ == '__main__':
    src_dir = "imgs/input/"
    dest_dir = "imgs/thresholded/"
    jpgs = [jpg for jpg in os.listdir(src_dir) if jpg.endswith('jpg') or jpg.endswith('png')]
    for idx,jpg in enumerate(jpgs):
        src_file = src_dir + jpg
        print(f'reading: {src_file}')
        img = cv2.imread(src_file)
        thresh = threshold(np.array(img))
        save_img(dest_dir + jpg, np.flipud(flip_stack_unfloat(thresh)))