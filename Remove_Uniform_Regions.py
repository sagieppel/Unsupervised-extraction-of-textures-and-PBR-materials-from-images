import os
import cv2
import shutil
import numpy as np
from scipy.stats import ks_2samp, mannwhitneyu
import scipy
from sklearn.metrics.pairwise import cosine_similarity
import json
##################################################################################33333

# Identify uniform region to remove textures which are just black/white or uniform colors

#################################################################################

image_dir = "extracted_textures/texture_large" # image of textures to filtered
#image_dir2 = "../outdir_6/texture_small/"
out_dir = "extracted_textures/filtered_smooth_texture/" # image were the textures that does not pass the filtering will be moved to
if not os.path.isdir(out_dir): os.mkdir(out_dir)
for ii,fl in enumerate(os.listdir(image_dir)):
    print(ii,fl)
    im = cv2.imread(image_dir+"/"+fl)
    if im is None:
        print(image_dir+"/"+fl)
        os.remove(image_dir + "/" + fl)
        continue
        x=3
 #   im2 = cv2.imread(image_dir2 + "/" + fl)
    h = int(im.shape[0]/2)
    w = int(im.shape[1]/2)
    fin=False
    for  dx in range(2):
        for dy in range(2):
          crop = im[dy*h:dy*h+h,dx*w:dx*w+w]
          cv2.destroyAllWindows()
          if crop.std()<3.5 or (crop.std()<6 and  crop.mean()>245):
              fin=True
              break
              cv2.imshow("1:  "+str(crop.std()),im);
 #             cv2.imshow("2:  " + str(crop.std()), im2);
              cv2.waitKey()
          #     break
          # if crop.mean()<10:
          #     cv2.imshow("2 "+str(crop.mean()),im);
          #     cv2.waitKey()
          #     break
          # if crop.std()/(2+crop.mean())<0.03:
          #     cv2.imshow("3 "+str(crop.std()/(2+crop.mean())),im);
          #     cv2.waitKey()
          #     break
        if fin: break
    if fin:
        shutil.move(image_dir+"/"+fl,out_dir)
        print(image_dir + "/" + fl, "->", out_dir)

