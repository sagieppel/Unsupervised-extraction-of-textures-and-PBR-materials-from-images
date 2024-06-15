# Scan a list of folders and identify regions with uniform texturs extract this textures regions into differnt file



import os
import cv2
import shutil
import numpy as np
from scipy.stats import ks_2samp, mannwhitneyu
import scipy
from sklearn.metrics.pairwise import cosine_similarity
import json

##################################################################################################################################

# Identify regions with uniform textures in map (large, extract larger textures (parameters suited for images in te segment anything repository)

##################################################################################################################################
# Get propeties maps for the image
def get_prop_maps(img,props):  # Get statitical props for a region
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
##################################################################################################################################
# # Get match between two patches
# def get_match(sample1,sample2,mode="mw"):
#     if mode == "ks":
#        _stat, p_value = ks_2samp(sample1, sample2) # Perform the Kolmogorov-Smirnov test
#     else:
#        _stat, p_value = mannwhitneyu(sample1, sample2)  # Perform the Mann-Whitney U test
#     return p_value
###############################################################################################################################

# Get similarity between two distribution (to asses if they have same texture)

####################################################################################################################################
# Get Distribution Similarity between two cells
def get_similarity(sample1,sample2):
    num_bins = 10#int(np.sqrt(len(sample1)))
   # num_bins = int(np.log2(len(sample1))) + 1


    # Calculate the combined minimum and maximum
    combined_min = min(np.min(sample1), np.min(sample2))
    combined_max = max(np.max(sample1), np.max(sample2))

    # Create histograms (density distributions) of the samples
    hist1, _ = np.histogram(sample1, bins=num_bins, range=(combined_min, combined_max), density=True)
    hist2, _ = np.histogram(sample2, bins=num_bins, range=(combined_min, combined_max), density=True)
  #  hist2=hist1
  #  similarity = np.sum(np.minimum(hist1, hist2)) / np.minimum(np.sum(hist1), np.sum(hist2)) # Overlap Coefficient for Histograms


  #  similarity = cosine_similarity(hist1.reshape(1, -1), hist2.reshape(1, -1))[0][0]# Reshape histograms for cosine_similarity function

    similarity = 1 -  scipy.spatial.distance.jensenshannon(hist1, hist2) # # Compute the Jensen-Shannon distance
    return similarity

##################################################################################################################################
# turn x,y coordinate to a single index
###################################################################################################################
def xy2ind(x,y,xrange):
    return y*xrange+x

##########################################################################33
def sim_level(maps,total_sim,x1,y1,x2,y2,xrange,tile_size,sim_thresh):
# Get the similarity between a cell (x1,y1,xrange) and (cell x2,y2,xrange), cells are in maps return
#    print(x2, y2, xrange,"   ",total_sim.shape)
    sim_list=[]
    if total_sim[xy2ind(x1, y1, xrange), xy2ind(x2, y2, xrange)] > -1:  # similarity between squares have already been calculated
        return total_sim[xy2ind(x1, y1, xrange), xy2ind(x2, y2, xrange)] , total_sim
    else:  # find patches similarities
        for p1 in range(maps.shape[2]): # scan similarity acr
            patch1 = maps[y1 * tile_size: y1 * tile_size + tile_size, x1 * tile_size: x1 * tile_size + tile_size,p1].reshape(-1)
            patch2 = maps[y2 * tile_size: y2 * tile_size + tile_size, x2 * tile_size: x2 * tile_size + tile_size,p1].reshape(-1)
            similarity = get_similarity(patch1, patch2)
            sim_list.append(similarity)
            if similarity < sim_thresh: break
        min_sim=np.array(sim_list).min()
        total_sim[xy2ind(x2, y2, xrange), xy2ind(x1, y1, xrange)] = min_sim
        total_sim[xy2ind(x1, y1, xrange), xy2ind(x2, y2, xrange)] = min_sim
    return min_sim , total_sim
#################################################################################
# similarity between patch (x2,y2) and a list of patches (list_patches)
def sim_level_2_list_of_patches(maps,total_sim,list_patches,x2,y2,xrange,tile_size,sim_thresh):
    sim_list=[]
    for  pt in list_patches:
        x1=pt[0]
        y1=pt[1]
        psim, total_sim = sim_level(maps, total_sim, x1, y1, x2, y2, xrange, tile_size, sim_thresh)
        sim_list.append(psim)
        if psim<sim_thresh: break
    return np.array(sim_list).min(),total_sim



