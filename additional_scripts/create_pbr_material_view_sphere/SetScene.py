
# Set Scene create and set camera, set background, set ground plane, clean scene

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
import RenderingAndSaving as RenderSave
#####################################################################################3

# Random multiply

#####################################################################################################################
def RandPow(n):
    r=1
    for i in range(int(n)):
        r*=np.random.rand()
    return r


##############################################################

# Add  multiple point lights to scene

##############################################################
def add_random_point_light(box_min = (-9, -9, -9),box_max = (9, 9, 9),intensity_min=20000,intensity_max=500000):
     (x1, y1, z1) = box_min
     (x2, y2, z2) = box_max
     assert (x1<=x2 and y1<=y2 and z1<=z2)
     min_dist = min(x2-x1,y2-y1,z2-z1)    
     # center only relevant for spot light
     (c1,c2,c3) = ((x1+x2)/2, (y1+y2)/2, (z1+z2)/2)
     (d1,d2,d3) = ((x2-x1)*.05,(y2-y1)*.05,(z2-z1)*.05)
#-------Delete existing light sources-------------------------------------------------------- 
     print("adding light source")
     bpy.ops.object.select_by_type(type='LIGHT')
     bpy.ops.object.delete()

     while(True):
        #---------Select random position------------------------------------------------- 
        x = random.uniform(x1, x2)
        y = random.uniform(y1, y2)
        z = random.uniform(z1, z2)

        
        # Random intensity
        intensity = random.uniform(intensity_min, intensity_max)
        radius = 0.0
        # Random size (radius)
        if random.random() > 0.5: 
             radius = random.uniform(0, min_dist/10)
             if random.random() <0.2:
                    radius = random.uniform(0, 3)
        # Random rotation (direction
        
      #  size = random.uniform(size_min, size_max)
        # source type
        if np.random.rand()<0.5:
            ptype='POINT'
        else:
            ptype='SPOT'
        
        # Directopm    
        direction = None
        
        # Create a new point light
        bpy.ops.object.light_add(type=ptype, radius=radius, align='WORLD', location=(x,y,z))
        new_light = bpy.context.active_object
        
        if (ptype=='SPOT'):
             # add 5% noise to not always directly look at center of BB
             (n1,n2,n3) = (random.uniform(-d1,d1), random.uniform(-d2,d2), random.uniform(-d3,d3))
             (p1,p2,p3) = (c1+n1,c2+n2,c3+n3)
         # Set the light direction
             new_light.rotation_euler = (p1,p2,p3)
             if np.random.rand()<0.4:
                      new_light.rotation_euler = [random.uniform(-3.14159, 3.14159) for _ in range(3)]
             new_light.data.spot_size=radius
        
        # Set the light intensity
        new_light.data.energy = intensity
        if np.random.rand()<0.5: break
     print("done adding light source")


## Add new random lights
#for _ in range(num_lights):
#    add_random_point_light()



###############################################################################################################################

##==============Clean secene remove  all objects currently on the schen============================================

###############################################################################################################################

def CleanScene():
    print("cleaning scene")
    # Clear existing lights in the scene
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()

    for bpy_data_iter in (
            bpy.data.objects,
            bpy.data.meshes,
            bpy.data.cameras,
    ):
        for id_data in bpy_data_iter:
            bpy_data_iter.remove(id_data)
    print("=================Cleaning scene deleting all objects==================================")     
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    allMeshes=[]
    for mes in bpy.data.meshes:
       allMeshes.append(mes)
       print("Deleting Mesh:")
       print(mes)
    for mes in allMeshes:
        bpy.data.meshes.remove(mes)
    bpy.ops.outliner.orphans_purge(num_deleted=630, do_local_ids=True, do_linked_ids=True, do_recursive=True)
    print("Done cleaning")

     

################################################################################################################################3


#            Set random background HDRI from the HDRI Folder (note this function use existing node structure in the blender file)


##################################
###################################################################################################3
def AddBackground(hdr_list): 
    bpy.context.scene.world= bpy.data.worlds['World']

          
#-------------------------------Load random hdri from the list----------------------------------------------------
    u=np.random.randint(len(hdr_list))
    bpy.data.worlds["World"].node_tree.nodes["Environment Texture"].image= bpy.data.images.load(filepath=hdr_list[u])
    
