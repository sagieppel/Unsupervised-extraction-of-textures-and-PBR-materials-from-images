import cv2
import os
import numpy as np
##########################################################################################################################\

# Given image of uniform texture turn it into PBR material (old version)

##################################################################################################################################
# Get propeties maps for the image
def get_prop_maps(img,props=["RGB","GRAD","HSV","RELATIVE_RGB"]):  # Get statitical props for a region
           maps=np.zeros([img.shape[0],img.shape[1],0],dtype=np.float32)
           if  "RGB" in props:
               maps = np.concatenate([maps,img,img.mean(2, keepdims=True)],axis=2)#[..., np.newaxis]
           if "RELATIVE_RGB" in props:
               maps = np.concatenate([maps, img/(img.mean(2, keepdims=True)+10)], axis=2)
           if "HSV" in props:
               maps = np.concatenate([maps,cv2.cvtColor(img, cv2.COLOR_RGB2HSV)], axis=2)
           if "GRAD" in props:
               grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0)
               grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1)
               grad_sum = np.sqrt(grad_x ** 2 + grad_y ** 2)
               maps = np.concatenate([maps, grad_x, grad_y, grad_sum], axis=2)
           return maps
############################################################################################################################

# Convert Height map to Normal map (by dx,dy derivation)

#############################################################################################################
def height_map_to_normal_map(height_map):
    """
    Converts a height map (numpy array of uint8) to a normal map.

    Args:
    height_map (numpy.ndarray): A 2D numpy array of uint8 type representing the height map.

    Returns:
    numpy.ndarray: A 3D numpy array (height, width, 3) of uint8 type representing the normal map.
    """
    # Convert height map to float32 for processing
    heights = height_map.astype(np.float64) / 255.0

    # Calculate gradients in both x and y directions
    dy, dx = np.gradient(heights)

    # if np.random.rand()<-0.4:
    #     r = np.random.rand() * 2 + 1
    #     if np.random.rand() < 0.7:
    #        dy /= r
    #        dx /= r
    #     else:
    #         dy*=r
    #         dx*=r



    normals = np.zeros((height_map.shape[0], height_map.shape[1], 3), dtype=np.float64)  # Initialize the normals array
    if np.random.rand()<0.76: # factor of dx,dy to dz
      r = 16*np.random.rand()*np.random.rand()
    elif np.random.rand()<0.77:# factor of dx,dy to dz
      r = 24 * np.random.rand() * np.random.rand()
    else:
        r=1

    normals[:, :, 0] = -dx*r   # x-component of normal
    normals[:, :, 1] = -dy*r   # y-component of normal
    normals[:, :, 2] = 1  # z-component of normal (straight up)

    # Normalize the normal vectors to make them unit vectors
    norm = np.linalg.norm(normals, axis=2, keepdims=True)
    normals /= norm

    # Convert normalized vectors to RGB format
    normal_map = ((0.5 * (normals + 1) * 255).clip(0, 255)).astype(np.uint8)
    normal_map = normal_map[:,:,::-1] # convert from bgr to RGB
   # cv2.imshow("normal_map",normal_map);cv2.waitKey()

    return normal_map
################################################################################################################################
# display for debuging
def display_pbr_dir(pbr_dir = "/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/NormalizedPBR/"):
    ls=[]
    for dr in os.listdir(pbr_dir):
        for fl in os.listdir(pbr_dir + "/" + dr + "/"):
            sdir = pbr_dir + "/" + dr + "/"
            # normal_path = sdir + "Normal.jpg"
            # norm = cv2.imread(normal_path)
            if fl not in ls: ls.append(fl)
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

##################################################################################################################################

# rotate color space along hue for augmentation

##########################################################################################################
def rotate_color_space(im):
    im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    im[:, :, 0] = ((im[:, :, 0].astype(np.float32) + np.random.randint(0, 255)) % 255).astype(np.uint8)
    im = cv2.cvtColor(im, cv2.COLOR_HSV2BGR)
    return im


