import shutil

import cv2
import os
import numpy as np
########################################################################################################

# Create New PBRs by mixing two or more PBR map

####################################################################################################################################

if __name__ == '__main__':
    pbr_dir="extracted_pbrs/"
    merge_dir="mixed_pbrs/"
    # if os.path.exists(merge_dir):
    #      shutil.rmtree(merge_dir)
    if not os.path.exists(merge_dir): os.mkdir(merge_dir)
    pbr_list = []
    for dr in os.listdir(pbr_dir):
        pbr_list.append(pbr_dir+"/"+dr)



    for itr in range(8):
       outsubdir=merge_dir + "/" + str(itr) +"/"
       if os.path.exists(outsubdir ):continue
       if not os.path.exists(outsubdir): os.mkdir(outsubdir)
       pbr2merge=[]# select pbrs to merge
       files_names = ""
       # select folders to merge
       while(True): # select pbrs to merge
           path = pbr_list[np.random.randint(len(pbr_list))]
           print(path)
           files_names += "\n" + path
           pbr2merge.append(path)
           if np.random.rand()<0.5 and len(pbr2merge)>1:
               break

       # Choose mode
       r=np.random.rand()
       if r<0.28:
           mode = "equal"# weighted distrubutio same weights to all propery
           eqweights = np.random.rand(len(pbr2merge))
       elif r<0.55:
           mode="max" # max value of mixed maps
       else:
           mode="flexible"# weighted distrubutio different weights to each propery
       files_names+="\n Mode:"+str(mode)


       # collect maps
       maps = {}

       size0=[]# size use for all maps (based on the first map read)
       for i in range(len(pbr2merge)): # collect maps to each property
             for fl in os.listdir(pbr2merge[i]):

                        if ("Normal" in fl) or ("Color" in fl): # read as 3 channels
                              im = cv2.imread(pbr2merge[i]+"/"+fl)
                            #  cv2.imshow(pbr2merge[i]+"/"+fl,im);cv2.waitKey()
                        else: # read as one channel
                              im = cv2.imread(pbr2merge[i] + "/" + fl,0)
                        if im is None: continue

                        if not fl in maps:
                            maps[fl] = []
                            maps[fl + "_weights"] = []
                        if len(size0)==0: # set main size
                            size0 = im.shape
                        if im.shape[0] != size0[0]  or  im.shape[1] != size0[1]:
                            im = cv2.resize(im,[size0[1],size0[0]])
                        maps[fl].append(im)
                        if mode=="equal":
                              maps[fl+"_weights"].append(eqweights[i])
                        else:
                              maps[fl + "_weights"].append(np.random.rand())
       # merge maps:
       for ky in maps:
           if "_weights" in ky: continue
           # Weights array
           weights = np.array(maps[ky+"_weights"],dtype=np.float32)
           weights/=weights.sum() # normalize weights
           stacked_matrices = np.stack(maps[ky]).astype(np.float32)
           if mode == "max":
               final_map = stacked_matrices.max(0)
           else:
               final_map = np.tensordot(weights, stacked_matrices, axes=([0], [0])) # weighted sum of maps
               # final_map=np.zeros_like(stacked_matrices[0])
               # for kk in range(stacked_matrices.shape[0]): # weighted sum
               #     final_map += stacked_matrices[kk] * weights[kk]
           print(ky)
           cv2.imwrite(outsubdir+"/"+ky,final_map.astype(np.uint8))
       x=open(outsubdir+"/Finished.txt","w")
       x.write(files_names)
       x.close()
       x = open(outsubdir + "/" + mode + ".txt", "w")
       x.write(mode)
       x.close()
       print("Finished",outsubdir)
