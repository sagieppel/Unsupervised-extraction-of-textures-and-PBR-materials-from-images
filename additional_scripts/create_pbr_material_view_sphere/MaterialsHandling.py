# Load assign and generate materials (PBR/BSDF)

###############################Dependcies######################################################################################3

import bpy
import math
import numpy as np
import bmesh
import os
import shutil
import random
import sys
import colorsys
import uuid
import pickle  
import json
filepath = bpy.data.filepath
directory = os.path.dirname(filepath)
#sys.path.append("/home/breakeroftime/Desktop/Simulations/ModularVesselContent")
sys.path.append(directory)
os.chdir(directory)

#################################################################################################     

# map node fields to indexes (For the BSDF and Volume Absorbtion)

##############################################################################################
def map_name2indx():
    stm = bpy.data.materials['Glass'].node_tree.nodes["Principled BSDF"]
    d={}
    for i in range(len(stm.inputs)):
        fld=stm.inputs[i]
        d[fld.name]=i
    
    stm = bpy.data.materials["TransparentLiquidMaterial"].node_tree.nodes["Volume Absorption"]
    dv={}
    for i in range(len(stm.inputs)):
        fld=stm.inputs[i]
        dv[fld.name]=i
    return d,dv 
#####################################################################################3

# Random multiply (random with different distribution)

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


###############################################################################################################################

###################################################################################################################################

# Transform BSDF Mateiral to dictionary (use to save materials properties)

####################################################################################################################################
def BSDFMaterialToDictionary(Mtr):
    stm=Mtr.node_tree.nodes["Principled BSDF"]
    dic={}
   
    dic["TYPE"]="Principled BSDF"
    dic["Name"]=Mtr.name
    for i in range(len(stm.inputs)):
        if "array" in str(type(stm.inputs[i].default_value)):
                 dic[stm.inputs[i].name]=stm.inputs[i].default_value[:]#*
        else:
                  dic[stm.inputs[i].name]=stm.inputs[i].default_value
    return dic

#############################################################################################################################################

##                       Assign  bsdf Material for object and set random properties (assume material already exist in the blend file)

##############################################################################################################################################
#def AssignMaterialBSDFtoObject(ObjectName, MaterialName):  
#    
#    

#    print("================= Assign bsdf material to object "+ObjectName+" Material "+MaterialName+"=========================================================")
#    bpy.ops.object.select_all(action="DESELECT")
#    bpy.data.objects[ObjectName].select_set(True)
#    bpy.context.view_layer.objects.active = bpy.data.objects[ObjectName] 
#     # Basically pick existing node and assign it to the material and set random properties (this will not work if the node doesnt already exist)          

###-------------------------------Add BSDF material to object============================================
#  
#    print(bpy.data.objects[ObjectName].data.materials)
#    if len(bpy.data.objects[ObjectName].data.materials)==0:
#         bpy.data.objects[ObjectName].data.materials.append(bpy.data.materials[MaterialName])
#    else: # if object already have material replace them
#         for i in range(len(bpy.data.objects[ObjectName].data.materials)):
#                bpy.data.objects[ObjectName].data.materials[i]=bpy.data.materials[MaterialName]
##           
#        

## ----------------------------------Select random property for material --------------------------------------------------------------------------------------      
#      
#    if np.random.rand()<0.9:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = np.random.rand() # Transmission
#    else:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[17].default_value = 1 #Transmission
#    if np.random.rand()<0.8:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = np.random.rand()*np.random.rand()# Roughness
#    else: 
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[9].default_value = 0# Roughness

#    if np.random.rand()<0.9: # color
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1) # random color hsv
#    else:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1, 1,1, 1) # white color
#    if np.random.rand()<0.4:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value = np.random.rand() # metalic
#    elif np.random.rand()<0.7:
#      bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value =0# metalic
#    else:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[6].default_value =1# metalic
#    if np.random.rand()<0.12: # specular
#       stem.inputs[7].default_value = np.random.rand()# specular
#    elif np.random.rand()<0.6:
#      stem.inputs[7].default_value =0.5# specular
#    else:
#      ior=stem.inputs[16].default_value# specular
#      specular=((ior-1)/(ior+1))**2/0.08
#      stem.inputs[7].default_value=specular
#      
#    if np.random.rand()<0.12: # specular tint
#       stem.inputs[8].default_value = np.random.rand()# tint specular
#    else:
#      stem.inputs[8].default_value =0.0# specular tint