#############################################################33
#  Similarity identify region on the image with uniform textures by splitting region to chekboard tiles and finding region were the statistic of all tiles overlap
def get_box_sim_maps(maps,tile_size,min_tiles2map,sim_thresh,img,max_regions_per_img=100):
     yrange = int(np.floor((img.shape[0])/tile_size)) # number of tiles in image
     xrange = int(np.floor((img.shape[1])/tile_size))
     all_regions=[]
     total_sim = np.eye(xrange*yrange, xrange*yrange, dtype=np.float32)*2-1 # Dictionary of  total similarity matrix between every 2 tiles  in the image -1: undertmined 0-1 prob (to prevent the need to recalculate every time)
     for x1 in range(xrange-min_tiles2map+1):
         for y1 in range(yrange-min_tiles2map+1):
             min_sim_tot = 1000 # min similarity for current
             rsize_fin = 0
             tiles_in_map=[[x1,y1]] # coordinates of all tiles in map
             for rsize in range(1,np.min([xrange-x1,yrange-y1])): # dimension of texture map scan similarity of texture map  starting at x1,y1 and of size rsize
                     y2 = y1+rsize
                     min_sim = 1000 # min similarity for current

                     # increase the size of the scanned map one row and column at a time (by comparing the cells in this column to already added cells)
                     for  x2 in range(x1+1,x1+rsize+1):  # scan row

                        psim , total_sim = sim_level_2_list_of_patches(maps,total_sim,tiles_in_map,x2,y2,xrange,tile_size,sim_thresh)
                        tiles_in_map.append([x2,y2])
                        min_sim = np.min([min_sim, psim])
                        if psim<sim_thresh: break
                     if psim<sim_thresh: break
                     x2 = x1 + rsize
                     for y2 in range(y1 + 1, y1 + rsize + 1): # Scan column
                         psim , total_sim = sim_level_2_list_of_patches(maps, total_sim, tiles_in_map, x2, y2, xrange, tile_size, sim_thresh)
                         tiles_in_map.append([x2,y2])
                         min_sim = np.min([min_sim, psim])
                         if psim<sim_thresh: break
                     if psim<sim_thresh: break

                     rsize_fin = rsize
                     min_sim_tot =  np.min([min_sim_tot,min_sim])

             if  rsize > min_tiles2map: # if larger then minimal texture size marke as pass
                 region = {"x1":x1*tile_size,"y1":y1*tile_size,"size":rsize_fin*tile_size,"score":min_sim_tot}
                 add2regions=True
                 for rg in all_regions:
                     if rg["x1"]<=region["x1"] and rg["y1"]<=region["y1"] and rg["x1"]+rg["size"]>=region["x1"]+region["size"] and rg["y1"]+rg["size"]>=region["y1"]+region["size"]:
                         add2regions=False
                         break
                 if add2regions: # add region to founed textures
                        all_regions.append(region)
                        if len(all_regions)>max_regions_per_img: return all_regions
                        print(len(all_regions),"new Texture Found:",region)
     return all_regions
###################################################################################################################################

# Mark square on image (for visuallization only)

##################################################################################################################################
def mark_region(im,rg,display=True):
    im2 = im.copy()
    cv2.rectangle(im2, (rg["x1"], rg["y1"]),  (rg["x1"]+rg["size"], rg["y1"]+rg["size"]), (0, 0, 255), 5)
    texture = im[ rg["y1"]:rg["y1"]+rg["size"],rg["x1"]:rg["x1"]+rg["size"]]
    if display:
        cv2.destroyAllWindows()
        cv2.imshow("Texture + size="+str(rg["size"])+" score="+str(rg["score"]),texture)
        cv2.imshow("marked + size="+str(rg["size"])+" score="+str(rg["score"]), im2)
        cv2.waitKey()
    return texture,im2

##############################################################################################################################
##################################################################################################################################

# INPUT PARAMETERS

##################################################################################################################################
tile_sizes=[75] # cell size in pixel use (75 is good for segment anything repository, 40 is good for the open_images repository_
min_tiles2map=7 # min number of cells in texture (across one dimension 6-8 are good values)
properties = ["RGB","GRAD"]#,"HSV","RELATIVE_RGB"]#,"HSV","GRAD","RELATIVE_RGB"] # Properties used for the cell histogram matching uniform texture will have to have uniform disribution of these properties
image_dir = "in_images/"#Image dir from wich textures will be extracted
sim_thresh = 0.5  #minimal similarity  between cells for uniform texutre
max_im_size=2200 # maximal image size (shrink  if image is larger)
save_by_thresh_and_size=False
image_type=".jpg" # read only this images leave empty if read everythin
out_dir = "extracted_textures/" # folder were output will be saved will be saved



# Make output folder
texture_small_dir = out_dir + "/texture_small/"# output textures original sizes dir
texture_large_dir = out_dir + "/texture_large/"# textures original sizes dir
marked_dir = out_dir + "/marked/"
data_dir = out_dir + "/data/"
done_files = out_dir + "/done_files/"


