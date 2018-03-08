import sys, os, argparse
import numpy as np
from scipy.misc import imread, imsave
import render_utils as utils

parser = argparse.ArgumentParser()
parser.add_argument('--in_root',  default='/home/gein/Code/rendering_script/test/test_graycode/')
parser.add_argument('--in_dir',   default='graycode')
parser.add_argument('--out_dir',  default='')
parser.add_argument('--reload',   action='store_false', default=False)
parser.add_argument('--mute',     action='store_false', default=True)
args = parser.parse_args()

class FlowCalibrator:
    def __init__(self, imgs=[]):
        self.imgs = imgs
        if imgs != []:
            self.h = imgs[0].shape[0]
            self.w = imgs[0].shape[1]
            if not args.mute:
                print('Image height width %dX%d' % (self.h, self.w))
            self.mask = imgs[0]
            self.rho  = imgs[1]

    def obtainImgBinaryCode(self, sub_imgs, h, w):
        if not args.mute:
            print('Obtaining Image binary code (%dx%dx%d)' % (len(sub_imgs), h,w))
        binary_code = np.chararray((h, w)); binary_code[:]=''
        for img in sub_imgs:
            bit_code = np.chararray((h,w), itemsize=1)
            bit_code[img >  190] = '1'
            bit_code[img <= 190] = '0'
            binary_code = binary_code + bit_code
        if not args.mute:
            print(binary_code[:2,:2], len(binary_code[0,0]))
        return binary_code

    def findCorrespondence(self):
        self.flow_x_idx = np.zeros((self.h, self.w), dtype=np.int64)
        self.flow_y_idx = np.zeros((self.h, self.w), dtype=np.int64)
        self.x_grid = np.tile(np.linspace(0, self.w-1, self.w), (self.h, 1)).astype(int)
        self.y_grid = np.tile(np.linspace(0, self.h-1, self.h), (self.w, 1)).T.astype(int)
        if not args.mute:
            print('Finding correspondence with graycode pattern')
        self.img_code  = self.obtainImgBinaryCode(self.imgs[2:], self.h, self.w)
        self.findCorrespondenceGraycode()

    def findCorrespondenceGraycode(self):
        digit_code = [int(code, 2) for code in self.img_code.flatten()]
        digit_code = np.array(digit_code).reshape(self.h, self.w)
        self.flow_x_idx = np.mod(digit_code, self.w)
        self.flow_y_idx = np.divide(digit_code, self.w)

        self.flow_x_idx -= self.x_grid
        self.flow_y_idx -= self.y_grid
        self.flow_x_idx[self.mask >= 200] = 0
        self.flow_y_idx[self.mask >= 200] = 0
        self.saveFlow(self.flow_x_idx, self.flow_y_idx, self.rho)

    def flowWithRho(self, flow_color, rho):
        h = rho.shape[0]
        w = rho.shape[1]
        flow_rho = flow_color * np.tile(rho.reshape(h,w,1), (1,1,3)).astype(float) /255
        return flow_rho.astype(np.uint8)

    def writeFlowBinary(self, flow, filename):
        flow = flow.astype(np.float32)
        with open(filename, 'wb') as f:
            magic = np.array([202021.25], dtype=np.float32) 
            h_w   = np.array([flow.shape[0], flow.shape[1]], dtype=np.int32)
            magic.tofile(f)
            h_w.tofile(f)
            flow.tofile(f)

    def saveFlow(self, flow_x, flow_y, rho):
        h = flow_x.shape[0]
        w = flow_x.shape[1]
        flow = np.zeros((h,w,2))
        flow[:,:,1] = flow_x; flow[:,:,0] = flow_y
        if not args.mute:
            print(args.out_name)
        flow_color = utils.flowToColor(flow)
        imsave(os.path.join(args.out_dir, args.out_name + '.png'), self.flowWithRho(flow_color, rho))
        utils.writeFlowBinary(flow, os.path.join(args.out_dir, args.out_name + '.flo'))

def readImgOrLoadNpy():
    if args.reload and os.path.exists(os.path.join(args.in_root, 'imgs.npy')):
        if not args.mute:
            print('Loading imgs.npy')
        imgs = np.load(os.path.join(args.in_root, 'imgs.npy'))
    else:
        exts = ['.png', '.jpg']
        img_list = utils.readImgListFromDir(args.in_dir, exts, sort=True)
        if not args.mute:
            print('Totaling %d images' % len(img_list))
        imgs = utils.readImgFromList(img_list)
        utils.listRgb2Gray(imgs)
        np.save(os.path.join(args.in_root, 'imgs.npy'), imgs)
    return imgs

def checkImgNumber(imgs):
    img_num = len(imgs)
    h = imgs[0].shape[0]
    w = imgs[0].shape[1]
    if not (img_num == 2 + int(np.log2(h)) + int(np.log2(w))):
        raise Exception('Not correct image number: %dX%dX%d' % (img_num, h, w))

if __name__ == '__main__':
    args.in_dir  = os.path.join(args.in_root, args.in_dir)
    imgs = readImgOrLoadNpy()
    checkImgNumber(imgs)

    args.out_name = '%s_flow' % (os.path.basename(args.in_dir))
    if args.out_dir == '':
        args.out_dir = os.path.join(args.in_root, 'correspondence')
    print(args.out_dir)
    utils.makeFile(args.out_dir)
    calibrator = FlowCalibrator(imgs)
    calibrator.findCorrespondence()