#    if np.random.rand()<0.4:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = np.random.rand()# unisotropic
#    else:
#        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[10].default_value = 0# unisotropic
#    if np.random.rand()<0.4:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = np.random.rand()# unisotropic rotation
#    else: 
#        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[11].default_value = 0# unisotropic rotation
#    if np.random.rand()<0.4:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[12].default_value = np.random.rand()# sheen
#    else: 
#        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[12].default_value = 0# sheen
#    if np.random.rand()<0.4:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[13].default_value = np.random.rand()# sheen tint
#    else: 
#        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[13].default_value = 0.5# sheen tint
#    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[14].default_value =0 #Clear Coat
#    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[15].default_value = 0.03# Clear coat
# 
#  
#    bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[16].default_value = 1+np.random.rand()*2.5 #ior index of reflection for transparen objects  
#    #https://pixelandpoly.com/ior.html
#    
#    
#    if np.random.rand()<0.2:
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = np.random.rand()**2*0.4# transmission rouighness
#    else: 
#        bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[18].default_value = 0 # transmission rouighness
#    
#    if np.random.rand()<0.02: # Emission
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[19].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1)# Emission
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[20].default_value = (np.random.rand()**2)*100 # emission strengh
#    else: 
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[19].default_value = (0, 0,0, 1)## transmission rouighness
#       bpy.data.materials[MaterialName].node_tree.nodes["Principled BSDF"].inputs[20].default_value = 0# Transmission strengh
#      
#    bpy.context.object.active_material.use_screen_refraction = True
#####    return BSDFMaterialToDictionary(bpy.data.materials[MaterialName])


###########################################################################

# Randomize mapping for pbr  (assume existing mapping node in stem and randomize it (rotation/scale/translation), stem is a node graph)

###########################################################################
def Randomize_PBR_MaterialMapping(stem):
    # random translation 
    stem["Mapping"].inputs[1].default_value[0] = random.uniform(0, 30)
    stem["Mapping"].inputs[1].default_value[1] = random.uniform(0, 30)
    stem["Mapping"].inputs[1].default_value[2] = random.uniform(0, 30)
    # random rotation
    stem["Mapping"].inputs[2].default_value[0] = random.uniform(0, 6.28318530718)
    stem["Mapping"].inputs[2].default_value[1] = random.uniform(0, 6.28318530718)
    stem["Mapping"].inputs[2].default_value[2] = random.uniform(0, 6.28318530718)
    # random scalling
    r=10**random.uniform(-2, 0.6)
    stem["Mapping"].inputs[3].default_value[0] = r
    stem["Mapping"].inputs[3].default_value[1] = r
    stem["Mapping"].inputs[3].default_value[2] = r
    if random.random()<0.4:
        stem["Mapping"].inputs[3].default_value[0] = 10**random.uniform(-2, 0.6)
        stem["Mapping"].inputs[3].default_value[1] = 10**random.uniform(-2, 0.6)
        stem["Mapping"].inputs[3].default_value[2] = 10**random.uniform(-2, 0.6)
#    else:  
#        stem["Mapping"].inputs[3].default_value[0] = 1
#        stem["Mapping"].inputs[3].default_value[1] = 1
#        stem["Mapping"].inputs[3].default_value[2] = 1
###########################################################################

# Randomize mapping for pbr (assume existing mapping node in stem and randomize it only rotation and translation, stem is a node graph)


###########################################################################
def Randomize_RotateTranslate_PBR_MaterialMapping(stem,RotateMaterial):
    # Random translation
    stem["Mapping"].inputs[1].default_value[0] = random.uniform(0, 30)
    stem["Mapping"].inputs[1].default_value[1] = random.uniform(0, 30)
    stem["Mapping"].inputs[1].default_value[2] = random.uniform(0, 30)
    if RotateMaterial: # Random rotation
        stem["Mapping"].inputs[2].default_value[0] = random.uniform(0, 6.28318530718)
        stem["Mapping"].inputs[2].default_value[1] = random.uniform(0, 6.28318530718)
        stem["Mapping"].inputs[2].default_value[2] = random.uniform(0, 6.28318530718)        
#######################################################################################

## Translate and rotate randomly the PBR texture map on an object to increase variability

############################################################################
#def Randomize_RotateTranslate_TwoPBR_MaterialMapping(stem1,stem2,RotateMaterial):
#    # Random translation
#    mat1=stem1["Mapping"].inputs
#    mat2=stem1["Mapping"].inputs
#    mat1[1].default_value[0] = mat2[2].default_value[0] = random.uniform(0, 30)
#    mat1[1].default_value[1] = mat2[2].default_value[0] = random.uniform(0, 30)
#    mat1[1].default_value[2] = mat2[2].default_value[0] = random.uniform(0, 30)
#    if RotateMaterial: # Random rotation
#        mat1[2].default_value[0] = mat2[2].default_value[0] = random.uniform(0, 6.28318530718)
#        mat1[2].default_value[1] = mat2[2].default_value[0] = random.uniform(0, 6.28318530718)
#        mat1[2].default_value[2] = mat2[2].default_value[0] = random.uniform(0, 6.28318530718)  


###################################################################################################################################

# Transform BSDF Mateiral to dictionary (use to save materials properties for later use)

