# Turn folder of textures images into seamless textures  (by adding mirror symetry)
import os

import cv2
import numpy as np


def turn_texture(im): # turn texture image to seamless
    im = np.concatenate([im,im[::-1]],axis=0)
    im = np.concatenate([im, im[:,::-1]], axis=1)
    return(im)


#    Input parameter
in_dir="extracted_textures/texture_large/" # input texture folder
out_dir="seamless_texture_large/"# output seamless texture folder
os.makedirs(out_dir, exist_ok=True)

#---Turn all files in in_dir to seamless
for fl in os.listdir(in_dir):
    print("reading ",in_dir+"/"+fl)
    im = cv2.imread(in_dir+"/"+fl)
    im=turn_texture(im)
    print("writing ", out_dir + "/" + fl)
    cv2.imwrite(out_dir+"/"+fl,im)