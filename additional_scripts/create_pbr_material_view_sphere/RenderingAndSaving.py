# Rendering and saving images depth maps and normal maps
###############################Dependcies######################################################################################3

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
directory = os.path.dirname(filepath)
#sys.path.append("/home/breakeroftime/Desktop/Simulations/ModularVesselContent")
sys.path.append(directory)
os.chdir(directory)

import ObjectsHandling as Objects
########################################################################################################

# Render scene as RGB + Depth Map + Normal map

#################################################################################################
def RenderDepthNormalAndImageToFiles(OutputFolder,FileName, RenderImage=True,RenderDepth=True,RenderNormal=True):
    if not os.path.exists(OutputFolder): os.mkdir(OutputFolder)
   # else: print("Warning output folder: "+ OutputFolder+ " Already exists")



    #=========================Get Scene compostion tree=======================================
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    #================remove/clear existing composition node tree======================================
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
    #===========================Create new composition tree=====================================================
    scene = bpy.context.scene
    scene.render.use_multiview = False  #True # Use stereo
    #scene.render.views_format = 'STEREO_3D'
    r1 = tree.nodes.new(type="CompositorNodeRLayers") # Add node
    composite = tree.nodes.new(type = "CompositorNodeComposite") # Add another node
    composite.location = 200,0 # panel location on the board meaningles

    # Add passes for computing surface normals
    scene.view_layers['View Layer'].use_pass_normal = True
    #scene.render.image_settings.color_depth = '16'


    scene.render.image_settings.file_format = "JPEG"#'OPEN_EXR' # output format
  
    #============Render image=============================================================
    if  RenderImage:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # Rendering engine
        #bpy.context.scene.render.engine = 'CYCLES' # Rendering engine
        links.new(r1.outputs['Image'],composite.inputs['Image']) # link image node to output
        scene = bpy.context.scene  # Initialize scene
        scene.render.use_multiview = False # multiview stereo features #https://docs.blender.org/manual/en/2.79/render/workflows/multiview/usage.html
        scene.render.filepath=OutputFolder+"/"+FileName+"" # rgb image file name
        print("saving to:",OutputFolder+"/"+FileName+"")       
        bpy.ops.render.render(write_still=True) # render scene
    #============Render Normal map=============================================================
    
    if  RenderNormal:
        Objects.ReplacePBRbyBSDFMaterials() # PBR material doesnt give good normals replace them
        #scene.render.image_settings.file_format = "PNG"#'OPEN_EXR' # File format
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # Rendering engine
        links.new(r1.outputs['Normal'], composite.inputs['Image']) # Link the nORmal mode to the output node
        scene.render.use_multiview = False # Disable  stereo/displacement images 
        scene.view_layers['View Layer'].use_pass_normal = True
        scene.render.filepath=OutputFolder+"/"+FileName+"_Normal" # set save file name
        bpy.ops.render.render(write_still=True) # Save file 
        
        scene.render.image_settings.file_format = 'OPEN_EXR' # File format with higher depth
        scene.render.image_settings.color_depth = '16'#'16'# depth of image (number of bytes)    
        scene.render.filepath=OutputFolder+"/"+FileName+"_Normal" # Save Again as exr
        bpy.ops.render.render(write_still=True) # Save file
        
        Objects.ReplacePBRbyBSDFMaterials(Inverse=True) # Replace back to the original PBR material
    #===========Render Depth EXR Image=============================================================
    if  RenderDepth:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'  # Rendering engine
        scene.render.image_settings.file_format = 'OPEN_EXR' # File format with higher depth
        scene.render.image_settings.color_depth = '32'#'16'# depth of image (number of bytes)    
        scene = bpy.context.scene
        links.new(r1.outputs['Depth'],composite.inputs['Image']) # link depth node to vfile output node
        scene.render.use_multiview = False # Disable  stereo/displacement images 
        scene.render.filepath = OutputFolder+"/"+FileName+"_Depth" # set depth file path
        bpy.ops.render.render(write_still=True) # save depth file
    #================================================================================================
    links.new(r1.outputs['Image'],composite.inputs['Image']) # link image node to output
        
###############################################################################################################   
############################################################################################################

#                 Render image and save to file

###########################################################################################
def RenderImageAndSave(FileNamePrefix,OutputFolder, RenderImage=True,RenderDepth=True,RenderNormal=True):
    if not os.path.exists(OutputFolder): os.mkdir(OutputFolder)
    else: print("Warining output folder: "+ OutputFolder+ " Already exists")
    #================set render  need to be done once======================================
  #  bpy.ops.object.select_all(action="DESELECT")
    render=bpy.context.scene.render
    #==================go over Selected frames========================================================