####################################################################################################################################
def BSDFMaterialToDictionary(bsdf):
    import uuid
    dic={}
    dic["id"] =   str(uuid.uuid4()) # will be use to store and extract material for later use
    for prop in bsdf.inputs:
        if  "array" in str(type(prop.default_value)):
             dic[prop.name] = list(prop.default_value)
        else:
             dic[prop.name] = prop.default_value
        print(prop.name,"=",dic[prop.name])
    return dic
##################################################################################################################################

# LOAD BSDF Mateiral from dictionary (this is use if you want to have same materials in different images

####################################################################################################################################
def BSDFMaterialFromDictionary(bsdf,mat_data_dic):
    for ii,prop in enumerate(bsdf.inputs):
    #   prop.default_value = mat_data_dic[prop.name]     
       bsdf.inputs[ii].default_value  = mat_data_dic[prop.name]      
#########################################################################################################################3

# Generate random BSDF material(stem is existing BSDF node)

########################################################################################################
 
def load_random_BSDF_material(stem):  
    print("Generate BSDF material")
    d,dv = map_name2indx()

           
        

# ----------------------------------Select random property for material --------------------------------------------------------------------------------------      
    #-----------Set random properties for material-----------------------------------------------------
    RGB=colorsys.hsv_to_rgb(np.random.rand(), np.random.rand(),np.random.rand()) # Create random HSV and convert to RGB (HSV have better distrobution)
 
    stem.inputs[d['Base Color']].default_value =  (RGB[0], RGB[1],RGB[2], 1)
  
    stem.inputs[d['Subsurface Weight']].default_value = 0
    if np.random.rand()<0.98:
      stem.inputs[d['Transmission Weight']].default_value = np.random.rand() # Transmission
    else:
      stem.inputs[d['Transmission Weight']].default_value = 1 #Transmission
    if np.random.rand()<0.90:
      stem.inputs[d['Roughness']].default_value = np.random.rand()# Roughness*
    else: 
      stem.inputs[d['Roughness']].default_value = 0# Roughness*


    if np.random.rand()<0.8:
      stem.inputs[d['Metallic']].default_value = np.random.rand() # metalic*
    elif np.random.rand()<0.5:
     stem.inputs[d['Metallic']].default_value =0# metalic*
    else:
      stem.inputs[d['Metallic']].default_value =1# metalic*
    stem.inputs[d["IOR"]].default_value = 1+np.random.rand()*2.5 #ior index of reflection for transparen objects  *#https://pixelandpoly.com/ior.html
    if np.random.rand()<0.12: # specular
      stem.inputs[d['Specular IOR Level']].default_value = np.random.rand()# specular
    elif np.random.rand()<0.6:
     stem.inputs[d['Specular IOR Level']].default_value =0.5# specular
    else:
      ior=stem.inputs[d["IOR"]].default_value# specular
      specular=((ior-1)/(ior+1))**2/0.08
      stem.inputs[d['Specular IOR Level']].default_value=specular
#      
#    if np.random.rand()<0.12: # specular tint
#       stem.inputs[d['Specular Tint']].default_value = (np.random.rand()# tint specular
#    else:
    stem.inputs[d['Specular Tint']].default_value =(1,1,1,1)# specular tint

    if np.random.rand()<0.4:
      stem.inputs[d['Anisotropic']].default_value = np.random.rand()# unisotropic*
    else:
       stem.inputs[d['Anisotropic']].default_value = 0# unisotropic*
    if np.random.rand()<0.4:
      stem.inputs[d['Anisotropic Rotation']].default_value = np.random.rand()# unisotropic rotation
    else: 
       stem.inputs[d['Anisotropic Rotation']].default_value = 0# unisotropic rotation
    if np.random.rand()<0.4:
      stem.inputs[d['Sheen Weight']].default_value = np.random.rand()# sheen
    else: 
       stem.inputs[d['Sheen Weight']].default_value = 0# sheen
    if np.random.rand()<0.6:
      stem.inputs[d['Sheen Tint']].default_value = (1, 1, 1, 1) # sheen tint
    else: 
       stem.inputs[d['Sheen Tint']].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand()) # sheen tint
    stem.inputs[d['Coat Weight']].default_value =np.random.rand()*0.03 #Clear Coat
    stem.inputs[d['Coat Roughness']].default_value = np.random.rand()*0.03 
 
  
   
    
#    
#    if np.random.rand()<0.2:
#      stem.inputs[18].default_value = np.random.rand()**2*0.4# transmission rouighness
#    else: 
#       stem.inputs[18].default_value = 0 # transmission rouighness
    
    if np.random.rand()<0.03: # Emission
      stem.inputs[d['Emission Color']].default_value = (np.random.rand(), np.random.rand(),np.random.rand(), 1)# Emission
      stem.inputs[d['Emission Strength']].default_value = (np.random.rand()**2)*100 # emission strengh
    else: 
      stem.inputs[d['Emission Color']].default_value = (0, 0,0, 1)## emmision color
      stem.inputs[d['Emission Strength']].default_value = 0# emision weight
    stem.inputs[d["Alpha"]].default_value=1

    return BSDFMaterialToDictionary(stem)
  
       