#===================================Set random rotation scale/Intensitiy properties for the hdri==========================    
    
#---------------------------Set uniform or hdri background--------------------------------------------    
  #  bpy.data.worlds["World"].node_tree.nodes["Background.002"].inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), 1)

    bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = 1
#    if np.random.rand()<0.00:
#        bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = np.random.rand()
#        bpy.data.worlds["World"].node_tree.nodes["Background.002"].inputs[0].default_value = (np.random.rand(), np.random.rand(), np.random.rand(), 1)
#    if np.random.rand()<0.00:
#        bpy.data.worlds["World"].node_tree.nodes["Mix Shader.001"].inputs[0].default_value = 0
#   
#----------------------Set Background intensity---------------------------------------------------------    
#    if np.random.rand()<0.5:
#          bpy.data.worlds["World"].node_tree.nodes["Background.001"].inputs[1].default_value = 1+np.random.rand()*1.5
#    else:     
#         bpy.data.worlds["World"].node_tree.nodes["Background.001"].inputs[1].default_value = 1
#     

    
#--------------Rotation-----------------------------------------------   
    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value=(0,0,0)# Rotating
#    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[2] = np.random.rand()*6.28
#    if np.random.rand()<0.50:
#       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[0] = +(np.random.rand()/4-1/8)*6.28
#       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[1] = +(np.random.rand()/4-1/8)*6.28

    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(1,1,1)
#--------------Scale--------------------------    
#    Scale=2**random.uniform(-1,1)
#    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(1,1,1)
#    if np.random.rand()<0.3:
#        bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[3].default_value=(Scale,Scale,Scale)
#################################################################################################################################3


#            Set random rotate background


#####################################################################################################################################3
def RandomRotateBackground():  
       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[2] = np.random.rand()*6.28
       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[0] = +(np.random.rand()/4-1/8)*6.28
       bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[1] = +(np.random.rand()/4-1/8)*6.28



#############################################################################################################

#                    Create ground plane 

####################Add Ground/floor Plane######################################################################################
def AddSphere(name, segments=300, ring_count=60): # sz x0,y0 are cordinates sx,sy are scale
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=ring_count, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

    OriginName=bpy.context.object.name
    bpy.context.object.name = name
    bpy.data.meshes[OriginName].name = name
    bpy.context.object.cycles.use_adaptive_subdivision = True# Allow bumpiness only work at experimental setting optional
    bpy.ops.object.modifier_add(type='SOLIDIFY')

    return bpy.context.object.scale[0], bpy.context.object.scale[1]
    
##############################################################################################################################

#                   Write camera parameters to dicitonary (for saving to file)

##############################################################################################################################   
def CameraParamtersToDictionary():
   # https://mcarletti.github.io/articles/blenderintrinsicparams/
   #https://www.rojtberg.net/1601/from-blender-to-opencv-camera-and-back/
    dic={}
    dic['name']=bpy.context.object.name #= name    
    dic['Focal Length']=bpy.context.object.data.lens #= lens
    dic['Location']=bpy.context.scene.camera.location[:]#=location
    dic['Rotation']=bpy.context.scene.camera.rotation_euler[:]#=rotation
    dic['Perseption']=bpy.context.scene.camera.data.type #= 'PERSP'
    dic['shift_x']=bpy.context.scene.camera.data.shift_x#=shift_x
    dic['shift_y']=bpy.context.scene.camera.data.shift_y#=shift_y
    dic['sensor_width']=bpy.context.object.data.sensor_width 
    dic['sensor_height']=bpy.context.object.data.sensor_height
    dic['sensor_fit']=bpy.context.object.data.sensor_fit
    dic['resolution_y']=bpy.context.scene.render.resolution_y 
    dic['resolution_x']=bpy.context.scene.render.resolution_x 
    dic['pixel_aspect_x']=bpy.context.scene.render.pixel_aspect_x
    dic['pixel_aspect_y']=bpy.context.scene.render.pixel_aspect_y  
    dic['resolution_percentage']=bpy.context.scene.render.resolution_percentage
    dic['scale']=bpy.context.object.scale[:]

    return dic

        
##############################################################################################################################

#                   Add Camera to scene

