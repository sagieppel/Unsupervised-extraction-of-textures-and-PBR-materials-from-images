# Script for Generating The MatSeg Dataset
###############################Dependcies######################################################################################

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import json
import sys
filepath = bpy.data.filepath
homedir = os.path.dirname(filepath)
sys.path.append(homedir) # So the system will be able to find local imports
os.chdir(homedir)
import MaterialsHandling as Materials
import ObjectsHandling as Objects
import RenderingAndSaving as RenderSave
import MaterialMapping 
import SetScene
import time
import json

################################################################################################################################################################

#                                   Input Parameters: Input and OutPut paths

###################################################################################################################################################################


#ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
##r"Objects/"
##r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/" 
## folder where out put will be save
#OutFolder="OutFolder/" # folder where out put will be save
#pbr_folders = [r"/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/NormalizedPBR/",
#r'/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/NormalizedPBR_MERGED',
#r'/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/NormalizedPBR_MERGED']
##r'/media/breakeroftime/9be0bc81-09a7-43be-856a-45a5ab241d90/NormalizedPBR_MERGED/']
#image_dir=r"/home/breakeroftime/Documents/Datasets/ADE20K_Parts_Pointer/Eval/Image/"


#MainOutDir="/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/MaterialsDataset/Multiphase_SmoothTransition_MultiObjects_Take3/"


#------------------------Input parameters---------------------------------------------------------------------
MainOutDir="/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/GeneratedPBRs_And_Textures/dadasa/" # folder where out put will be save
if not os.path.exists(MainOutDir): os.mkdir(MainOutDir)

# Hdri background folder, 3d object folder, Pbr materials folder, Images folder use to generate the UV map 
# Example HDRI_BackGroundFolder and PBRMaterialsFolder  and ObjectsFolder folders should be in the same folder as the script. 

HDRI_BackGroundFolder=r"/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/selected/"#/home/breakeroftime/Documents/Datasets/DataForVirtualDataSet/4k_HDRI/4k/"  # Background hdri folder (taken from HDRI Haven site)
ObjectFolder=r"/home/breakeroftime/Documents/Datasets/Shapenet/ObjectGTLF_NEW/"  #Folder of objects (like shapenet) 
#pbr_folders = "/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/GeneratedPBRs_And_Textures/pbr_openimages_0_large"
#mode =2
pbr_folders = "/mnt/306deddd-38b0-4adc-b1ea-dcd5efc989f3/Materials_Assets/GeneratedPBRs_And_Textures/pbr_openimages_1_large_1"
mode =2 
               
                # PBR materials folders to read PBR from, could contain few folders  
natural_image_dir=r"/media/breakeroftime/2T/Data_zoo/dms_v1_labels/images/train/"#random images that will be used to generate the materials UV map
material_dic_file = MainOutDir + "/Materials_Dictinary.json" # contain wich material appear in which image not currently used

NumSetsToRender=100000 # How many set to render before you finish (how many images to create)
use_priodical_exits = False # Exit blender once every few sets to avoid memory leaks, assuming that the script is run inside sh Run.sh loop that will imidiatly restart blender fresh (use this if the generation seem to get slower over time).

 


#########################################################################################################################################################

#------------------Set material handling structures--------------------------------------------------------------------------
 
#material loader class
mat_loader=Materials.MaterialHandler(pbr_folders,material_dic_file,mode=mode)

#---------------List of materials that are part of the blender structure and will not be deleted between scenes------------------------------------------
 
MaterialsList=["Multiphase_Graph","Material_Group1","Material_Group","TwoPhaseFromImage","White","Black","PbrMaterial1","PbrMaterial2","TwoPhaseMaterial","GroundMaterial","TransparentLiquidMaterial","BSDFMaterial","BSDFMaterialLiquid","Glass","PBRReplacement"] # Materials that will be used
#---------------------------------------------------------------------------------------------------------

images_paths=[]
#for fl in os.listdir(natural_image_dir): images_paths.append(natural_image_dir+"/"+fl)

#------------------------------------Create list with all hdri files in the folder (this used for backgroun image and illumination)-------------------------------------
hdr_list=[]
for hname in os.listdir(HDRI_BackGroundFolder): 
   if ".hdr" in hname:
         hdr_list.append(HDRI_BackGroundFolder+"//"+hname)


#-------------------------Create output folder--------------------------------------------------------------

if not os.path.exists(MainOutDir): os.mkdir(MainOutDir)

#==============Rendering engine parameters ==========================================

bpy.context.scene.render.engine = 'CYCLES' # 
bpy.context.scene.cycles.device = 'GPU' # If you have GPU 
#bpy.context.scene.cycles.feature_set = 'EXPERIMENTAL' # Not sure if this is really necessary but might help with sum surface textures
bpy.context.scene.cycles.samples = 120 #200, #900 # This work well for rtx 3090 for weaker hardware this can take lots of time
bpy.context.scene.cycles.preview_samples = 900 # This work well for rtx 3090 for weaker hardware this can take lots of time

bpy.context.scene.render.resolution_x = 440 # image resulotion 
bpy.context.scene.render.resolution_y = 440

#bpy.context.scene.eevee.use_ssr = True
#bpy.context.scene.eevee.use_ssr_refraction = True
bpy.context.scene.cycles.caustics_refractive=True
bpy.context.scene.cycles.caustics_reflective=True
bpy.context.scene.cycles.use_preview_denoising = True
bpy.context.scene.cycles.use_denoising = True #****************************


# get_devices() to let Blender detects GPU device
#bpy.context.preferences.addons["cycles"].preferences.get_devices()
#print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
#for d in bpy.context.preferences.addons["cycles"].preferences.devices:
#    d["use"] = 1 # Using all devices, include GPU and CPU
#    print(d["name"], d["use"])