#########################################################################################################################3

# Generate random BSDF material(stem is existing BSDF node)

########################################################################################################
#def load_random_BSDF_material(stem):  
#    #stem = bpy.data.materials[slot].node_tree.nodes["Principled BSDF"]
#    if np.random.rand()<0.9:
#      stem.inputs[17].default_value = np.random.rand() # Transmissionxxxxxxxxxxxxxxxxx
#    else:
#      stem.inputs[17].default_value = 1 #Transmissionxxxxxxxxxxxxxxxxxxx
#    if np.random.rand()<0.7:
#      stem.inputs[9].default_value = np.random.rand()# Roughnessxxxxxxxxxxxxxxxx
#    else: 
#      stem.inputs[9].default_value = 0# Roughnessxxxxxxxxxxxxxxxxxxxxx
#    
#    RGB=colorsys.hsv_to_rgb(np.random.rand(), np.random.rand(),np.random.rand()) # Create random HSV and convert to RGB (HSV have better distrobution)
#    stem.inputs[0].default_value = (RGB[0], RGB[1],RGB[2], 1) # random color hsvxxxxxxxxxxxxxx

#    if np.random.rand()<0.5:
#      stem.inputs[6].default_value = np.random.rand() # metalicxxxxxxxxxxxx
#    elif np.random.rand()<0.38:
#     stem.inputs[6].default_value =0# metalicxxxxxxx
#    else:
#      stem.inputs[6].default_value =1# metalicxxxxxxxxxxxxxxxxxxx


#    if np.random.rand()<0.4:
#      stem.inputs[10].default_value = np.random.rand()# anisotropicxxxxxxxxx
#    else:
#       stem.inputs[10].default_value = 0# anisotropicxxxxxxxxxxxxxxxxxxxxx
#    if np.random.rand()<0.4:
#      stem.inputs[11].default_value = np.random.rand()# anisotropic rotationxxxxxxxxxx
#    else: 
#       stem.inputs[11].default_value = 0# anisotropic rotationxxxxxxxxxxxxx
#    if np.random.rand()<0.4:
#      stem.inputs[12].default_value = np.random.rand()# sheenxxxxxxxxxxxxxxx
#    else: 
#       stem.inputs[12].default_value = 0# sheenxxxxxxxxxxxxxxxxxxxx
#    if np.random.rand()<0.4:
#      stem.inputs[13].default_value = np.random.rand()# sheen tint##############
#    else: 
#       stem.inputs[13].default_value = 0.5# sheen tint######################
#    
# 
#    stem.inputs[16].default_value = 1+np.random.rand()*2.5 #ior index of reflection for transparen objects  
#    #https://pixelandpoly.com/ior.html
#    
#    
#    if np.random.rand()<0.2:
#      stem.inputs[18].default_value = np.random.rand()**2*0.4# transmission rouighness
#    else: 
#       stem.inputs[18].default_value = 0 # transmission rouighness
#    
#    if np.random.rand()<0.015: # Emission
#      stem.inputs[19].default_value = (RGB[0], RGB[1],RGB[2], 1)# Emission
#      stem.inputs[20].default_value = (np.random.rand()**2)*100 # Transmission strengh
#    else: 
#      stem.inputs[19].default_value = (0, 0,0, 1)## transmission rouighness
#      stem.inputs[20].default_value = 1# Transmission strengh
#    stem.inputs[21].default_value = 1# alpha
#    return BSDFMaterialToDictionary(stem)



#########################################################################################################################3

# Generate random transparent BSDF material (stem is existing BSDF node)

########################################################################################################
def load_transparent_BSDF_material(stem):
    
    print("generate transparent material=========================================================")
    
    d,dv = map_name2indx()

#-----------Set random properties for material-----------------------------------------------------
    if np.random.rand()<0.25: # Color
          RGB=colorsys.hsv_to_rgb(np.random.rand(), np.random.rand(),np.random.rand()) # Create random HSV and convert to RGB (HSV have better distrobution)
          stem.inputs[d['Base Color']].default_value =  (RGB[0], RGB[1],RGB[2], 1)
    else:
        rnd=1-np.random.rand()*0.3
        stem.inputs[d['Base Color']].default_value = (rnd, rnd, rnd, rnd) # color
    # index of refraction
