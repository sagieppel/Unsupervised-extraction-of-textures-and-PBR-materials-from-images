# Read and display the generated MatSeg Dataset
import cv2
import numpy as np
import os
#---Input parameters---------------------------
data_dir = r"sample/" # folder of the MatSeg Dataset

display=True# display on screen
write=False# write to file
outdir = r""

#------Colors--------------------------------------------------

colors = [
    (255, 0, 0),    # Class 0: Red
    (0, 255, 0),    # Class 1: Green
    (0, 0, 255),    # Class 2: Blue
    (128,128,128),  # Grey
    (255, 255, 0),  # Class 3: Yellow
    (255, 0, 255),  # Class 4: Magenta
    (0, 255, 255),  # Class 5: Cyan
    (128, 0, 0),    # Class 6: Dark Red
    (0, 128, 0),    # Class 7: Dark Green
    (0, 0, 128),    # Class 8: Dark Blue
    (128, 128, 0)   # Class 9: Olive
]


#---------main loop-------------------------------------------------------

for sdr in os.listdir(data_dir):
    if os.path.exists(outdir +"/"+sdr+".png"): continue
    path = data_dir+"/"+sdr+"/"
    im =  cv2.imread(path+"/RGB__RGB.jpg")
    masks=[]
    images=[]
    for fl in os.listdir(path):
        if "mask" in fl:
           mask =  cv2.imread(path+"/"+fl,0)
           rgb_image = np.ones((*mask.shape, 3))
           rgb_image[:,:] = colors[len(masks)]
           masks.append(mask)
           images.append(rgb_image)
    masks=np.array(masks)
    images=np.array(images)

    masks[masks<10]=0
    masks = np.where(masks == 0, 0, masks / masks.sum(axis=0))
    # im = (masks[:, :, :, np.newaxis] * images).mean(0)
    # color = (masks[:, :, :, np.newaxis] * images).sum(0)
    ann = (masks[:, :, :, np.newaxis] * images).sum(0).astype(np.uint8)
    fin = np.concatenate([im, ann], 1)
    fin = cv2.resize(fin,[int(fin.shape[1]/2),int(fin.shape[0]/2)])

  #------------display and save-------------------------------------------------------
    if display:
        cv2.imshow("press any key to continue",fin)
        ky=cv2.waitKey()

    if write:
         print("save",outdir +"/"+sdr+".png")
         cv2.imwrite(outdir +"/"+sdr+".png",fin)