#----------------------------Create list of Objects that will be loaded during the simulation---------------------------------------------------------------
ObjectList={}
ObjectList=Objects.CreateObjectList(ObjectFolder)
print("object list len",len(ObjectList))
#ClearMaterials(KeepMaterials=MaterialsList)
#main_phase_graph, uv,  MaterialDictionary = CreateMultiphaseMaterialGraph()
#----------------------------------------------------------------------
######################Main loop##########################################################\



scounter=0 # Count how many scene have been made in this run of the script (if folder exist and cnt have skipped one this will not be increased (cnt will)
cnt=0# counter name of output  this will be used as the name of the output folder
while(True):# Each cycle of this loop generate one image and segmentation map
 
        cnt+=1
        OutputFolder=MainOutDir+"/"+str(cnt)+"/" # sub outpur folder
#       
        if  os.path.exists(OutputFolder): continue # Dont over run existing folder, if folder exist go to next number 
        if  not os.path.exists(OutputFolder):  os.mkdir(OutputFolder)
        
        mat_loader.initiate_scene_data(OutputFolder,cnt) # class for loading and handling materials
        scounter+=1
        

        
        #if os.path.exists(CatcheFolder): shutil.rmtree(CatcheFolder)# Delete liquid simulation folder to free space
        
        if scounter>NumSetsToRender: break
    
    
#================================Create scene load object and set material=============================================================================
        print("==========================================Start Scene Generation======================================================")
        print("Simulation number:"+str(cnt)+" Remaining:"+ str(NumSetsToRender))
        SetScene.CleanScene()  # Clear scence, Delete all objects in scence
   
      
#------------Load random object into scene center these are the main objects where the materials will map to---------------------------------
#        print("Load main object")
#        bpy.ops.object.select_all(action="DESELECT")
#        bpy.data.objects[MainObjectName].select_set(True)
#        bpy.context.view_layer.objects.active = bpy.data.objects[MainObjectName]
#        bpy.ops.object.editmode_toggle() #edit mode
#        bpy.ops.mesh.remove_doubles() #remove overlapping faces
#        bpy.ops.uv.smart_project(island_margin=0.03)
#        bpy.ops.object.editmode_toggle() #back to object mode

       
#***************************SMOOTH objec (optional)******************************************************************

#**************************Replace the object materials*****************************************************************        
     #   print("Set Scene Creating enviroment and background and set camera")
       # Materials.ReplaceMaterial(MainObject,main_phase_graph) # replace material on object
        
    #    MaxZ=MaxXY=20 # Size of object
       #-------------------------------------------Create ground plane and assign materials to it (optional)----------------------------------
         
        PlaneSx,PlaneSy= SetScene.AddSphere("Ground",segments=200, ring_count=200) # Add plane for ground
            ##if np.random.rand()<10.9:
        mat_loader.load_random_PBR_material(bpy.data.materials['GroundMaterial'].node_tree)
        Materials.ReplaceMaterial(bpy.data.objects["Ground"],bpy.data.materials['GroundMaterial']) # Assign PBR material to ground plane (Physics based material) from PBRMaterialsFolder
        current_dir = mat_loader.current_dir
        OutputFolder = mat_loader.current_dir
    #------------------------Load random background hdri---------------------------------------------------------------   
        SetScene.AddBackground(hdr_list) # Add randonm Background hdri from hdri folder


    #...........Set Scene and camera postion..........................................................
        SetScene.RandomlySetCameraPos(name="Camera",VesWidth = 1,VesHeight = 1)
               
#######################################Saving and Image Rendering################################################################################3  
        print("Saving data:",OutputFolder)        
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        
  #      x=sfsfsfs
        print("Write:",current_dir)
        RenderSave.RenderImageAndSave(FileNamePrefix="Material_View.jpg",OutputFolder=current_dir) # Render image and save
  
    
           #------------------Save Segmentation mask-----------------------------------------------------------------------------
#        
#        RenderSave.SaveMaterialsMasks([MainObjectName],OutputFolder) # Save segmentation maps of all materials 
#        RenderSave.SaveObjectVisibleMask([MainObject.name],OutputFolder +"/ObjectMaskOcluded") #mask of only visible region
#    
#        #-------------Save material properties This isnt really used at this point (but help indentify same material in different images, not used and unchecked)----------------------------------------------------
#        mat_loader.save_scene_data()
    
   
        
    
      
        
       # open(OutputFolder+"/Finished.txt","w").close()
        print("DONE SAVING")
##################################Finish and clean scene######################################################################################    
        
        objs=[]
            #------------------------------Finish and clean data--------------------------------------------------
        
       
        #-------------Delete all objects from scene but keep materials---------------------------
        for nm in bpy.data.objects: objs.append(nm)
        for nm in objs:  
                bpy.data.objects.remove(nm)
       

        print("Cleaning")

    #    open(OutputFolder+"/Finished.txt","w").close() # add in the end of image generation and used to confirmed that all data was created for this scene (if this doesnt exist in folder it mean that generation wasnt complete (due crashes or something)
        
        # Clean images
        imlist=[]
        for nm in bpy.data.images: imlist.append(nm) 
        for nm in imlist:
            bpy.data.images.remove(nm)
        # Clean materials
     
        SetScene.ClearMaterials(KeepMaterials=MaterialsList)
        print("======================================Finished===========================================")
        SetScene.CleanScene()  # Delete all objects in scence
        if use_priodical_exits and scounter>=100: # Break program and exit blender, allow blender to remove junk use this if you feel the generation becoming slower with time, and if you use Run.sh, otherwise ignore. 
             print("quit")
             bpy.ops.wm.quit_blender()
             break
      