#    stem.inputs[d['subsurface']] = stem.inputs[0] # Subsurface
  

    if np.random.rand()<0.1: # Subsurface
        stem.inputs[d['Subsurface Weight']].default_value = np.random.rand()
    else:
        stem.inputs[d['Subsurface Weight']].default_value = 0
   
    if np.random.rand()<0.2: #Transmission
       stem.inputs[d['Transmission Weight']].default_value = 1-0.2*RandPow(4) # Transmission
    else:
       stem.inputs[d['Transmission Weight']].default_value = 1 #Transmission
       
       
    if np.random.rand()<0.2: # Roughnesss
       stem.inputs[d['Roughness']].default_value = 0.2*RandPow(3) # Roughness*
    else: 
       stem.inputs[d['Roughness']].default_value = 0# Roughness*
  
 
   
       
    if np.random.rand()<0.7:# ior index refraction
         stem.inputs[d["IOR"]].default_value = 0.7+np.random.rand()*2 #ior index of reflection for transparen objects   #ior index of reflection for transparen objects*  
    
    else:
        stem.inputs[d["IOR"]].default_value = 1.415+np.random.rand()*0.115 #ior index of reflection for transparen objects*  
    #https://pixelandpoly.com/ior.html

     

    if np.random.rand()<0.1: # Metalic
       stem.inputs[d['Metallic']].default_value = 0.15*RandPow(3)# metalic*
    else:
      stem.inputs[d['Metallic']].default_value =0# metalic*
      
      
    if np.random.rand()<0.12: # specular
       stem.inputs[d['Specular IOR Level']].default_value = np.random.rand()# specular
    elif np.random.rand()<0.6:
      stem.inputs[d['Specular IOR Level']].default_value =0.5# specular
    else:
      ior=stem.inputs[d['Specular IOR Level']].default_value# specular
      specular=((ior-1)/(ior+1))**2/0.08
      stem.inputs[d['Specular IOR Level']].default_value=specular
      

    stem.inputs[d['Specular Tint']].default_value =(1,1,1,1)# specular tint
  
    if np.random.rand()<0.12: # anisotropic
       stem.inputs[d['Anisotropic']].default_value = np.random.rand()# unisotropic*
    else:
      stem.inputs[d['Anisotropic']].default_value =0.0# unisotropic*
  
    if np.random.rand()<0.12: # anisotropic rotation
       stem.inputs[d['Anisotropic Rotation']].default_value = np.random.rand()# unisotropic rotation
    else:
      stem.inputs[d['Anisotropic Rotation']].default_value =0.0# unisotropic
    
#    if np.random.rand()<0.6: #Transmission Roughness
#         stem.inputs[18].default_value = 0.25*RandPow(4) # transmission rouighness
#    else:
#         stem.inputs[18].default_value = 0 # transmission rouighness
    
      
    if np.random.rand()<0.1: # Clear  coat
       stem.inputs[d['Coat Weight']].default_value = np.random.rand()*0.1
    else:
      stem.inputs[d['Coat Roughness']].default_value =0# 

    if np.random.rand()<0.1: # Clear  coat
       stem.inputs[d['Coat Weight']].default_value = np.random.rand()
    else:
      stem.inputs[d['Coat Weight']].default_value =0.03# 
    stem.inputs[d['Sheen Weight']].default_value = 0 # Sheen 
    stem.inputs[d['Sheen Tint']].default_value = (1, 1, 1, 1) # Sheen tint
    
  

    
    stem.inputs[d['Emission Color']].default_value = (1, 1, 1, 1) # Emission
    stem.inputs[d['Emission Strength']].default_value = 0 # Emission stength
    stem.inputs[d["Alpha"]].default_value = random.uniform(0.6,1) # alpha *


    return BSDFMaterialToDictionary(stem) # turn material propeties into dictionary (for saving)
##########################################################################################################################3

## Generate random transparent BSDF material (stem is existing BSDF node)

#########################################################################################################
#def load_transparent_BSDF_material(stem):
##    material = bpy.data.materials['Glass'].copy() 
##    ntree=material.node_tree  
##    stem = ntree.nodes["Principled BSDF"]
#    if np.random.rand()<0.25: # Color
#        stem.inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), np.random.rand())xxxxx
#    else:
#        rnd=1-np.random.rand()*0.3
#        stem.inputs[0].default_value = (rnd, rnd, rnd, rnd)xxxxxxxxxxxx

#    stem.inputs[3].default_value = stem.inputs[0].default_value 


#    if np.random.rand()<0.1: # Subsurfacexxxxxx
#        stem.inputs[1].default_value = np.random.rand()xxxxxxx
#    else:
#        stem.inputs[1].default_value = 0
#   
#    if np.random.rand()<0.5: #Transmission
#        stem.inputs[17].default_value = 1-0.2*RandPow(4) # Transmissionxx
#    else:
#        stem.inputs[17].default_value = 1 #Transmissionxxxxxxx
#       
#       
#    if np.random.rand()<0.5: # Roughnesss
#        stem.inputs[9].default_value = 0.2*RandPow(3) # Roughnessxxx
#    else: 
#        stem.inputs[9].default_value = 0# Roughnessxxxxxxxxxxxxxxxxxx
#  
# 
#   
#       
#    if np.random.rand()<0.7:# ior index refractionxxxxxxxxxxxxxxxxxxxxxx
#          stem.inputs[16].default_value = 0.7+np.random.rand()*2 #ior index of reflection for transparen objects  xxxxxxxxx
#    
#    else:
#         stem.inputs[16].default_value = 1.415+np.random.rand()*0.115 #ior index of reflection for transparen objects  xxxxxxxxxxxxxxx
#    #https://pixelandpoly.com/ior.html