#    for k in FramesToRender:
#        bpy.context.scene.frame_set(k)
        #============Render image+depth map + normal=============================================================
    RenderDepthNormalAndImageToFiles(OutputFolder,FileNamePrefix, RenderImage=True,RenderDepth=False,RenderNormal=False) # render scene
#        render.filepath=OutputFolder+"/"+FileNamePrefix+"_Frame_"+str(k)+".jpg"      
#        bpy.ops.render.render(write_still=True)
    print(OutputFolder+"/"+FileNamePrefix+" Saved")

####################################################################################################

#           Save object mask (only unocludded region of the object) turn objects in the name list to white and all other object to black (also turn back ground to black)

###############################################################################################
def SaveObjectVisibleMask(objnames,filepath):
      bpy.context.scene.render.engine = 'BLENDER_EEVEE'
      bpy.context.scene.render.image_settings.file_format = 'PNG'#'OPEN_EXR' # output format
      bpy.context.scene.world= bpy.data.worlds['BackgroundBlack'] # Set Background to black
      for obj in   bpy.data.objects:
          if not obj.type=='MESH': continue

          obj.data.materials.clear()
          material=bpy.data.materials["Black"] # Set 
          for objname in objnames:
            if  obj.name==objname:
                print("white",obj.name)
                material=bpy.data.materials["White"]
                 
              
          obj.data.materials.append(material)
      bpy.context.scene.render.filepath = filepath
      bpy.ops.render.render(write_still=True)
      
####################################################################################################

#           Save object mask full even ocluded parts will appear on the mask, no occlusion turn object to white and hide all other object (also turn back ground to black)

###############################################################################################
def SaveObjectFullMask(objnames,filepath):
      bpy.context.scene.render.engine = 'BLENDER_EEVEE'
      bpy.context.scene.render.image_settings.file_format = 'PNG'#'OPEN_EXR' # output format
      bpy.context.scene.world= bpy.data.worlds['BackgroundBlack'] # Set Background to black
      
      for obj in   bpy.data.objects:
          if not obj.type=='MESH': continue

          obj.data.materials.clear()
          Objects.HideObject(obj.name,Hide=True)
          material=bpy.data.materials["Black"]
          for objname in objnames:
            if  obj.name==objname:
                Objects.HideObject(obj.name,Hide=False)
                material=bpy.data.materials["White"]
          obj.data.materials.append(material)             
          
      bpy.context.scene.render.filepath = filepath
      bpy.ops.render.render(write_still=True)
      
      for obj in   bpy.data.objects: # unhide objects
            if not obj.type=='MESH': continue
            Objects.HideObject(obj.name,Hide=False)
####################################################################################################

#           Create material segmentation map turn all materials to black except 1 which is white do it only for the materials in the object their name in  appear in objectnames

###############################################################################################
def SaveMaterialsMasks(objnames,out_folder):
      print("save materials masks")
      bpy.context.scene.render.engine = 'BLENDER_EEVEE'
      bpy.context.scene.render.image_settings.file_format = 'PNG'#'OPEN_EXR' # output format
      bpy.context.scene.world= bpy.data.worlds['BackgroundBlack'] # Set Background to black
    #-----set all background objects to black-----------------------------------
      for obj in   bpy.data.objects:
          if not obj.type=='MESH': continue
          if obj.name in objnames: continue
          obj.data.materials.clear()
          obj.data.materials.append(bpy.data.materials["Black"]) 
    
      mat_dic={} # data about material in each mask
#    #-----------Set all materials to black----------------------------------             
      for grp in  list(bpy.data.node_groups):
           if 'Material_Group.0' in grp.name:
               grp.nodes["Value"].outputs[0].default_value=0
               grp.links.new(grp.nodes["Value"].outputs[0],grp.nodes["Group Output"].inputs[0])
    #------turn one material white and save----------------------------------------
      for i,grp in  enumerate(list(bpy.data.node_groups)):
           if 'Material_Group.0' in grp.name:
               file_name= "mask" + grp.name.replace("Material_Group.","")+".png"
               grp.nodes["Value"].outputs[0].default_value=255
               grp.links.new(grp.nodes["Value"].outputs[0],grp.nodes["Group Output"].inputs[0])
               bpy.context.scene.render.filepath = out_folder + "//" + file_name
               bpy.ops.render.render(write_still=True)
               grp.nodes["Value"].outputs[0].default_value=0
     
#################################Other parameters#########################################################
