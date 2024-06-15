# Functions for generating UV map from images, and load materials into them
# Note that this function use existing shading node strucure  in .blend file and rewire the nodes in this graphs
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
import SetScene
import time
import json
########################################################################################

#  load random materials to materials slots in materials_dic 

###########################################################################################333
def load_materials(materials_dict,mat_loader):
    print("Load material")
#------set uv mapping mode--------------------------------------------
    rn=random.random()
    if rn<0.7:
       uv='camera'
    elif rn<0.47: 
       uv='object' 
    else: 
        uv='uv'
#--------------------------------------------------
    MaterialDictionary={}
    for mat_name in materials_dict:
        # Pick material type PBR/bsdf
        if random.random()<0.8:# select material type
               matype1='pbr' 
        else:
               matype1='bsdf'
     
        print("mat name",mat_name," mat ",materials_dict[mat_name])
        Materials.ChangeUVmapping(materials_dict[mat_name].node_tree,uvmode = uv) # set uv mapping in the material graph
        #if np.random.rand()<10.9: #***********************************************************************************************
              #MaterialDictionary[mat_name]=
        mat_loader.LoadRandomMaterial(materials_dict[mat_name].node_tree,matype1) # Load random material to materials_dict[mat_name].node_tree. Note that this material already map to the object
#        else:
#            #MaterialDictionary[mat_name]=
#            mat_loader.LoadExistingMaterial(materials_dict[mat_name].node_tree,matype1) # Load existing material that was used in previous images (currently not in use)
#    return  MaterialDictionary
########################################################################################################3



# Use natural image thresholding to create binary uv map with 0-1 values 


###################################################################################################        
def SetPhaseSplitFromImage(phase_sep,images_paths):
    print("Set Phase spli uv map")
   ### x=3
  #  phase_sep.nodes["Separate Color"]
    # set color ramp
    phase_sep.nodes["Separate Color"].mode={0:'RGB',1:'HSV',2:'HSL'}[random.randint(0,2)] # choose map
  #  phase_sep.nodes["ColorRamp"].color_ramp.color_mode="HSV"# [‘RGB’, ‘HSV’, ‘HSL’]
    
#    pos2=pos1*(1-(random.random()**2)*0.33)# pos1
    #-------Choose upper and lower threshold for the fuzy threshold
    if np.random.rand()<0.75:
        pos1=random.random()*0.4+0.3
        pos2=pos1# hard boundaries
    else:
       pos1=random.random()*0.4+0.4# soft boundary threshold
       pos2=pos1*(1-(random.random())*0.25)# pos1
    #----------Set Threshold into Graph----------------------------
    phase_sep.nodes["ColorRamp"].color_ramp.elements[0].position=pos1
    phase_sep.nodes["ColorRamp"].color_ramp.elements[1].position=pos2
    phase_sep.nodes["ColorRamp"].color_ramp.interpolation = "LINEAR" #[‘EASE’, ‘CARDINAL’, ‘LINEAR’, ‘B_SPLINE’, ‘CONSTANT’
     
    indx=random.randint(0,len(images_paths)-1)
    phase_sep.nodes["Image Texture"].image=bpy.data.images.load(images_paths[indx])  
    #------------------Randomize UV map postion/rotation---------------------------
    # Translate
    phase_sep.nodes["Mapping"].inputs[1].default_value[0] = random.uniform(0, 30)
    phase_sep.nodes["Mapping"].inputs[1].default_value[1] = random.uniform(0, 30)
    phase_sep.nodes["Mapping"].inputs[1].default_value[2] = random.uniform(0, 30)
    # Rotate
    phase_sep.nodes["Mapping"].inputs[2].default_value[0] = random.uniform(0, 6.28318530718)
    phase_sep.nodes["Mapping"].inputs[2].default_value[1] = random.uniform(0, 6.28318530718)
    phase_sep.nodes["Mapping"].inputs[2].default_value[2] = random.uniform(0, 6.28318530718)
    # scale
#    scl=1
    #if random.random()<0.4:
    scl=10**random.uniform(-1, 0.2)
    phase_sep.nodes["Mapping"].inputs[3].default_value[0] = scl
    phase_sep.nodes["Mapping"].inputs[3].default_value[1] = scl
    phase_sep.nodes["Mapping"].inputs[3].default_value[2] = scl
    # choos which of the HSV channels will be use to generate the map
    map_mode= random.randint(0,2) 
    phase_sep.links.new(phase_sep.nodes["Separate Color"].outputs[random.randint(0,2)],phase_sep.nodes["ColorRamp"].inputs[0])
    
    
    #------set uve mapping mode 
    uv_mode={0:'generated',1:'object',2:'uv'}[random.randint(0,2)]
    Materials.ChangeUVmapping(phase_sep,uv_mode)