#     

#    if np.random.rand()<0.1: # Metalicxxxxxxxxxxxxxxxxxxxxxxx
#        stem.inputs[6].default_value = 0.15*RandPow(3)# metalic
#    else:
#        stem.inputs[6].default_value =0# meralic
#      
#      
#    if np.random.rand()<0.12: # specularxxxxxxxxxxx
#          stem.inputs[7].default_value = np.random.rand()# specular
#    elif np.random.rand()<0.6:
#          stem.inputs[7].default_value =0.5# specular
#    else:
#       ior=stem.inputs[16].default_value# specularxxxxxxxxxxxxxxxxxxxx
#       specular=((ior-1)/(ior+1))**2/0.08
#       stem.inputs[7].default_value=specular
#      
#    if np.random.rand()<0.12: # specular tint
#        stem.inputs[8].default_value = np.random.rand()# tint specularxxxxxxxxxxxxxxxxxxxx
#    else:
#        stem.inputs[8].default_value =0.0# specular tint
#  
#    if np.random.rand()<0.12: # anisotropic
#        stem.inputs[10].default_value = np.random.rand()# unisotropic
#    else:
#       stem.inputs[10].default_value =0.0# unisotropic
#  
#    if np.random.rand()<0.12: # anisotropic rotation
#        stem.inputs[11].default_value = np.random.rand()# unisotropic rotation
#    else:
#        stem.inputs[11].default_value =0.0# unisotropic
#    
#    if np.random.rand()<0.6: #Transmission Roughness
#           stem.inputs[18].default_value = 0.25*np.random.rand()*np.random.rand() # transmission rouighness
#    else:
#           stem.inputs[18].default_value = 0 # transmission rouighness
#    
#      
#    if np.random.rand()<0.1: # Clear  coat
#          stem.inputs[14].default_value = np.random.rand()
#    else:
#          stem.inputs[14].default_value =0# 

#    if np.random.rand()<0.1: # Clear  coat
#          stem.inputs[15].default_value = np.random.rand()
#    else:
#        stem.inputs[15].default_value =0.03# 
#    stem.inputs[12].default_value = 0 # Sheen 
#    stem.inputs[13].default_value = 0.5 # Sheen tint
#    stem.inputs[19].default_value = (0, 0, 0, 1) # Emission
#    stem.inputs[20].default_value = 0 # Emission stength
#    

#    
#    return BSDFMaterialToDictionary(stem)    


#######################################################################################################

# Replace material on object, set material be the only material of object obj

##############################################################################################################3
def ReplaceMaterial(obj,material):  

#    # Pick method to wrap PBr around object
#        if random.random()<0.55: 
#               nm='Material_pbr_camera_cord'
#        elif random.random()<0.5:
#               nm='Material_pbr_generated_cord' 
#        else:
#               nm='Material_pbr_object_cord'
        if hasattr(obj,'uv_textures'):
            obj.data.uv_textures.clear() 
            uv_textures=obj.data.uv_textures
            while (len(uv_textures)>0):
                  uv_textures = obj.data.uv_textures
                  uv_textures.remove(uv_textures[0])
        
#        for i in range(len(obj.data.materials)):
#            obj.data.materials[i]=material
        obj.data.materials.clear()
       
        obj.data.materials.append(material)
     #   fdfd=sss

####################################################################################################

#   Change UV mapping (the way the material ovelayed on the object )          

########################################################################################################
def ChangeUVmapping(mat,uvmode): # 
    #   'camera' 'generated' 'object'
    print(mat)
    if uvmode == 'object':
          mat.links.new(mat.nodes["Texture Coordinate"].outputs[3],mat.nodes["Mapping"].inputs[0])
    if uvmode == 'generated':
          mat.links.new(mat.nodes["Texture Coordinate"].outputs[0],mat.nodes["Mapping"].inputs[0])
    if uvmode == 'camera':
          mat.links.new(mat.nodes["Texture Coordinate"].outputs[4],mat.nodes["Mapping"].inputs[0])
    if uvmode == 'uv':
          mat.links.new(mat.nodes["Texture Coordinate"].outputs[2],mat.nodes["Mapping"].inputs[0])

#############################################################################################################

# Class for handling materials (loading creating,  and keeping track of materials previously used)


