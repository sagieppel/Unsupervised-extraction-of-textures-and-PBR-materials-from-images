# Turn folder of PBR materials into seamless (by adding mirror symetry)
import os

import cv2
import numpy as np


def turn_texture(im): # turn texture image to seamless
    im = np.concatenate([im,im[::-1]],axis=0)
    im = np.concatenate([im, im[:,::-1]], axis=1)
    return(im)


#    Input parameter
in_dir="extracted_pbrs/" # input texture folder
out_dir="seamless_pbrs/"# output seamless texture folder
os.makedirs(out_dir, exist_ok=True)

#---Turn all files in in_dir to seamless
for dr in  os.listdir(in_dir):
    insubdir = in_dir + "/" + dr + "/"
    outsubdir = out_dir + "/" + dr + "/"
    os.makedirs(outsubdir, exist_ok=True)

    for fl in os.listdir(insubdir):
        print("reading ",insubdir+"/"+fl)
        if ".png" in fl or ".jpg" in fl or ".tif" in fl:
            im = cv2.imread(insubdir+"/"+fl, cv2.IMREAD_UNCHANGED)
            im = turn_texture(im)
            print("writing ", out_dir + "/" + fl)
            cv2.imwrite(outsubdir+"/"+fl,im)