##############################################################################################################################   
def SetCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0),shift_x=0,shift_y=0):
    
    #=================Set Camera================================
    
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=location, rotation=rotation)
    bpy.context.object.name = name    
    bpy.context.object.data.lens = lens

    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.location=location
    bpy.context.scene.camera.rotation_euler=rotation
    bpy.context.scene.camera.data.type = 'PERSP'
    bpy.context.scene.camera.data.shift_x=shift_x
    bpy.context.scene.camera.data.shift_y=shift_y

##############################################################################
   
#    Change Camera properties location and angle

########################################################################################
def ChangeCamera(name="Camera", lens = 32, location=(0,0,0),rotation=(0, 0, 0),shift_x=0,shift_y=0):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[name] 
    
    bpy.context.object.data.lens = lens
    bpy.context.scene.camera = bpy.context.object
    bpy.context.scene.camera.location=location
    bpy.context.scene.camera.rotation_euler=rotation
    bpy.context.scene.camera.data.type = 'PERSP'
    bpy.context.scene.camera.data.shift_x=shift_x
    bpy.context.scene.camera.data.shift_y=shift_y
########################################################################################################

# Randomly set camera position (so it will look at the main object)

#################################################################
def RandomlySetCameraPos(name,VesWidth,VesHeight):
     print("Randomly set camera position")
     MinDist=np.max([VesWidth,VesHeight])
     R=np.random.rand()*MinDist*3+MinDist*2 
  #   R=np.random.rand()*MinDist*3.5+MinDist*2.5
     print('R='+str(R)+"  MinDist="+str(MinDist))
     Ang=(1.0-1.1*np.random.rand()*np.random.rand())*3.14/2 
     x=0
     y=np.sin(Ang)*R+np.random.rand()*VesWidth-VesWidth/2
     z=np.cos(Ang)*R+VesHeight*np.random.rand()
     rotx=Ang
     rotz=3.14159
     roty=(0.5*np.random.rand()-0.5*np.random.rand())*np.random.rand()
    
     Focal=50 #(np.random.rand()*5+2)*R/np.max([VesWidth,VesHeight])
     shift_x=0#0.2-np.random.rand()*0.4
     shift_y=0#0.2-np.random.rand()*0.4
     SetCamera(name="Camera", lens = Focal, location=(-3.6116271018981934, 0.017461417242884636, 1.6168954372406006),rotation=(1.1344656944274902, 1.312216397764132e-07, -1.5708001852035522),shift_x=shift_x,shift_y=shift_y)
########################################################################################################

# Randomly set camera position (so it will look at the main object)

#################################################################
def RandomlyChangeCameraPos(name,VesWidth,VesHeight):
     print("Randomly set camera position")
     MinDist=np.max([VesWidth,VesHeight])
     R=np.random.rand()*MinDist*4+MinDist*3 
  #   R=np.random.rand()*MinDist*3.5+MinDist*2.5
     print('R='+str(R)+"  MinDist="+str(MinDist))
     Ang=(1.0-1.1*np.random.rand()*np.random.rand())*3.14/2 
     x=0
     y=np.sin(Ang)*R+np.random.rand()*VesWidth-VesWidth/2
     z=np.cos(Ang)*R+VesHeight*np.random.rand()
     rotx=Ang
     rotz=3.14159
     roty=(0.5*np.random.rand()-0.5*np.random.rand())*np.random.rand()
    
     Focal=50 #(np.random.rand()*5+2)*R/np.max([VesWidth,VesHeight])
     shift_x=0#0.2-np.random.rand()*0.4
     shift_y=0#0.2-np.random.rand()*0.4
     ChangeCamera(name="Camera", lens = Focal, location=(x,y,z),rotation=(rotx, roty, rotz),shift_x=shift_x,shift_y=shift_y)
########################################################################################

# Remove all loaded materials from memory (except the one in the KeepMaterials  list) 

###########################################################################################
def ClearMaterials(KeepMaterials): # clean materials from scene all materials except the ones in KeepMaterials
    print("Clearing materials from memory")
    mtlist=[]
    for nm in bpy.data.materials: 
        if nm.name not in KeepMaterials: mtlist.append(nm)
    for nm in mtlist:
        bpy.data.materials.remove(nm)
    
    group_list=[]
    for nm in bpy.data.node_groups: 
        if nm.name not in KeepMaterials: group_list.append(nm)
    for nm in group_list:
        bpy.data.node_groups.remove(nm)
  