###################################################################################################
# Main function receive RGB image of texutre an
def turn_texture_to_PBR(im):
    # augmentations
        if np.random.rand()<0.22: # Augment color
            im = rotate_color_space(im)

        if np.random.rand() < 0.5: im = np.rot90(im)
        if np.random.rand() < 0.5: im = np.fliplr(im)
        if np.random.rand() < 0.5: im = np.flipud(im)
     #------Property map to extract from image
        raw_maps = get_prop_maps(im,props=["HSV","RELATIVE_RGB"])
        final_maps = {}
        #------------AmbientColor ----------- OriginColor albedo--------------------------------------------------------------
        if np.random.rand()<0.20:
            im = rotate_color_space(im) # augment color by rotating color space
      #  final_maps["AmbientColor"] = im
        final_maps["Color"] = im
        #---------------------------Properties map to generate---------------------------------------------------------------------------------
        mapkeys=['Height', 'Roughness', 'Metallic'] # list of property maps to generate
      # add optional property maps
        if np.random.rand()<0.1: mapkeys.append("AmbientOcclusion") # optional map
        if np.random.rand()<0.13: mapkeys.append("Opacity")# optional map


        if np.random.rand() < 0.13: mapkeys.append("Specular")# optional property map





        if np.random.rand() < 0.02: mapkeys.append("Emission")# optional property map

    # generate map for each property ----------------------------------
        for ky in ['Height', 'Roughness', 'Metallic']:
            #------------Constant  unform map for prorty------------------------------------------------------------------------------
            if np.random.rand()<0.14: # use constant value
                if ky == 'Height':
                    final_maps['Height'] = np.zeros_like(im[:,:,0])
                    continue
                if np.random.rand() < 0.5:
                    final_maps[ky] = np.ones_like(im[:, :, 0]) * np.random.randint(0,256)
                elif np.random.rand() < 0.5:
                    final_maps[ky] = np.ones_like(im[:, :, 0]) * 255
                else:
                    final_maps[ky] = np.zeros_like(im[:, :, 0])
                continue
            # ----------------Generate Patterned map from image channel---------------------------------------------------------
            else: #  choose which image property will be used to generate the map
                r = np.random.rand()
                if r<0.2:
                      mp = im.mean(2)
                elif r<0.6:
                    k=np.random.randint(0,raw_maps.shape[2])
                    mp = raw_maps[:,:,k]
                else:
                    mp = rotate_color_space(im)[:,:,np.random.randint(0,3)]
            #............Blure augment.............................
                if np.random.rand() < 0.5: # negative of map
                    mp = 255 - mp
                if np.random.rand() < 0.22: # blurring
                        kernel_size = 3 + np.random.randint(0, 4) * 2
                        mp = cv2.GaussianBlur(mp, (kernel_size, kernel_size), 0)


    #---------Add tresholds and min and max values--------------------------------------------------------------------
                if np.random.rand()<0.2:
                    final_maps[ky] = mp
                    continue
                else:
                    if np.random.rand()<0.75:
                           low_thresh = np.random.randint(0,250)
                    else:
                        low_thresh = 0
                    if np.random.rand() < 0.75:
                         high_thresh = np.random.randint(low_thresh, 256)
                    else:
                        high_thresh = 255
                if ky == 'Height': # height should always be the max range
                     high_thresh=255
                     low_thresh=0
# ---------------create final map----------------------------------------------------------
                mp = low_thresh + (high_thresh - low_thresh)*(mp.astype(np.float32)/(mp.max()+1))
                if np.random.rand() < 0.11 or  ky == 'Height':
                    mp[mp<low_thresh]=0

                final_maps[ky] = mp.astype(np.uint8)
# some more augmentation property specific
        if np.random.rand()<0.14: # generate reflective regions max mettalic np roughness
            final_maps['Metallic'][final_maps['Metallic']>160]=255
            if np.random.rand() < 0.66:
                final_maps['Roughness'][final_maps['Metallic'] > 160] = 0
        if np.random.rand()<0.1: # generate non reflective regions
            final_maps['Metallic'][final_maps['Metallic']<160]=0
            if np.random.rand() < 0.66:
                final_maps['Roughness'][final_maps['Metallic'] > 160] = 255
        if np.random.rand()<0.17 and ('Opacity' in final_maps): # generate transparent regions (max transprency)
            final_maps['Opacity'][final_maps['Opacity']<100]=0
            if np.random.rand() < 0.66:
                final_maps['Roughness'][final_maps['Opacity']<100] = 0
                final_maps['Metallic'][final_maps['Metallic'] < 100] = 0



        #========Normal map derived from height map by gradient===============================================================
        final_maps["Normal"] = height_map_to_normal_map(final_maps['Height'])
        # if np.random.rand() < 0.18:
        #     kernel_size = 3 + np.random.randint(0, 4) * 2
        #     final_maps["Normal"] = cv2.GaussianBlur(final_maps["Normal"], (kernel_size, kernel_size), 0)
        return final_maps
#####################################################################################################################################

# Go over texture folder (images of uniform textures) and turn each texture into pbr into PBR

###################################################################################
# given a folder of texture (texture dir) turn  every texture into pbr material (pbr dir)
def texture_dir2pbrdir(texture_dir,pbr_dir,tag=""):
    if not os.path.exists(pbr_dir): os.mkdir(pbr_dir)
    for ii,fl in enumerate(os.listdir(texture_dir)):
        sdir = pbr_dir + "/" + fl[:-4]
        if os.path.exists(sdir+"/finished.txt"): continue
        print("=============================================================")
        print(ii)
      #   if ii<10: continue
        texture = cv2.imread(texture_dir+"/"+fl)
        maps = turn_texture_to_PBR(texture) # turn texture into pbr
        if not os.path.isdir(pbr_dir): os.mkdir(pbr_dir)

        if not os.path.isdir(sdir): os.mkdir(sdir)
        for ky in maps: # save all maps into files
            cv2.imwrite(sdir+"/"+ky+".jpg",maps[ky])
        x=open(sdir+"/finished.txt","w")
        x.close()


####################################################################################################################################
#  Given image of uniform texture turn it into PBR material
if __name__ == '__main__':
    texture_dir = "extracted_textures/texture_large/" # input texture folder used to generate the PBR
    pbr_dir = "extracted_pbrs/" # output pbr folder each subfolder in these will contain a generate maps for PBR
    # turn the texture into PBR
    texture_dir2pbrdir(texture_dir, pbr_dir, tag="pbr_")
    #display_pbr_dir()