if not os.path.exists(out_dir): os.mkdir(out_dir)
if not os.path.exists(texture_small_dir): os.mkdir(texture_small_dir) #
if not os.path.exists(texture_large_dir): os.mkdir(texture_large_dir)
if not os.path.exists(marked_dir): os.mkdir(marked_dir) # texture marked on image
if not os.path.exists(data_dir): os.mkdir(data_dir) # data on texture short
if not os.path.exists(done_files): os.mkdir(done_files) # marked done files
#----------------not used-------------------------------------------------

if save_by_thresh_and_size:
    for i in range(11):
        if not os.path.exists(out_dir+"/score_"+str(i)):
             os.mkdir(out_dir+"/score_"+str(i))
    for i in tile_sizes:
        if not os.path.exists(out_dir + "/size_" + str(i)):
            os.mkdir(out_dir + "/size_" + str(i))
#--------------------------------------------------------------
#image_dir = "/media/breakeroftime/2T/Data_zoo/dms_v1_labels/images/test/"
#---------------go over all images in folder image_dir and extract uniform textures and saved to out_dir----------------------------------------------------------------
for num,fl in enumerate(os.listdir(image_dir)):
            if len(image_type)>0 and (not image_type in fl): continue

            if os.path.exists(done_files+"/"+fl[:-3]+"txt"): # if already done skip
                print(num,fl,":  File already done")
                continue
            for tile_size in tile_sizes:
             #   try:
                    print(fl,"tile size",tile_size)
                    path=image_dir+"/" + fl
                    if not os.path.isfile(path):
                        print("continue")
                        continue
                    print(1)

                    im_origin = cv2.imread(path)
#Resize if too big
                    print("Size: ", im_origin.shape)
                    r=max_im_size/np.min([im_origin.shape[0], im_origin.shape[1]])
                    if r<1:
                         im=cv2.resize(im_origin,[int(im_origin.shape[1]*r),int(im_origin.shape[0]*r)])
                    else:
                         im = im_origin.copy()
                    print("New Size: ",im.shape)
# Get property map from the image
                    prop_maps = get_prop_maps(im,properties)
                    print(2)
# identify regions with uniform textures
                    region_list = get_box_sim_maps(prop_maps, tile_size, min_tiles2map, sim_thresh, im, max_regions_per_img=100)
                    print(3)
# Extract and save uniform textures
                    for i,reg in enumerate(region_list):
                        texture , marked_images = mark_region(im,reg,display=False)# Get texture region in small size
                        print(out_dir+"/"+fl[:-4]+str(i)+"_Score_"+str(reg["score"])[2:6]+"_TileSize"+str(tile_size)+"_Texture.jpg",)
                        cv2.imwrite(texture_small_dir + "/" + fl[:-4]+str(i)+"_Score_"+str(reg["score"])[2:6]+"_TileSize"+str(tile_size)+"_Texture.jpg",texture)
                      #  cv2.imwrite(marked_dir + "/" + fl[:-4] + str(i) + "_Score_" + str(reg["score"])[2:6] + "TileSize" + str(tile_size) + "Marked.jpg", marked_images)
                        #----------------------------------------------------------------------------------------------------------
                        # Save in the orginal size
                        if r<1: # resize to original size
                            reg['y1'] = int(reg['y1'] / r)
                            reg['x1'] = int(reg['x1'] / r)
                            reg['size'] = int(reg['size'] / r)
                            reg['image'] = path
                        texture, marked_images = mark_region(im_origin, reg, display=False)# Get texture region in original size
                        cv2.imwrite(texture_large_dir + "/" + fl[:-4] +"_"+ str(i) + "_Score_" + str(reg["score"])[2:6] + "_TileSize" + str(tile_size) + "_Texture.jpg", texture)
                        # Convert and write JSON object to file
                        with open(data_dir+"/"+fl[:-4] + str(i) + "_Score_" + str(reg["score"])[2:6] + "TileSize" + str(tile_size) + ".json", "w") as outfile:
                            json.dump(reg, outfile)
                        if save_by_thresh_and_size:
                              cv2.imwrite(out_dir + "/size_"+str(tile_size) +"/"+fl[:-4] + str(i) + "_Score_" + str(reg["score"])[2:6] + "TileSize" + str(tile_size) + "Marked.jpg", marked_images)
                              cv2.imwrite(out_dir + "/score_" + str(int(reg["score"]*10)) + "/"+fl[:-4] + str(i) + "_Score_" + str(reg["score"])[2:6] + "TileSize" + str(tile_size) + "Marked.jpg", marked_images)
                    # Marked file as finished
                    x=open(done_files+"/"+fl[:-3]+"txt","w")
                    x.write("done")
                    x.close()
            #    except:
             #       print("failed at:",image_dir+"/" + fl)


