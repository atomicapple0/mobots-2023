import cv2
import numpy as np
from my_cv_pilot import *
from matplotlib import pyplot as plt

def resizer(img):
    h,w,z = img.shape
    crop = img[int(.85*h):int(1*h),int(.3*w):int(.7*w),:]
    # resize to (320, 240)
    res = cv2.resize(crop, (320, 240))
    # print(f"img shape {img.shape}, crop.shape {crop.shape}, res.shape {res.shape}")
    return res

def log(s):
    if True:
        print(s)

def save_img(filename, img):
    # if filename.startswith(YUV_DIR):
    #     plt.imshow(img)
    #     plt.show()
    # return
    if not cv2.imwrite(filename, img):
        raise Exception("Could not write image to {}", filename)

def flip_stack_unfloat(img):
    return np.flipud(np.stack((img,)*3, axis=-1) * 255).astype('uint8')

def relu(img, thresh):
    assert img.dtype == np.float32
    diff = img - thresh
    relud = (diff * (diff > 0))
    return relud + thresh

def assemble_imgs(img_list):
    max_width = 0
    total_height = 200  # padding
    for img in img_list:
        if img.shape[1] > max_width:
            max_width = img.shape[1]
        total_height += img.shape[0]

    # create a new array with a size large enough to contain all the images
    final_image = np.zeros((total_height, max_width, 3), dtype=np.uint8)

    current_y = 0  # keep track of where your current image was last placed in the y coordinate
    for image in img_list:
        # add an image to the final array and increment the y coordinate
        image = np.hstack((image, np.zeros((image.shape[0], max_width - image.shape[1], 3))))
        final_image[current_y:current_y + image.shape[0], :, :] = image
        current_y += image.shape[0]
    return final_image

def assemble_imgs_horiz(img_list):
    new_img_list = []
    total_width = 0
    for img in img_list:
        if len(img.shape) == 2:
            new_img_list.append(flip_stack_unfloat(img))
        else:
            new_img_list.append(np.flipud(img))
        new_img_list[-1] = new_img_list[-1].transpose(1, 0, 2)
        total_width += new_img_list[-1].shape[0]
    ass = assemble_imgs(new_img_list)
    return ass[:total_width,:].transpose(1, 0, 2)