#########################################################################################################
class MaterialHandler():
    
    def __init__(self,pbr_folders,material_dic_file, mode=1):
        
        print("init materials handler")
 
         
        #------------------Create PBR material  list-------------------------------------------------------- 
        self.materials_lst = [] # List of all pbr materials folders path
        if mode==1:
            for fff,fold in enumerate(os.listdir(pbr_folders)): # go over all super folders 
                print("pbr_folders",pbr_folders)
                fold = pbr_folders +"/"+ fold+"/"
                for sdir in  os.listdir(fold): # go over all pbrs in a folder
                    if os.path.isdir(fold):
                        print("fold",fold)
                        pbr_path=fold+"//"+sdir+"//"
                        if os.path.isdir(pbr_path):
                              print("pbr_path",pbr_path)
                              print("Adding material",pbr_path)
                              self.materials_lst.append(pbr_path)
        elif mode == 2:
            for fff,fold in enumerate(os.listdir(pbr_folders)): # go over all super folders 
                print(fff,"pbr_folders",pbr_folders)
                pbr_path = pbr_folders +"/"+ fold+"/"
                if os.path.exists(pbr_folders +"/"+ fold+"/Material_View.jpg"): 
                    print("already done")
                    continue
                self.materials_lst.append(pbr_path)
             
                              
      
    ###    print("self.materials_lst",self.materials_lst)
    
        #------------------load or create material dictionary--------------------------------------------------------------
        self.materials_used = {"pbr":{},"bsdf":{}} # dictionary for all materials used in dataset (keept track on previously used materials, in case you want identify same material in different images).
        if os.path.exists(material_dic_file):
            self.materials_used=json.load(open(material_dic_file,"r"))
        self.materials_in_scene = {} # dictionary for all materials used in  current scene
        self.scene_path="" # folder for current scene 
        self.scene_number=-1 # number of scene 
        self.itr = 0
#        #-----Genearate main material (material that will remain the same between frames)
#        self.main_mat = bpy.data.node_groups["Material_Group"].copy()
#        self.main_mat.name = main_material_name
#        print("Main Material name",self.main_mat.name)
#        self.mat_count = 0 # number of times the main material was used 
#        self.mat_max_uses = max_mat_uses   # maximum number of times/images the main material will be used before it got replaced
#        self.main_material_name =  main_material_name # name of the main material (material that will not be replace between frames)
#        self.LoadRandomMaterial(self.main_mat,mode = 'bsdf')
      ############################################################################################################3

    # initiate scene data 

    ###############################################################################################################

    def initiate_scene_data(self,path,scene_number):
        self.materials_in_scene = {} # dictionary for all materials used in  current scene
        self.scene_path = path # folder for current scene 
        self.scene_number = scene_number # number of scene 
     ############################################################################################################3

    # save scene data 

    ###############################################################################################################

    def save_scene_data(self):
        if len(self.scene_path)==0:
            print("no path exist") # folder for current scene 
        print(self.materials_in_scene)
        for i in range(10): print("*********************************************************************************************************")
        print(self.scene_path)
        print("#####################################################################################################################")
        with open(self.scene_path+"/scene_data.pkl", "wb") as file:
                     pickle.dump(self.materials_in_scene, file)
        print(self.scene_path+"/scene_data.pkl",os.path.exists(self.scene_path+"/scene_data.pkl"))
        for i in range(10): print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(self.scene_path)
#        with open(self.scene_path+"/material_data", "w") as file:
#                     json.dump(self.materials_in_scene, file)
      ############################################################################################################3

    # save full materials data
    ###############################################################################################################

    def save_full_material_data(self,path):
          with open(path+".pkl", "wb") as file:
                     pickle.dump(self.materials_used, file)
#          with open(path+"/material_data", "w") as file:
#                     json.dump(self.materials_in_scene, file)
    #####################################################################################################
    
    
    # add material to dictionary 
    
    #################################################################################################
    def add_to_dic(self,mat_name,mat_data,mode):
        msk_name= "mask" + mat_name.replace("Material_Group.","")+".png" # which mask does the material belong to
        print("mat_data",mat_data)
        if mode == "pbr": id = mat_data # ID will be used as the key in the dictionary will be 
        if mode == "bsdf": id = mat_data["id"]
        mat_info = {"mode":mode,"data":mat_data,"id":id,"path":self.scene_path,"mask name":msk_name}
        self.materials_in_scene[msk_name] =   mat_info # dictionary for all materials used in  current scene
        print("self.materials_in_scene",self.materials_in_scene)
        if not id in self.materials_used[mode]:
            self.materials_used[mode][id] = {"data":mat_data,"id":id,"instance_list":[]}
        self.materials_used[mode][id]["instance_list"].append({"path":self.scene_path,"mask name":msk_name})
        
    
    ####################################################################################################

# load random PBR material
        
########################################################################################################
    def load_random_PBR_material(self,mat,PbrDir=""):
        stem = mat.nodes  # node where the material will be loaded
