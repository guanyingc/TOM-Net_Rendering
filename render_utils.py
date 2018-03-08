from scipy.misc import imread, imsave
import matplotlib
import numpy as np
import os

def makeFile(f):
    if not os.path.exists(f):
        os.makedirs(f)

def checkEmpty(a_list):
    if len(a_list) == 0:
        raise Exception('Empty list')

def readImgListFromDir(input_dir, exts=['.jpg'], sort=False, add_path=True):
    f_names = os.listdir(input_dir)
    img_names = []
    for ext in exts:
        img_names += [f for f in f_names if f.endswith(ext)]
    checkEmpty(img_names)
    if add_path: 
        img_list = ['%s' % os.path.join(input_dir, name) for name in img_names]
    else:
        img_list = img_names
    if sort == True:
        img_list.sort(key=natural_keys)
    return img_list

import re
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def readImgFromList(img_list):
    print('Reading images from list')
    checkEmpty(img_list)
    imgs = []
    for i, img_name in enumerate(img_list):
        I = imread(img_name)
        imgs.append(I)
    return imgs

def rgb2gray(rgb):
    if len(rgb.shape) <= 2:
        return rgb
    return np.uint8(np.dot(rgb[...,:], [0.299, 0.587, 0.114]))

def listRgb2Gray(imgs):
    print('Converting list of rgb images to gray images')
    for i in range(len(imgs)):
        imgs[i] = rgb2gray(imgs[i])

## Helper functions for flow
def flowToMap(F_mag, F_dir):
    sz = F_mag.shape
    flow_color = np.zeros((sz[0], sz[1], 3), dtype=float)
    flow_color[:,:,0] = (F_dir+np.pi) / (2 * np.pi)
    f_dir =(F_dir+np.pi) / (2 * np.pi)
    flow_color[:,:,1] = F_mag / (F_mag.shape[0]*0.5)
    flow_color[:,:,2] = 1
    flow_color = matplotlib.colors.hsv_to_rgb(flow_color)*255
    return flow_color

def flowToColor(flow):
    F_dx = flow[:,:,1].copy().astype(float)
    F_dy = flow[:,:,0].copy().astype(float)
    F_mag = np.sqrt(np.power(F_dx, 2) + np.power(F_dy, 2))
    F_dir = np.arctan2(F_dy, F_dx)
    flow_color = flowToMap(F_mag, F_dir)
    return flow_color.astype(np.uint8)

def writeFlowBinary(flow, filename, short=True):
    if short:
        flow = flow.astype(np.int16)
    else:
        flow = flow.astype(np.float32)
    with open(filename, 'wb') as f:
        magic = np.array([202021.25], dtype=np.float32) 
        h_w   = np.array([flow.shape[0], flow.shape[1]], dtype=np.int32)
        magic.tofile(f)
        h_w.tofile(f)
        flow.tofile(f)