################################################################################################################


# Reccursive create phase splits, basically use binary phase split to create binary tree which split uv map to unlimited splits
# Each image is one splite in the binary tree
#View the uv map as a tree with splits as binary uv maps, and the leafs as the materials. 
#################################################################################################################
def GenerateNodeGraph(ntree,num_phases,bsdf_out, displacement_out,phase_maps = {},materials = {}, num_mats=0, num_splits=0):
     print("recursive generate node graphs for multiphase")
     #-------------  Add new material if leaf node (leaf of the tree are the materials- ---------------------------------
     if num_phases==1: 
         num_mats  += 1
         mat_name = "Material "+str(num_mats)
   
                      
        
         mat = ntree.nodes.new("ShaderNodeGroup")
         materials[num_mats]=mat
         print("***********ADDing matertial",num_mats,"\n\n\n\n",mat)
#         if main_material_name == mat_name: # if its the main material dont create new material but instead 
#            mat.node_tree = bpy.data.node_groups[main_material_name]#.copy()
#         else:
         mat.node_tree = bpy.data.node_groups["Material_Group"].copy()
         mat.name = "Material "+str(num_mats)
         print("Material name",mat.name)
         ##ntree = materials[num_mats].node_tree
         ntree.links.new(mat.outputs[0],bsdf_out)
         ntree.links.new(mat.outputs[1],displacement_out)            
       ### bpy.data.materials['Main Material'].node_tree.nodes[""phase "+str(i)"]
         mat.location = [-(num_mats+num_splits)*200,num_splits*200]
         
         return materials,phase_maps, num_mats, num_splits
    
     # ------------------ Add phase split if branch node (splits are simply binary uv map)----------------------------------
     num_splits += 1
     print("CREATIng split",num_splits,"**********&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
     phsplit = ntree.nodes.new("ShaderNodeGroup")
     phase_maps[num_splits] = phsplit 
     phsplit.node_tree = bpy.data.node_groups['TwoPhaseFromImage'].copy()
     phsplit.name = "Phase Map"+str(num_splits)
     phsplit.location = [-num_splits*200,0]
     ntree.links.new(phsplit.outputs[0],bsdf_out)
     ntree.links.new(phsplit.outputs[1],displacement_out)

     
     num_phases1 = int(np.floor(num_phases/2))
     num_phases2 = int(np.ceil(num_phases/2))
     print("Numphases:",num_phases1,num_phases2)
     materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases1,bsdf_out=phsplit.inputs[0], 
                        displacement_out=phsplit.inputs[2],phase_maps = phase_maps,materials = materials, num_mats = num_mats, num_splits = num_splits)
     materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases2,bsdf_out=phsplit.inputs[1], 
                       displacement_out=phsplit.inputs[3],phase_maps = phase_maps,materials = materials, num_mats = num_mats , num_splits = num_splits)
     return materials,phase_maps, num_mats, num_splits
     
     
     

################################################################################################################3

# Main function for creating phases seperation graph (call GenerateNodeGraph recursively)
# Note look at the Multiphase_Grap in shading  to see how the graph look like (its really hard to understand just from the code). 
###############################################################################################################
def CreateMultiphaseMaterialGraph(num_phases,material_loader,images_paths):
    print("set main material multiphase graph")
    mat = bpy.data.materials.new("Multiphase_Graph")
    mat.use_nodes = True
#    nodes = mat.node_tree.nodes
#    phase_maps = {}
#    materials = {}
    ntree=mat.node_tree
    materials, phase_maps, num_mats, num_splits = GenerateNodeGraph(ntree=ntree,num_phases=num_phases,bsdf_out=ntree.nodes["Material Output"].inputs[0], displacement_out=ntree.nodes["Material Output"].inputs[2],materials={},phase_maps={})
   
#---------------------------set materials properties----------------------------------------------------------------
    #MaterialDictionary = 
    load_materials(materials,material_loader)
#--------------Set phase seperator---------------------------------------------------------------------------------
    
    print("phase map",phase_maps)
    for ky in phase_maps:
        print("KEY",ky)
        SetPhaseSplitFromImage(phase_maps[ky].node_tree,images_paths)
    
    return mat#,  MaterialDictionary  
         
    
##########################################################################################################################