#        if len(PbrDir)==0:
#            print("Load a new random material")   
#            materials_lst=self.materials_lst
#            rnd=np.random.randint(len(materials_lst)) # pick dataset
#            index = random.randint(0, len(materials_lst[rnd])-1 )
        PbrDir = self.materials_lst[self.itr ] # pick pbr
        self.current_dir = PbrDir
        self.itr+=1
        
        
        print("PBR DIR #################",PbrDir)
        for Fname in os.listdir(PbrDir):
           if ("olor." in Fname)  or ("COLOR." in Fname) or ("ao." in Fname)  or ("AO." in Fname):
              stem["Image Texture.001"].image=bpy.data.images.load(PbrDir+"/"+Fname)          
              print("Color "+ Fname)
           if ("oughness." in Fname) or ("ROUGH." in Fname) or ("roughness" in Fname) or ("ROUGHNESS" in Fname) or ("roughnness" in Fname):
              stem["Image Texture.002"].image=bpy.data.images.load(PbrDir+"/"+Fname)
              print("Roughness "+ Fname)
           if ("ormal." in Fname)  or ("NORM." in Fname) or ("normal" in Fname)  or ("NORMAL" in Fname) or ("Normal" in Fname):
              stem["Image Texture.003"].image=bpy.data.images.load(PbrDir+"/"+Fname)
              print("Normal "+ Fname)
           if ("eight." in Fname) or ("DISP." in Fname) or ("height" in Fname) or ("displacement" in Fname):
              stem["Image Texture"].image=bpy.data.images.load(PbrDir+"/"+Fname)
              print("Height "+ Fname)
           if ("etallic." in Fname) or ("etalness." in Fname)  or ("etal." in Fname) or ("etalic." in Fname) :
              stem["Image Texture.004"].image=bpy.data.images.load(PbrDir+"/"+Fname)
              print("Metallic "+ Fname)
           if ("pecular."  in Fname):
              stem["Image Texture.005"].image=bpy.data.images.load(PbrDir+"/"+Fname)
              print("Specular "+ Fname)
     #   x=dfdfdfdf
      #  Randomize_PBR_MaterialMapping(stem)
        return PbrDir

    ####################################################################################################

    #   Change material mode  (load random material into mat)        

    ########################################################################################################
    def LoadRandomMaterial(self,mat,mode): # Change the type of material by connecting bsdf, pbr, or value 0-255 node to the output node 

        
        print("LOADING RANDOM MATERIAL pbr/bsdf")
       #matprop={} # material properties
        
        if mode == 'bsdf': # 
              
              if np.random.rand()<0.9: # used to be 75
                 mat_data=load_random_BSDF_material(mat.nodes["Principled BSDF.001"])
           
              else:
                 mat_data=load_transparent_BSDF_material(mat.nodes["Principled BSDF.001"])    
                
              mat.links.new(mat.nodes["Principled BSDF.001"].outputs[0],mat.nodes["Group Output"].inputs[0])
              
              
        if mode == 'pbr': # load PBR material to a slot
              mat_data=self.load_random_PBR_material(mat)
              mat.links.new(mat.nodes["Principled BSDF"].outputs[0],mat.nodes["Group Output"].inputs[0])
              print("PBR NAME:",mat_data)
        
        # for segmenetation map basically turn material region to 255,0,0 (white) regardles of illumination and use for 
        if mode == 'white':
               mat.nodes["Value"].outputs[0].default_value = 1
               mat.links.new(mat.nodes["Value"].outputs[0],mat.nodes["Group Output"].inputs[0])
        if mode == 'black':
               mat.nodes["Value"].outputs[0].default_value = 0
               mat.links.new(mat.nodes["Value"].outputs[0],mat.nodes["Group Output"].inputs[0])
         
         
        if mode=="bsdf" or mode == "pbr":
               self.add_to_dic(mat.name,mat_data,mode)
        
      ####################################################################################################

    #  Load existing material that was used in previous images (for recognizing materials across different images), not in use.        

    ########################################################################################################
    def LoadExistingMaterial(self,mat,mode): # Change the type of material by connecting bsdf, pbr this will read from existing materials that was already used in previous images (currently not in use)
        
        print("LOADING RANDOM MATERIAL pbr/bsdf")
       #matprop={} # material properties
        
      
        if  len(list(self.materials_used[mode].keys()))>0:
             # Pick random existing material 
               key = random.choice(list(self.materials_used[mode].keys()))    
               mat_data = self.materials_used[mode][key]["data"]
               id = self.materials_used[mode][key]["id"]
             # check that material is not already in scene
               for msk_name in self.materials_in_scene:
                   if self.materials_in_scene[msk_name]["id"] == id: # if material already in object load a new material
                           return  self.LoadRandomMaterial(mat,mode)
                    
                   
               if mode == 'bsdf':        
                    BSDFMaterialFromDictionary(mat.nodes["Principled BSDF.001"],mat_data) 
               if mode == 'pbr':
                      mat_data=self.load_random_PBR_material(mat,mat_data)
                      mat.links.new(mat.nodes["Principled BSDF"].outputs[0],mat.nodes["Group Output"].inputs[0])
        else:
            return  self.LoadRandomMaterial(mat,mode)
                
                
                
         
        self.add_to_dic(mat.name,mat_data,mode)
