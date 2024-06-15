import os
import cv2
import numpy as np

# Display PBR material maps one by one
def display_pbr_dir(pbr_dir ):
    ls=[]
    print("num_pbrs", len(os.listdir(pbr_dir)))
    for dr in os.listdir(pbr_dir):
        cv2.destroyAllWindows()

        for fl in os.listdir(pbr_dir + "/" + dr + "/"):
            sdir = pbr_dir + "/" + dr + "/"
            # normal_path = sdir + "Normal.jpg"
            im = cv2.imread(sdir+"/"+fl)
            if im is None: continue
            cv2.imshow(fl,im); cv2.waitKey()
            #if fl not in ls: ls.append(fl)
            # print(ls)
            # #print(sdir + "/" +fl)
            # map = cv2.imread(sdir + "/" +fl)
            # #  cv2.imshow("", norm);cv2.waitKey()
            # norm = norm.astype(np.float32)
            # # norm=500-511
            # ['AmbientColor.jpg', 'checked.txt', 'Height.jpg', 'Roughness.jpg', 'Normal.jpg', 'OriginColor.jpg','Metallic.jpg']
            # # print("std sqr", (norm ** 2).sum(2).std() / ((norm ** 2).sum(2).mean()), " Mean=",((norm ** 2).sum(2).mean()))
            # # print("std lin", (norm).sum(2).std() / (norm).sum(2).mean(), " Mean=", (norm.sum(2).mean()))

            print(fl)
display_pbr_dir(pbr_dir = "/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/GeneratedPBRs_And_Textures/pbr_openimages_0_large/")#generated_pbr_3/")