# <pep8 compliant>
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

#TODO
#transfer vgroups without deleting existing ones
#draw all edges
#copy modifiers
#copy constraints
#copy bone constraints
#apply LocRotScale after rigifying
#hard surface weights

bl_info = {
    "name": "Khalibloo Panel",
    "version": (1, 0),
    "author": "Khalifa Lame",
    "blender": (2, 70, 0),
    "description": "Broad collection of tools to simplify common repetitive tasks. Includes tools for prepping DAZ Genesis characters and items.",
    "location": "View3D > Properties > Khalibloo panel",
    "category": "Khalibloo"}



if "bpy" in locals():
    #print("Reloading Khalibloo Panel")
    import bmesh
    import math
    
else:
    #print("Loading Khalibloo Panel")
    import bpy
    import bmesh
    import math


#============================================================================
# DEFINE FUNCTIONS since i cant seem to get around the import errors
#============================================================================

rigifyRig = None
genesisRig = None

def isShapeKeyType(obj):
    if ((obj.type == 'MESH') or (obj.type == 'CURVE') or (obj.type == 'SURFACE')):
        return True
    else:
        return False

def isModifierType(obj):
    if ((obj.type == 'MESH') or
        (obj.type == 'CURVE') or
        (obj.type == 'SURFACE') or
        (obj.type == 'FONT') or
        (obj.type == 'LATTICE')):
        return True
    else:
        return False

def copyAllShapeKeys(sourceObject, targetObject):
    shapeKeyIndex = 1
    totalShapeKeyCount = len(sourceObject.data.shape_keys.key_blocks.items())
    while (shapeKeyIndex < totalShapeKeyCount):
        copyShapeKey(shapeKeyIndex, sourceObject, targetObject)
        shapeKeyIndex = shapeKeyIndex + 1

def copyShapeKey(shapeKeyIndex, sourceObject, targetObject):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = sourceObject
    bpy.context.active_object.active_shape_key_index = shapeKeyIndex
    bpy.context.scene.objects.active = targetObject
    bpy.ops.object.shape_key_transfer()


#----------------------------------------------------------

def hardenWeights(obj, vgroupName, spread_vgroups):
    vgroupHard = obj.vertex_groups[vgroupName]
    hardList = []
    vertCount = len(obj.data.vertices.items())
    vertCheckList = []
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(bpy.data.meshes[obj.data.name])
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = vgroupHard.index
    bpy.ops.object.vertex_group_select()
    bpy.context.scene.tool_settings.vertex_group_weight = 1
    for i in range(0, vertCount):
        if (bm.verts[i].select == True):
            hardList.append(i)
    bpy.ops.mesh.hide(unselected = True)
    bpy.ops.mesh.select_all(action='DESELECT')
    for i in range(0, vertCount):
        vert = bm.verts[i]
        if ((vert.index in hardList) and (vert.index not in vertCheckList)):
            vert.select = True
            bpy.ops.mesh.select_linked(limit = False)
            connectedVertList = []
            for i in range(0, vertCount):
                if (bm.verts[i].select == True):
                    connectedVertList.append(i)
            print("connected: " + str(connectedVertList))
            vgroupList = massFindVgroups(obj, connectedVertList)
            for vgroup in vgroupList:
                averageWeight = findAverageWeight(obj, vgroup.name, connectedVertList)
                print ("average = " + str(averageWeight))
                bpy.context.scene.tool_settings.vertex_group_weight = averageWeight
                if (spread_vgroups == False):
                    bpy.ops.mesh.select_all(action='DESELECT')
                    obj.vertex_groups.active_index = vgroup.index
                    bpy.ops.object.vertex_group_select()
                for i in range(0, vertCount):
                    if (bm.verts[i].select == True):
                        if (i not in connectedVertList):
                            bm.verts[i].select = False
                bpy.ops.object.vertex_group_assign()
                #for i in range(0, vertCount):
                    #if (bm.verts[i].select == True):
                        #vertCheckList.append(i)
                bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
                
def findAverageWeight(obj, vgroupName, vertList):
    vgroup = obj.vertex_groups[vgroupName]
    vgroupContent = findVertices(obj, vgroupName)
    weightList = []
    for v in vertList:
        if (v in vgroupContent):
            weight = vgroup.weight(v)
            if (vgroup.weight(v) > 0):
                weightList.append(weight)
        else:
            weightList.append(0)
    averageWeight = sum(weightList) / len(weightList)
    return averageWeight

def massFindVgroups(obj, vertList):
    vgroupList = []
    vgroupCount = len(obj.vertex_groups.keys())
    for i in range(0, vgroupCount):
        vgroup = obj.vertex_groups[i]
        vgroupContent = findVertices(obj, vgroup.name)
        for v in vertList:
            if ((v in vgroupContent) and (vgroup.weight(v) > 0)):
                if (vgroup not in vgroupList):
                    vgroupList.append(vgroup)
    return vgroupList

def findVertices(obj, vgroupName):
    vertList = []
    vgroup = obj.vertex_groups[vgroupName]
    vertCount = len(obj.data.vertices.items())
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(bpy.data.meshes[obj.data.name])
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    obj.vertex_groups.active_index = vgroup.index
    bpy.ops.object.vertex_group_select()
    for v in range (0, vertCount):
        if (bm.verts[v].select == True):
            vertList.append(v)
    return vertList
    

def findVgroups(obj, vIndex):
    vgroupList = []
    vgroupCount = len(obj.vertex_groups.keys())
    for i in range(0, vgroupCount):
        vgroup = obj.vertex_groups[i]
        if (vgroup.weight(vIndex) > 0):
            vgroupList.append(vgroup)
    return vgroupList

def createVgroup(obj, bm, vgroupName, vertList):
    bpy.ops.mesh.select_all(action='DESELECT')
    for v in vertList:
        bm.verts[v].select = True
    bpy.ops.object.vertex_group_add()
    obj.vertex_groups.active.name = vgroupName
    bpy.ops.object.vertex_group_assign()
    bpy.ops.mesh.select_all(action='DESELECT')

def delVgroup(obj, vgroupName):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = obj
    vgroupIndex = obj.vertex_groups[vgroupName].index
    bpy.context.active_object.vertex_groups.active_index = vgroupIndex
    bpy.ops.object.vertex_group_remove()

def findLayer(obj):
    for i in range(0, 20):
        if obj.layers[i]:
            return i

def hideSelect():
    for obj in bpy.context.selected_objects:
        obj.hide_select = True
        
def unhideSelect():
    for obj in bpy.context.scene.objects:
        obj.hide_select = False

def hideRender():
    for obj in bpy.context.selected_objects:
        obj.hide_render = True

def unhideRender():
    for obj in bpy.context.selected_objects:
        obj.hide_render = False

def copyMeshPos(metarig, genesis, targetBone, headOrTail, vgroupName):
    vgroupIndex = genesis.vertex_groups[vgroupName].index
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = genesis
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.context.active_object.vertex_groups.active_index = vgroupIndex
    bpy.ops.object.vertex_group_select()
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    
    if headOrTail == "head":
        bpy.context.active_object.data.edit_bones[targetBone].select_head = True
    if headOrTail == "tail":
        bpy.context.active_object.data.edit_bones[targetBone].select_tail = True
        
    bpy.ops.view3d.snap_selected_to_cursor()
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def copyBonePos(metarig, genesisRig, targetBone, headOrTail, sourceBone):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = genesisRig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    
    if headOrTail == "head":
        bpy.context.active_object.data.edit_bones[sourceBone].select_head = True
    if headOrTail == "tail":
        bpy.context.active_object.data.edit_bones[sourceBone].select_tail = True
        
    bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    
    if headOrTail == "head":
        bpy.context.active_object.data.edit_bones[targetBone].select_head = True
    if headOrTail == "tail":
        bpy.context.active_object.data.edit_bones[targetBone].select_tail = True
            
    bpy.ops.view3d.snap_selected_to_cursor()
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

def metarigPrep(metarig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.active_object.data.use_mirror_x = True
    bpy.context.active_object.data.edit_bones["neck"].use_connect = True
    bpy.ops.object.mode_set(mode='OBJECT')

def metarigFinishingTouches(metarig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["heel.02.L"].head[2] = 0
    bpy.context.active_object.data.edit_bones["heel.02.R"].head[2] = 0
    bpy.context.active_object.data.edit_bones["heel.02.L"].tail[2] = 0
    bpy.context.active_object.data.edit_bones["heel.02.R"].tail[2] = 0
    bpy.context.active_object.data.edit_bones["heel.02.L"].tail[1] = bpy.context.active_object.data.edit_bones["heel.02.L"].head[1]
    bpy.context.active_object.data.edit_bones["heel.02.R"].tail[1] = bpy.context.active_object.data.edit_bones["heel.02.R"].head[1]
    bpy.context.active_object.data.edit_bones["heel.L"].tail[2] = 0
    bpy.context.active_object.data.edit_bones["heel.R"].tail[2] = 0
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

def createFaceRig():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.armature_add(view_align=False, enter_editmode=False, location=(0, 0, 0))
    faceRig = bpy.context.active_object
    bpy.ops.object.mode_set(mode='EDIT')

    #add tongue bones
    #the default bone is the tongue's base
    bpy.context.space_data.cursor_location[0] = 0
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 1
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 2
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 3
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 4
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 5
    bpy.ops.armature.bone_primitive_add()
    #add eye bones
    bpy.context.space_data.cursor_location[0] = 6
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 7
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 8
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 9
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 10
    bpy.ops.armature.bone_primitive_add()
    bpy.context.space_data.cursor_location[0] = 11

    #names
    faceRig.data.edit_bones["Bone"].name = "DEF-tonguebase"
    faceRig.data.edit_bones["Bone.001"].name = "DEF-tongue.01"
    faceRig.data.edit_bones["Bone.002"].name = "DEF-tongue.02"
    faceRig.data.edit_bones["Bone.003"].name = "DEF-tongue.03"
    faceRig.data.edit_bones["Bone.004"].name = "DEF-tongue.04"
    faceRig.data.edit_bones["Bone.005"].name = "DEF-tongue.05"
    faceRig.data.edit_bones["Bone.006"].name = "DEF-tonguetip"
    faceRig.data.edit_bones["Bone.007"].name = "DEF-eye.L"
    faceRig.data.edit_bones["Bone.008"].name = "DEF-eye.R"
    faceRig.data.edit_bones["Bone.009"].name = "IK-eye.L"
    faceRig.data.edit_bones["Bone.010"].name = "IK-eye.R"
    faceRig.data.edit_bones["Bone.011"].name = "IK-eyes_lookat"
    
    #disable deform
    faceRig.data.edit_bones["IK-eye.L"].use_deform = False
    faceRig.data.edit_bones["IK-eye.R"].use_deform = False
    faceRig.data.edit_bones["IK-eyes_lookat"].use_deform = False
    
    #constraints
    bpy.ops.object.mode_set(mode='POSE')
    
    faceRig.data.bones.active = faceRig.data.bones["DEF-eye.L"]
    bpy.ops.pose.constraint_add(type='IK')
    faceRig.pose.bones["DEF-eye.L"].constraints[-1].target = faceRig
    faceRig.pose.bones["DEF-eye.L"].constraints[-1].subtarget = "IK-eye.L"
    faceRig.pose.bones["DEF-eye.L"].constraints[-1].chain_count = 1

    faceRig.data.bones.active = faceRig.data.bones["DEF-eye.R"]
    bpy.ops.pose.constraint_add(type='IK')
    faceRig.pose.bones["DEF-eye.R"].constraints[-1].target = faceRig
    faceRig.pose.bones["DEF-eye.R"].constraints[-1].subtarget = "IK-eye.R"
    faceRig.pose.bones["DEF-eye.R"].constraints[-1].chain_count = 1

    bpy.ops.object.mode_set(mode='OBJECT')

    return faceRig

def faceRigSetParents(faceRig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = faceRig
    bpy.ops.object.mode_set(mode='EDIT')
    
    faceRig.data.edit_bones["DEF-tongue.01"].parent = faceRig.data.edit_bones["DEF-tonguebase"]
    faceRig.data.edit_bones["DEF-tongue.01"].use_connect = True
    
    faceRig.data.edit_bones["DEF-tongue.02"].parent = faceRig.data.edit_bones["DEF-tongue.01"]
    faceRig.data.edit_bones["DEF-tongue.02"].use_connect = True
    
    faceRig.data.edit_bones["DEF-tongue.03"].parent = faceRig.data.edit_bones["DEF-tongue.02"]
    faceRig.data.edit_bones["DEF-tongue.03"].use_connect = True
    
    faceRig.data.edit_bones["DEF-tongue.04"].parent = faceRig.data.edit_bones["DEF-tongue.03"]
    faceRig.data.edit_bones["DEF-tongue.04"].use_connect = True
    
    faceRig.data.edit_bones["DEF-tongue.05"].parent = faceRig.data.edit_bones["DEF-tongue.04"]
    faceRig.data.edit_bones["DEF-tongue.05"].use_connect = True
    
    faceRig.data.edit_bones["DEF-tonguetip"].parent = faceRig.data.edit_bones["DEF-tongue.05"]
    faceRig.data.edit_bones["DEF-tonguetip"].use_connect = True

    faceRig.data.edit_bones["IK-eye.L"].parent = faceRig.data.edit_bones["IK-eyes_lookat"]
    faceRig.data.edit_bones["IK-eye.R"].parent = faceRig.data.edit_bones["IK-eyes_lookat"]

def faceRigFinishingTouches(faceRig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = faceRig
    bpy.ops.object.mode_set(mode='EDIT')

    #Left Eye IK bone
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["DEF-eye.L"].select_tail = True
    bpy.ops.view3d.snap_cursor_to_selected()
    
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eye.L"].select_head = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.5
    bpy.ops.view3d.snap_selected_to_cursor()
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eye.L"].select_tail = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.05
    bpy.ops.view3d.snap_selected_to_cursor()

    #Right Eye IK bone
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["DEF-eye.R"].select_tail = True
    bpy.ops.view3d.snap_cursor_to_selected()
    
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eye.R"].select_head = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.5
    bpy.ops.view3d.snap_selected_to_cursor()
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eye.R"].select_tail = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.05
    bpy.ops.view3d.snap_selected_to_cursor()

    
    #Eyes Look-at Bone
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["DEF-eye.L"].select_tail = True
    bpy.context.active_object.data.edit_bones["DEF-eye.R"].select_tail = True
    bpy.ops.view3d.snap_cursor_to_selected()
    
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eyes_lookat"].select_head = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.5
    bpy.ops.view3d.snap_selected_to_cursor()
    
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["IK-eyes_lookat"].select_tail = True
    cursorY = bpy.context.space_data.cursor_location[1]
    bpy.context.space_data.cursor_location[1] = cursorY - 0.1
    bpy.ops.view3d.snap_selected_to_cursor()

    bpy.ops.armature.select_all(action='SELECT')
    bpy.ops.armature.calculate_roll(type='X')

def setRolls(metarig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.active_object.data.edit_bones["head"].roll = 3.141593
    bpy.context.active_object.data.edit_bones["neck"].roll = 3.141593
    bpy.context.active_object.data.edit_bones["chest"].roll = 3.141593
    bpy.context.active_object.data.edit_bones["spine"].roll = 3.141593
    bpy.context.active_object.data.edit_bones["hips"].roll = 3.141593
    bpy.context.active_object.data.edit_bones["thigh.L"].roll = -0.050401
    bpy.context.active_object.data.edit_bones["shin.L"].roll = -0.015987
    bpy.context.active_object.data.edit_bones["foot.L"].roll = 1.991918
    bpy.context.active_object.data.edit_bones["toe.L"].roll = 1.570715
    bpy.context.active_object.data.edit_bones["heel.L"].roll = 0.0939
    bpy.context.active_object.data.edit_bones["heel.02.L"].roll = 0.0000
    bpy.context.active_object.data.edit_bones["shoulder.L"].roll = 1.563952
    bpy.context.active_object.data.edit_bones["upper_arm.L"].roll = 0.037177
    bpy.context.active_object.data.edit_bones["forearm.L"].roll = -1.49246
    bpy.context.active_object.data.edit_bones["hand.L"].roll = -0.001864
    bpy.context.active_object.data.edit_bones["thumb.01.L"].roll = 0.155141
    bpy.context.active_object.data.edit_bones["thumb.02.L"].roll = -1.202702
    bpy.context.active_object.data.edit_bones["thumb.03.L"].roll = -1.138647
    bpy.context.active_object.data.edit_bones["palm.01.L"].roll = -0.406613
    bpy.context.active_object.data.edit_bones["f_index.01.L"].roll = 0.342358
    bpy.context.active_object.data.edit_bones["f_index.02.L"].roll = 0.954415
    bpy.context.active_object.data.edit_bones["f_index.03.L"].roll = 1.113254
    bpy.context.active_object.data.edit_bones["palm.02.L"].roll = -0.170279
    bpy.context.active_object.data.edit_bones["f_middle.01.L"].roll = 0.35928
    bpy.context.active_object.data.edit_bones["f_middle.02.L"].roll = 1.005646
    bpy.context.active_object.data.edit_bones["f_middle.03.L"].roll = 1.48392
    bpy.context.active_object.data.edit_bones["palm.03.L"].roll = -0.054727
    bpy.context.active_object.data.edit_bones["f_ring.01.L"].roll = 0.044556
    bpy.context.active_object.data.edit_bones["f_ring.02.L"].roll = 0.589653
    bpy.context.active_object.data.edit_bones["f_ring.03.L"].roll = 0.936229
    bpy.context.active_object.data.edit_bones["palm.04.L"].roll = 0.19465
    bpy.context.active_object.data.edit_bones["f_pinky.01.L"].roll = 0.311602
    bpy.context.active_object.data.edit_bones["f_pinky.02.L"].roll = 0.895949
    bpy.context.active_object.data.edit_bones["f_pinky.03.L"].roll = 0.997271
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

def joinFaceRig(faceRig, rigifyRig):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    faceRig.select = True
    rigifyRig.select = True
    bpy.context.scene.objects.active = rigifyRig
    bpy.ops.object.join()

    bpy.ops.object.mode_set(mode='EDIT')
    rigifyRig.data.edit_bones["DEF-eye.L"].parent = rigifyRig.data.edit_bones["DEF-head"]
    rigifyRig.data.edit_bones["DEF-eye.R"].parent = rigifyRig.data.edit_bones["DEF-head"]
    rigifyRig.data.edit_bones["IK-eyes_lookat"].parent = rigifyRig.data.edit_bones["DEF-head"]
    rigifyRig.data.edit_bones["DEF-tonguebase"].parent = rigifyRig.data.edit_bones["DEF-head"]

    rigifyRig.data.edit_bones["DEF-eye.L"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-eye.R"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["IK-eye.L"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["IK-eye.R"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    
    rigifyRig.data.edit_bones["IK-eyes_lookat"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tonguebase"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tongue.01"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tongue.02"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tongue.03"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tongue.04"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tongue.05"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]
    rigifyRig.data.edit_bones["DEF-tonguetip"].layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False]

    bpy.context.object.data.layers[22] = True
    bpy.context.object.show_x_ray = True
    bpy.ops.object.mode_set(mode='OBJECT')

def parentWGTs():
    bpy.ops.object.mode_set(mode='OBJECT')
    objNameList = bpy.data.objects.keys()
    wgtList = []
    for name in objNameList:
        obj = bpy.data.objects[name]
        if (name.startswith("WGT-")):
            wgtList.append(obj)

    if (len(wgtList) > 0):
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        wgtParent = bpy.context.active_object
        wgtParent.name = "WGTs"
        for obj in wgtList:
            obj.parent = wgtParent
            
def moveToJunk(obj):
    obj.layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True]


#-------------------------------------------------------------

def mixVgroups(obj, vgroupA, vgroupB):
    if ((vgroupA in obj.vertex_groups.keys()) and (vgroupB in obj.vertex_groups.keys())):

        backupName = vgroupA + "_copy"
        if (backupName not in obj.vertex_groups.keys()):
            #Create backup
            bpy.ops.object.vertex_group_set_active(group=vgroupA) 
            bpy.ops.object.vertex_group_copy()
        
        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
        #to determine the name of the modifier just created
        length = len(obj.modifiers.keys())
        index = length - 1
        mod_name = obj.modifiers[index].name
        
        obj.modifiers[mod_name].vertex_group_a = vgroupA
        obj.modifiers[mod_name].vertex_group_b = vgroupB
        obj.modifiers[mod_name].mix_mode = 'ADD'
        obj.modifiers[mod_name].mix_set = 'OR'
        bpy.ops.object.modifier_apply(modifier=mod_name)
    
def renameVgroups(obj, oldname, newname):
    if (oldname in obj.vertex_groups.keys()):
        obj.vertex_groups[oldname].name = newname

def setupArmatureModifier(obj, rigifyRig):
    if (len(obj.modifiers.keys()) > 0):
        for modifierName in obj.modifiers.keys():
            if (obj.modifiers[modifierName].type == 'ARMATURE'):
                obj.modifiers["Armature"].use_deform_preserve_volume = True
                if (rigifyRig.name in bpy.context.scene.objects.keys()):
                    obj.modifiers["Armature"].object = rigifyRig



#------------------------------------------------------------------

def checkForMatName(obj, checkName):
    objMatList = obj.material_slots.keys()
    for key in objMatList:
        if (key == checkName):
            #normally, this checkpoint should be useless.
            #the next checkpoint should handle this possibility by itself.
            #I think it's a bug or sth...
            return key
        if (key.startswith(checkName)):
            if (isNameExtension(key, checkName)):
                print(key)
                return key
    print("Check is False")
    return None

def isNameExtension(refName, checkName):
    numerals = "0123456789"
    lenRefName = len(refName)
    lenCheckName = len(checkName)
    if (lenRefName - lenCheckName == 4):
        if (refName[lenCheckName] == "."):
            if (refName[lenCheckName + 1] in numerals):
                if (refName[lenCheckName + 2] in numerals):
                    if (refName[lenCheckName + 3] in numerals):
                        #print("It's a name extension")
                        return True
    #print("It's not a name extension")
    return False

def setupSpecTex(mat, name):
    mat.texture_slots[0].texture.name = name+"-COL"
    texName = name+"-SPEC"
    matList = bpy.context.active_object.material_slots.keys()
    index = matList.index(name)
    bpy.context.object.active_material_index = index
    texCount = len(mat.texture_slots.keys())
    #bpy.context.object.active_material.active_texture_index = texCount
    tex = bpy.data.textures.new(texName, 'IMAGE')
    mat.texture_slots.add()
    mat.texture_slots[texCount].texture = tex
    image = mat.texture_slots[texCount-1].texture.image
    mat.texture_slots[texCount].texture.type = 'IMAGE'
    mat.texture_slots[texCount].texture.image = image
    mat.texture_slots[texCount].texture_coords = 'UV'
    mat.texture_slots[texCount].use_map_color_diffuse = False
    mat.texture_slots[texCount].use_map_specular = True
    mat.texture_slots[texCount].use_rgb_to_intensity = True
    
def setupBumpTex(mat, name):
    mat.texture_slots[0].texture.name = name+"-COL"
    texName = name+"-BUMP"
    matList = bpy.context.active_object.material_slots.keys()
    index = matList.index(name)
    bpy.context.object.active_material_index = index
    texCount = len(mat.texture_slots.keys())
    #bpy.context.object.active_material.active_texture_index = texCount
    tex = bpy.data.textures.new(texName, 'IMAGE')
    mat.texture_slots.add()
    mat.texture_slots[texCount].texture = tex
    image = mat.texture_slots[texCount-1].texture.image
    mat.texture_slots[texCount].texture.type = 'IMAGE'
    mat.texture_slots[texCount].texture.image = image
    mat.texture_slots[texCount].texture_coords = 'UV'
    mat.texture_slots[texCount].use_map_color_diffuse = False
    mat.texture_slots[texCount].use_map_normal = True
    mat.texture_slots[texCount].normal_factor = 0.05
    mat.texture_slots[texCount].use_rgb_to_intensity = True

def genMatMergeList(obj, originalMatList):
    matList = obj.material_slots.keys()
    originalMatListLength = len(originalMatList)
    for m in range(0, originalMatListLength-1):
        n = len(obj.material_slots[m].material.texture_slots.keys())
        if (n == 0):
            index = matList.index(originalMatList[m])
            del matList[index]
        elif (obj.material_slots[m].material.texture_slots[0].texture.type != 'IMAGE'):
            index = matList.index(originalMatList[m])
            del matList[index]
    return matList

def mergeMats(obj, originalMatList):
    matList = genMatMergeList(obj, originalMatList)
    terminationList = []
    checkList = []
    for mainMat in matList:
        if (mainMat not in checkList):
            originalIndex = originalMatList.index(mainMat)
            image = obj.material_slots[mainMat].material.texture_slots[0].texture.image
            for childMat in matList:
                if (childMat not in checkList):
                    if (childMat != mainMat):
                        childIndex = originalMatList.index(childMat)
                        if (obj.material_slots[childMat].material.texture_slots[0].texture.image == image):
                            extractMat(obj, originalIndex, childIndex)
                            checkList.append(childMat)
                            terminationList.append(childMat)
        checkList.append(mainMat)
                    
    delMaterial(obj, terminationList, originalMatList)

def extractMat(obj, mainMatIndex, childMatIndex):
    #bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.context.scene.objects.active = obj
    obj.active_material_index = childMatIndex
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.material_slot_select()
    obj.active_material_index = mainMatIndex
    bpy.ops.object.material_slot_assign()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def delMaterial(obj, terminationList, originalMatList):
        bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.context.scene.objects.active = obj
        for m in terminationList:
            index = originalMatList.index(m)
            obj.active_material_index = index
            del originalMatList[index]
            bpy.ops.object.material_slot_remove()

def texturesOff(obj):
    matCount = len(obj.material_slots.keys())
    if (matCount > 0):
        for matSlot in obj.material_slots:
            matSlot.material.use_textures = [False] * 18
            
def texturesOn(obj):
    matCount = len(obj.material_slots.keys())
    if (matCount > 0):
        for matSlot in obj.material_slots:
            matSlot.material.use_textures = [True] * 18

def materialsRemove(obj):
    matCount = len(obj.material_slots.keys())
    if (matCount > 0):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = obj
        for i in range(0, matCount):
            bpy.ops.object.material_slot_remove()
        
def updateImages():
    return bpy.data.images.keys()

#----------------------------------------------------------------------------

def modifiersRealTimeOff(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_viewport = False
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_viewport = False
        
def modifiersRealTimeOn(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_viewport = True
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_viewport = True
            
def modifiersRenderOff(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_render = False
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_render = False
        
def modifiersRenderOn(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_render = True
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_render = True
            
def modifiersEditModeOff(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_in_edit_mode = False
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_in_edit_mode = False
        
def modifiersEditModeOn(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                obj.modifiers[modName].show_in_edit_mode = True
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    obj.modifiers[modName].show_in_edit_mode = True
            
def modifiersApply(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = obj
        for i in range(0, modCount - 1):
            modName = obj.modifiers[i].name
            if (modFilter == 'ALL'):
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modName)
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modName)
            
def modifiersRemove(obj, modFilter = 'ALL', modType = 'SUBSURF'):
    modList = obj.modifiers.keys()
    modCount = len(modList)
    if (modCount > 0):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = obj
        for modName in modList:
            if (modFilter == 'ALL'):
                bpy.ops.object.modifier_remove(modifier=modName)
            else: #modFilter is 'SPECIFIC'
                if (obj.modifiers[modName].type == modType):
                    bpy.ops.object.modifier_remove(modifier=modName)


#--------------------------------------------------------------------------------

def muteConstraints(obj):
    if (len(obj.constraints.keys()) > 0):
        for con in obj.constraints:
            con.mute = True

def unmuteConstraints(obj):
    if (len(obj.constraints.keys()) > 0):
        for con in obj.constraints:
            con.mute = False

def removeConstraints(obj):
    bpy.context.scene.objects.active = obj
    if (len(obj.constraints.keys()) > 0):
        bpy.ops.object.constraints_clear()

#============================================================================
# DEFINE OPERATORS
#============================================================================

class CopyAllShapeKeys(bpy.types.Operator):
    """Copies all shape keys of selected object(s) to active object"""
    bl_idname = "object.khalibloo_copy_all_shape_keys"
    bl_label = "Copy All Shape Keys"
    
    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (len(context.selected_objects) > 1))

    def execute(self, context):
        if (isShapeKeyType(context.active_object)):
            targetObject = bpy.context.active_object
            targetObjectIndex = bpy.context.selected_objects.index(bpy.context.active_object)
            selectionList = bpy.context.selected_objects
            del selectionList[targetObjectIndex]
            selectionSize = len(selectionList)
            currentObjectIndex = 0
            
            #to avoid problems with active object not having shape keys initially
            bpy.ops.object.shape_key_add(from_mix=False)
            shapeKeysCount = len(targetObject.data.shape_keys.key_blocks)
            
            #but if it already had a shape key, delete the one just created
            if (shapeKeysCount > 1):
                bpy.ops.object.shape_key_remove()
            
            while (currentObjectIndex < selectionSize):
                sourceObject = selectionList[currentObjectIndex]
                bpy.ops.object.select_all(action='DESELECT')
                sourceObject.select = True
                bpy.context.active_object.select = True
                copyAllShapeKeys(sourceObject, targetObject)
                currentObjectIndex = currentObjectIndex + 1
            
        return {'FINISHED'}
    
class HardenWeights(bpy.types.Operator):
    """Harden the weights of the vertex groups of the selected objects."""
    bl_idname = "object.khalibloo_harden_weights"
    bl_label = "Harden Weights"
    
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None)

    def execute(self, context):
        spread_vgroups = bpy.context.scene.khalibloo_spread_harden_vgroups
        objBackup = bpy.context.active_object
        for obj in bpy.context.selected_objects:
            hardenWeights(obj, "khalibloo_hard", spread_vgroups)
        
        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class GenesisRigifySetup(bpy.types.Operator):
    """Generate and setup a rigify rig for the active Genesis figure"""
    bl_idname = "object.khalibloo_genesis_rigify_setup"
    bl_label = "Rigify"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'MESH'))
    
    def execute(self, context):
        genesis = bpy.context.active_object
        global rigifyRig
        global genesisRig
        
        if ((genesis.parent is not None) and (genesis.parent.type == 'ARMATURE')):
            if (len(genesis.data.vertices.items()) == 19296):
                genesisRig = bpy.context.active_object.parent

                genesisRig.hide = False
                bpy.context.scene.layers[findLayer(genesisRig)] = True
                

                #VERTEX GROUPS RAW DATA
                bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.from_edit_mesh(bpy.data.meshes[genesis.data.name])
                
                head_tail = [3189, 3230]
                chest_head = [181, 182, 183, 184, 189, 190, 192, 3956, 3957, 4111, 4170, 4501,
                              4503, 4514, 4675, 4738, 4744, 4770, 4773, 4782, 4783, 4784,
                                4785, 4794, 4801, 4830, 4989, 4997, 4998, 4999, 5001, 5003,
                                5005, 5006, 5008, 5009, 5010, 5011, 5013, 5014, 5015, 5028,
                                6425, 6426, 6427, 6428, 6482, 6485, 6494, 6495, 6506, 6516,
                                6517, 6518, 6519, 9617, 9618, 9619, 9620, 9625, 9626, 9628,
                                13267, 13268, 13421, 13474, 13783, 13785, 13796, 13950, 14011,
                                14017, 14043, 14046, 14055, 14056, 14057, 14058, 14067, 14074,
                                14103, 14249, 14257, 14258, 14259, 14261, 14263, 14265, 14266,
                                14268, 14269, 14270, 14271, 14273, 14274, 14285, 15648, 15649,
                                15650, 15651, 15705, 15708, 15717, 15718, 15729, 15739, 15740,
                                15741, 15742]
                spine_head = [3943, 4834, 4870, 4973, 4986, 5063, 5068, 5074, 5075, 5076, 5077,
                              5078, 5079, 5080, 5081, 5082, 5083, 5084, 5085, 5086, 5087, 5088,
                              5089, 5090, 5100, 5108, 5109, 5110, 5111, 5112, 5113, 5114, 5115,
                              5116, 5117, 5118, 5119, 5120, 5121, 5122, 5123, 5124, 6522, 6523,
                              6524, 6525, 13254, 14107, 14140, 14233, 14246, 14318, 14323, 14329,
                              14330, 14331, 14332, 14333, 14334, 14335, 14336, 14337, 14338, 14339,
                              14340, 14341, 14342, 14343, 14344, 14354, 14359, 14360, 14361, 14362,
                              14363, 14364, 14365, 14366, 14367, 14368, 14369, 14370, 14371, 14372,
                              14373, 14374, 15745, 15746, 15747, 15748]
                hips_head = [166, 454, 483, 484, 485, 486, 487, 488, 489, 491, 492, 502, 507, 510,
                            511, 539, 542, 608, 609, 610, 611, 612, 613, 3780, 3781, 3837, 3920,
                            3923, 3932, 3933, 4365, 6466, 6467, 6472, 6473, 9272, 9277, 9602, 9890,
                            9919, 9920, 9921, 9922, 9923, 9924, 9925, 9927, 9928, 9938, 9943, 9946,
                            9947, 9975, 9978, 10044, 10045, 10046, 10047, 10048, 10049, 13091, 13092,
                            13148, 13231, 13234, 13243, 13244, 13659, 15689, 15690, 15695, 15696,
                            18426, 18431]
                toe_tail_L = [1288]
                heel_tail_L = [6575, 6586]
                heel02_head_L = [289]
                heel02_tail_L = [1410, 1451]
                hand_tail_L = [1561, 1742, 1779, 1781, 1783, 5140, 6400, 6643, 6644]
                thumbtip_L = [1602, 1603]
                indextip_L = [5778, 5850]
                midtip_L = [5926, 5998]
                ringtip_L = [6074, 6146]
                pinkytip_L = [6222, 6294]
                indexcarp_L = [1646, 1686, 1689, 1690, 1830, 1841, 1852, 1874, 6642]
                midcarp_L = [1584, 1670, 1751, 1796, 1798, 1801, 1809, 1873, 1874, 1875]
                ringcarp_L = [1648, 1666, 1693, 1695, 1696, 1697, 1767, 1768, 1788, 1791, 1801, 6404]
                pinkycarp_L = [1668, 1692, 1693, 1713, 1791, 1794]
                #face rig
                eye_head_L = [3385, 3386, 3389, 3391, 3393, 3395, 3397, 3399, 3401, 3403, 3405, 3407,
                              3409, 3411, 3413, 3415]
                eye_head_R = [12700, 12701, 12704, 12706, 12708, 12710, 12712, 12714, 12716, 12718,
                              12720, 12722, 12724, 12726, 12728, 12730]
                eye_tail_L = [3516]
                eye_tail_R = [12831]
                tonguetip_tail = [7342]
                
                createVgroup(genesis, bm, "metarig_head_tail", head_tail)
                createVgroup(genesis, bm, "metarig_chest_head", chest_head)
                createVgroup(genesis, bm, "metarig_spine_head", spine_head)
                createVgroup(genesis, bm, "metarig_hips_head", hips_head)
                createVgroup(genesis, bm, "metarig_toe_tail.L", toe_tail_L)
                createVgroup(genesis, bm, "metarig_heel_tail.L", heel_tail_L)
                createVgroup(genesis, bm, "metarig_heel02_head.L", heel02_head_L)
                createVgroup(genesis, bm, "metarig_heel02_tail.L", heel02_tail_L)
                createVgroup(genesis, bm, "metarig_hand_tail.L", hand_tail_L)
                createVgroup(genesis, bm, "metarig_thumbtip.L", thumbtip_L)
                createVgroup(genesis, bm, "metarig_indextip.L", indextip_L)
                createVgroup(genesis, bm, "metarig_midtip.L", midtip_L)
                createVgroup(genesis, bm, "metarig_ringtip.L", ringtip_L)
                createVgroup(genesis, bm, "metarig_pinkytip.L", pinkytip_L)
                createVgroup(genesis, bm, "metarig_indexcarp.L", indexcarp_L)
                createVgroup(genesis, bm, "metarig_midcarp.L", midcarp_L)
                createVgroup(genesis, bm, "metarig_ringcarp.L", ringcarp_L)
                createVgroup(genesis, bm, "metarig_pinkycarp.L", pinkycarp_L)
                #face rig
                createVgroup(genesis, bm, "metarig_eye_head.L", eye_head_L)
                createVgroup(genesis, bm, "metarig_eye_head.R", eye_head_R)
                createVgroup(genesis, bm, "metarig_eye_tail.L", eye_tail_L)
                createVgroup(genesis, bm, "metarig_eye_tail.R", eye_tail_R)
                createVgroup(genesis, bm, "metarig_tonguetip_tail", tonguetip_tail)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.armature_human_metarig_add()
                metarig = bpy.context.active_object
                
                metarigPrep(metarig)
                
                copyMeshPos(metarig, genesis, "head", "tail", "metarig_head_tail")
                copyMeshPos(metarig, genesis, "chest", "head", "metarig_chest_head")
                copyMeshPos(metarig, genesis, "spine", "head", "metarig_spine_head")
                copyMeshPos(metarig, genesis, "hips", "head", "metarig_hips_head")
                copyMeshPos(metarig, genesis, "toe.L", "tail", "metarig_toe_tail.L")
                copyMeshPos(metarig, genesis, "heel.L", "tail", "metarig_heel_tail.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "head", "metarig_heel02_head.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "tail", "metarig_heel02_tail.L")
                copyMeshPos(metarig, genesis, "hand.L", "tail", "metarig_hand_tail.L")
                copyMeshPos(metarig, genesis, "thumb.03.L", "tail", "metarig_thumbtip.L")
                copyMeshPos(metarig, genesis, "f_index.03.L", "tail", "metarig_indextip.L")
                copyMeshPos(metarig, genesis, "f_middle.03.L", "tail", "metarig_midtip.L")
                copyMeshPos(metarig, genesis, "f_ring.03.L", "tail", "metarig_ringtip.L")
                copyMeshPos(metarig, genesis, "f_pinky.03.L", "tail", "metarig_pinkytip.L")
                copyMeshPos(metarig, genesis, "palm.01.L", "head", "metarig_indexcarp.L")
                copyMeshPos(metarig, genesis, "palm.02.L", "head", "metarig_midcarp.L")
                copyMeshPos(metarig, genesis, "palm.03.L", "head", "metarig_ringcarp.L")
                copyMeshPos(metarig, genesis, "palm.04.L", "head", "metarig_pinkycarp.L")
                
                copyBonePos(metarig, genesisRig, "neck", "head", "neck")
                copyBonePos(metarig, genesisRig, "neck", "tail", "neck")
                copyBonePos(metarig, genesisRig, "thigh.L", "head", "lThigh")
                copyBonePos(metarig, genesisRig, "shin.L", "head", "lShin")
                copyBonePos(metarig, genesisRig, "shin.L", "tail", "lShin")
                #copyBonePos(metarig, genesisRig, "foot.L", "head", "lFoot")
                copyBonePos(metarig, genesisRig, "toe.L", "head", "lToe")
                copyBonePos(metarig, genesisRig, "shoulder.L", "head", "lCollar")
                copyBonePos(metarig, genesisRig, "shoulder.L", "tail", "lCollar")
                copyBonePos(metarig, genesisRig, "upper_arm.L", "head", "lShldr")
                copyBonePos(metarig, genesisRig, "forearm.L", "head", "lForeArm")
                copyBonePos(metarig, genesisRig, "forearm.L", "tail", "lForeArm")
                copyBonePos(metarig, genesisRig, "thumb.01.L", "head", "lThumb1")
                copyBonePos(metarig, genesisRig, "thumb.02.L", "head", "lThumb2")
                copyBonePos(metarig, genesisRig, "thumb.03.L", "head", "lThumb3")
                copyBonePos(metarig, genesisRig, "f_index.01.L", "head", "lIndex1")
                copyBonePos(metarig, genesisRig, "f_index.02.L", "head", "lIndex2")
                copyBonePos(metarig, genesisRig, "f_index.03.L", "head", "lIndex3")
                copyBonePos(metarig, genesisRig, "f_middle.01.L", "head", "lMid1")
                copyBonePos(metarig, genesisRig, "f_middle.02.L", "head", "lMid2")
                copyBonePos(metarig, genesisRig, "f_middle.03.L", "head", "lMid3")
                copyBonePos(metarig, genesisRig, "f_ring.01.L", "head", "lRing1")
                copyBonePos(metarig, genesisRig, "f_ring.02.L", "head", "lRing2")
                copyBonePos(metarig, genesisRig, "f_ring.03.L", "head", "lRing3")
                copyBonePos(metarig, genesisRig, "f_pinky.01.L", "head", "lPinky1")
                copyBonePos(metarig, genesisRig, "f_pinky.02.L", "head", "lPinky2")
                copyBonePos(metarig, genesisRig, "f_pinky.03.L", "head", "lPinky3")
                
                metarigFinishingTouches(metarig)
                setRolls(metarig)
                
                delVgroup(genesis, "metarig_head_tail")
                delVgroup(genesis, "metarig_chest_head")
                delVgroup(genesis, "metarig_spine_head")
                delVgroup(genesis, "metarig_hips_head")
                delVgroup(genesis, "metarig_toe_tail.L")
                delVgroup(genesis, "metarig_heel_tail.L")
                delVgroup(genesis, "metarig_heel02_head.L")
                delVgroup(genesis, "metarig_heel02_tail.L")
                delVgroup(genesis, "metarig_hand_tail.L")
                delVgroup(genesis, "metarig_thumbtip.L")
                delVgroup(genesis, "metarig_indextip.L")
                delVgroup(genesis, "metarig_midtip.L")
                delVgroup(genesis, "metarig_ringtip.L")
                delVgroup(genesis, "metarig_pinkytip.L")
                delVgroup(genesis, "metarig_indexcarp.L")
                delVgroup(genesis, "metarig_midcarp.L")
                delVgroup(genesis, "metarig_ringcarp.L")
                delVgroup(genesis, "metarig_pinkycarp.L")

                #face rig
                faceRig = createFaceRig()
                print(faceRig.name)
                faceRigSetParents(faceRig)
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "DEF-tonguetip", "tail", "metarig_tonguetip_tail")

                copyBonePos(faceRig, genesisRig, "DEF-tonguebase", "head", "tongueBase")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.01", "head", "tongue01")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.02", "head", "tongue02")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.03", "head", "tongue03")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.04", "head", "tongue04")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.05", "head", "tongue05")
                copyBonePos(faceRig, genesisRig, "DEF-tonguetip", "head", "tongueTip")
                faceRigFinishingTouches(faceRig)

                delVgroup(genesis, "metarig_eye_head.L")
                delVgroup(genesis, "metarig_eye_head.R")
                delVgroup(genesis, "metarig_eye_tail.L")
                delVgroup(genesis, "metarig_eye_tail.R")
                delVgroup(genesis, "metarig_tonguetip_tail")
                
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.context.scene.objects.active = metarig
                bpy.ops.pose.rigify_generate()
                rigifyRig = bpy.context.active_object
                rigifyRig.name = genesis.name + "-rig"
                #fix neck issue
                bpy.ops.object.khalibloo_rigify_neck_fix()
                parentWGTs()
                
                joinFaceRig(faceRig, rigifyRig)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = genesis
                genesis.select = True
        return {'FINISHED'}

class Genesis2FemaleRigifySetup(bpy.types.Operator):
    """Generate and setup a rigify rig for the active Genesis 2 Female figure"""
    bl_idname = "object.khalibloo_genesis2female_rigify_setup"
    bl_label = "Rigify"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'MESH'))
    
    def execute(self, context):
        genesis = bpy.context.active_object
        global rigifyRig
        global genesisRig
        
        if ((genesis.parent is not None) and (genesis.parent.type == 'ARMATURE')):
            if (len(genesis.data.vertices.items()) == 21556):
                genesisRig = bpy.context.active_object.parent

                genesisRig.hide = False
                bpy.context.scene.layers[findLayer(genesisRig)] = True


                #VERTEX GROUPS RAW DATA
                bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.from_edit_mesh(bpy.data.meshes[genesis.data.name])
                
                head_tail = [2054, 2087]
                chest_head = [10671, 21322]
                spine_head = [2926, 13724]
                hips_head = [7848, 18528]
                toe_tail_L = [789]
                heel_tail_L = [4128, 4133]
                heel02_head_L = [9337]
                heel02_tail_L = [8623]
                hand_tail_L = [1076, 2957, 3988, 4176, 9423, 9445, 9446]
                thumbtip_L = [964, 965]
                indextip_L = [3380, 3452]
                midtip_L = [3528, 3600]
                ringtip_L = [3676, 3748]
                pinkytip_L = [3824, 3896]
                indexcarp_L = [9404, 9409, 9692]
                midcarp_L = [1085, 9430, 9437]
                ringcarp_L = [1083, 9459, 9465]
                pinkycarp_L = [1008, 9484, 9515]
                #face rig
                eye_head_L = [2191, 2192, 2195, 2197, 8267, 8268, 8271, 8273, 8301, 8323, 8325, 8327, 8357, 8359, 8361, 8382]
                eye_head_R = [13023, 13024, 13027, 13029, 18938, 18939, 18942, 18944, 18972, 18994, 18996, 18998, 19028,
                              19030, 19032, 19053]
                eye_tail_L = [8313]
                eye_tail_R = [18984]
                tonguetip_tail = [4863]
                
                createVgroup(genesis, bm, "metarig_head_tail", head_tail)
                createVgroup(genesis, bm, "metarig_chest_head", chest_head)
                createVgroup(genesis, bm, "metarig_spine_head", spine_head)
                createVgroup(genesis, bm, "metarig_hips_head", hips_head)
                createVgroup(genesis, bm, "metarig_toe_tail.L", toe_tail_L)
                createVgroup(genesis, bm, "metarig_heel_tail.L", heel_tail_L)
                createVgroup(genesis, bm, "metarig_heel02_head.L", heel02_head_L)
                createVgroup(genesis, bm, "metarig_heel02_tail.L", heel02_tail_L)
                createVgroup(genesis, bm, "metarig_hand_tail.L", hand_tail_L)
                createVgroup(genesis, bm, "metarig_thumbtip.L", thumbtip_L)
                createVgroup(genesis, bm, "metarig_indextip.L", indextip_L)
                createVgroup(genesis, bm, "metarig_midtip.L", midtip_L)
                createVgroup(genesis, bm, "metarig_ringtip.L", ringtip_L)
                createVgroup(genesis, bm, "metarig_pinkytip.L", pinkytip_L)
                createVgroup(genesis, bm, "metarig_indexcarp.L", indexcarp_L)
                createVgroup(genesis, bm, "metarig_midcarp.L", midcarp_L)
                createVgroup(genesis, bm, "metarig_ringcarp.L", ringcarp_L)
                createVgroup(genesis, bm, "metarig_pinkycarp.L", pinkycarp_L)
                #face rig
                createVgroup(genesis, bm, "metarig_eye_head.L", eye_head_L)
                createVgroup(genesis, bm, "metarig_eye_head.R", eye_head_R)
                createVgroup(genesis, bm, "metarig_eye_tail.L", eye_tail_L)
                createVgroup(genesis, bm, "metarig_eye_tail.R", eye_tail_R)
                createVgroup(genesis, bm, "metarig_tonguetip_tail", tonguetip_tail)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.armature_human_metarig_add()
                metarig = bpy.context.active_object
                
                metarigPrep(metarig)
                
                copyMeshPos(metarig, genesis, "head", "tail", "metarig_head_tail")
                copyMeshPos(metarig, genesis, "chest", "head", "metarig_chest_head")
                copyMeshPos(metarig, genesis, "spine", "head", "metarig_spine_head")
                copyMeshPos(metarig, genesis, "hips", "head", "metarig_hips_head")
                copyMeshPos(metarig, genesis, "toe.L", "tail", "metarig_toe_tail.L")
                copyMeshPos(metarig, genesis, "heel.L", "tail", "metarig_heel_tail.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "head", "metarig_heel02_head.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "tail", "metarig_heel02_tail.L")
                copyMeshPos(metarig, genesis, "hand.L", "tail", "metarig_hand_tail.L")
                copyMeshPos(metarig, genesis, "thumb.03.L", "tail", "metarig_thumbtip.L")
                copyMeshPos(metarig, genesis, "f_index.03.L", "tail", "metarig_indextip.L")
                copyMeshPos(metarig, genesis, "f_middle.03.L", "tail", "metarig_midtip.L")
                copyMeshPos(metarig, genesis, "f_ring.03.L", "tail", "metarig_ringtip.L")
                copyMeshPos(metarig, genesis, "f_pinky.03.L", "tail", "metarig_pinkytip.L")
                copyMeshPos(metarig, genesis, "palm.01.L", "head", "metarig_indexcarp.L")
                copyMeshPos(metarig, genesis, "palm.02.L", "head", "metarig_midcarp.L")
                copyMeshPos(metarig, genesis, "palm.03.L", "head", "metarig_ringcarp.L")
                copyMeshPos(metarig, genesis, "palm.04.L", "head", "metarig_pinkycarp.L")
                
                copyBonePos(metarig, genesisRig, "neck", "head", "neck")
                copyBonePos(metarig, genesisRig, "neck", "tail", "neck")
                copyBonePos(metarig, genesisRig, "thigh.L", "head", "lThigh")
                copyBonePos(metarig, genesisRig, "shin.L", "head", "lShin")
                copyBonePos(metarig, genesisRig, "shin.L", "tail", "lShin")
                #copyBonePos(metarig, genesisRig, "foot.L", "head", "lFoot")
                copyBonePos(metarig, genesisRig, "toe.L", "head", "lToe")
                copyBonePos(metarig, genesisRig, "shoulder.L", "head", "lCollar")
                copyBonePos(metarig, genesisRig, "shoulder.L", "tail", "lCollar")
                copyBonePos(metarig, genesisRig, "upper_arm.L", "head", "lShldr")
                copyBonePos(metarig, genesisRig, "forearm.L", "head", "lForeArm")
                copyBonePos(metarig, genesisRig, "forearm.L", "tail", "lForeArm")
                copyBonePos(metarig, genesisRig, "thumb.01.L", "head", "lThumb1")
                copyBonePos(metarig, genesisRig, "thumb.02.L", "head", "lThumb2")
                copyBonePos(metarig, genesisRig, "thumb.03.L", "head", "lThumb3")
                copyBonePos(metarig, genesisRig, "f_index.01.L", "head", "lIndex1")
                copyBonePos(metarig, genesisRig, "f_index.02.L", "head", "lIndex2")
                copyBonePos(metarig, genesisRig, "f_index.03.L", "head", "lIndex3")
                copyBonePos(metarig, genesisRig, "f_middle.01.L", "head", "lMid1")
                copyBonePos(metarig, genesisRig, "f_middle.02.L", "head", "lMid2")
                copyBonePos(metarig, genesisRig, "f_middle.03.L", "head", "lMid3")
                copyBonePos(metarig, genesisRig, "f_ring.01.L", "head", "lRing1")
                copyBonePos(metarig, genesisRig, "f_ring.02.L", "head", "lRing2")
                copyBonePos(metarig, genesisRig, "f_ring.03.L", "head", "lRing3")
                copyBonePos(metarig, genesisRig, "f_pinky.01.L", "head", "lPinky1")
                copyBonePos(metarig, genesisRig, "f_pinky.02.L", "head", "lPinky2")
                copyBonePos(metarig, genesisRig, "f_pinky.03.L", "head", "lPinky3")
                metarigFinishingTouches(metarig)
                setRolls(metarig)
                
                delVgroup(genesis, "metarig_head_tail")
                delVgroup(genesis, "metarig_chest_head")
                delVgroup(genesis, "metarig_spine_head")
                delVgroup(genesis, "metarig_hips_head")
                delVgroup(genesis, "metarig_toe_tail.L")
                delVgroup(genesis, "metarig_heel_tail.L")
                delVgroup(genesis, "metarig_heel02_head.L")
                delVgroup(genesis, "metarig_heel02_tail.L")
                delVgroup(genesis, "metarig_hand_tail.L")
                delVgroup(genesis, "metarig_thumbtip.L")
                delVgroup(genesis, "metarig_indextip.L")
                delVgroup(genesis, "metarig_midtip.L")
                delVgroup(genesis, "metarig_ringtip.L")
                delVgroup(genesis, "metarig_pinkytip.L")
                delVgroup(genesis, "metarig_indexcarp.L")
                delVgroup(genesis, "metarig_midcarp.L")
                delVgroup(genesis, "metarig_ringcarp.L")
                delVgroup(genesis, "metarig_pinkycarp.L")

                #face rig
                faceRig = createFaceRig()
                print(faceRig.name)
                faceRigSetParents(faceRig)
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "DEF-tonguetip", "tail", "metarig_tonguetip_tail")

                copyBonePos(faceRig, genesisRig, "DEF-tonguebase", "head", "tongueBase")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.01", "head", "tongue01")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.02", "head", "tongue02")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.03", "head", "tongue03")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.04", "head", "tongue04")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.05", "head", "tongue05")
                copyBonePos(faceRig, genesisRig, "DEF-tonguetip", "head", "tongueTip")
                faceRigFinishingTouches(faceRig)

                delVgroup(genesis, "metarig_eye_head.L")
                delVgroup(genesis, "metarig_eye_head.R")
                delVgroup(genesis, "metarig_eye_tail.L")
                delVgroup(genesis, "metarig_eye_tail.R")
                delVgroup(genesis, "metarig_tonguetip_tail")
                
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.context.scene.objects.active = metarig
                bpy.ops.pose.rigify_generate()
                rigifyRig = bpy.context.active_object
                rigifyRig.name = genesis.name + "-rig"
                #fix neck issue
                bpy.ops.object.khalibloo_rigify_neck_fix()
                parentWGTs()
        
                joinFaceRig(faceRig, rigifyRig)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = genesis
                genesis.select = True
        return {'FINISHED'}

class Genesis2MaleRigifySetup(bpy.types.Operator):
    """Generate and setup a rigify rig for the active Genesis 2 Male figure"""
    bl_idname = "object.khalibloo_genesis2male_rigify_setup"
    bl_label = "Rigify"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'MESH'))
    
    def execute(self, context):
        genesis = bpy.context.active_object
        global rigifyRig
        global genesisRig
        
        if ((genesis.parent is not None) and (genesis.parent.type == 'ARMATURE')):
            if (len(genesis.data.vertices.items()) == 21556):
                genesisRig = bpy.context.active_object.parent

                genesisRig.hide = False
                bpy.context.scene.layers[findLayer(genesisRig)] = True
                

                #VERTEX GROUPS RAW DATA
                bpy.ops.object.mode_set(mode='EDIT')
                bm = bmesh.from_edit_mesh(bpy.data.meshes[genesis.data.name])
                
                head_tail = [2054, 2087]
                chest_head = [10459, 21116]
                spine_head = [2926, 13724]
                hips_head = [7872, 18552]
                toe_tail_L = [789]
                heel_tail_L = [4128, 4133]
                heel02_head_L = [9334]
                heel02_tail_L = [867, 8623]
                hand_tail_L = [1076, 2957, 3988, 4176, 9423, 9445, 9446]
                thumbtip_L = [964, 965]
                indextip_L = [3380, 3452]
                midtip_L = [3528, 3600]
                ringtip_L = [3676, 3748]
                pinkytip_L = [3824, 3896]
                indexcarp_L = [9404, 9409, 9692]
                midcarp_L = [1085, 9430, 9437]
                ringcarp_L = [1083, 9459, 9465]
                pinkycarp_L = [1008, 9484, 9515]
                #face rig
                eye_head_L = [2191, 2192, 2195, 2197, 8267, 8268, 8271, 8273, 8301, 8323, 8325, 8327, 8357, 8359, 8361, 8382]
                eye_head_R = [13023, 13024, 13027, 13029, 18938, 18939, 18942, 18944, 18972, 18994, 18996, 18998, 19028,
                              19030, 19032, 19053]
                eye_tail_L = [8313]
                eye_tail_R = [18984]
                tonguetip_tail = [4863]
                
                createVgroup(genesis, bm, "metarig_head_tail", head_tail)
                createVgroup(genesis, bm, "metarig_chest_head", chest_head)
                createVgroup(genesis, bm, "metarig_spine_head", spine_head)
                createVgroup(genesis, bm, "metarig_hips_head", hips_head)
                createVgroup(genesis, bm, "metarig_toe_tail.L", toe_tail_L)
                createVgroup(genesis, bm, "metarig_heel_tail.L", heel_tail_L)
                createVgroup(genesis, bm, "metarig_heel02_head.L", heel02_head_L)
                createVgroup(genesis, bm, "metarig_heel02_tail.L", heel02_tail_L)
                createVgroup(genesis, bm, "metarig_hand_tail.L", hand_tail_L)
                createVgroup(genesis, bm, "metarig_thumbtip.L", thumbtip_L)
                createVgroup(genesis, bm, "metarig_indextip.L", indextip_L)
                createVgroup(genesis, bm, "metarig_midtip.L", midtip_L)
                createVgroup(genesis, bm, "metarig_ringtip.L", ringtip_L)
                createVgroup(genesis, bm, "metarig_pinkytip.L", pinkytip_L)
                createVgroup(genesis, bm, "metarig_indexcarp.L", indexcarp_L)
                createVgroup(genesis, bm, "metarig_midcarp.L", midcarp_L)
                createVgroup(genesis, bm, "metarig_ringcarp.L", ringcarp_L)
                createVgroup(genesis, bm, "metarig_pinkycarp.L", pinkycarp_L)
                #face rig
                createVgroup(genesis, bm, "metarig_eye_head.L", eye_head_L)
                createVgroup(genesis, bm, "metarig_eye_head.R", eye_head_R)
                createVgroup(genesis, bm, "metarig_eye_tail.L", eye_tail_L)
                createVgroup(genesis, bm, "metarig_eye_tail.R", eye_tail_R)
                createVgroup(genesis, bm, "metarig_tonguetip_tail", tonguetip_tail)
                
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.ops.object.armature_human_metarig_add()
                metarig = bpy.context.active_object
                
                metarigPrep(metarig)
                
                copyMeshPos(metarig, genesis, "head", "tail", "metarig_head_tail")
                copyMeshPos(metarig, genesis, "chest", "head", "metarig_chest_head")
                copyMeshPos(metarig, genesis, "spine", "head", "metarig_spine_head")
                copyMeshPos(metarig, genesis, "hips", "head", "metarig_hips_head")
                copyMeshPos(metarig, genesis, "toe.L", "tail", "metarig_toe_tail.L")
                copyMeshPos(metarig, genesis, "heel.L", "tail", "metarig_heel_tail.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "head", "metarig_heel02_head.L")
                copyMeshPos(metarig, genesis, "heel.02.L", "tail", "metarig_heel02_tail.L")
                copyMeshPos(metarig, genesis, "hand.L", "tail", "metarig_hand_tail.L")
                copyMeshPos(metarig, genesis, "thumb.03.L", "tail", "metarig_thumbtip.L")
                copyMeshPos(metarig, genesis, "f_index.03.L", "tail", "metarig_indextip.L")
                copyMeshPos(metarig, genesis, "f_middle.03.L", "tail", "metarig_midtip.L")
                copyMeshPos(metarig, genesis, "f_ring.03.L", "tail", "metarig_ringtip.L")
                copyMeshPos(metarig, genesis, "f_pinky.03.L", "tail", "metarig_pinkytip.L")
                copyMeshPos(metarig, genesis, "palm.01.L", "head", "metarig_indexcarp.L")
                copyMeshPos(metarig, genesis, "palm.02.L", "head", "metarig_midcarp.L")
                copyMeshPos(metarig, genesis, "palm.03.L", "head", "metarig_ringcarp.L")
                copyMeshPos(metarig, genesis, "palm.04.L", "head", "metarig_pinkycarp.L")
                
                copyBonePos(metarig, genesisRig, "neck", "head", "neck")
                copyBonePos(metarig, genesisRig, "neck", "tail", "neck")
                copyBonePos(metarig, genesisRig, "thigh.L", "head", "lThigh")
                copyBonePos(metarig, genesisRig, "shin.L", "head", "lShin")
                copyBonePos(metarig, genesisRig, "shin.L", "tail", "lShin")
                #copyBonePos(metarig, genesisRig, "foot.L", "head", "lFoot")
                copyBonePos(metarig, genesisRig, "toe.L", "head", "lToe")
                copyBonePos(metarig, genesisRig, "shoulder.L", "head", "lCollar")
                copyBonePos(metarig, genesisRig, "shoulder.L", "tail", "lCollar")
                copyBonePos(metarig, genesisRig, "upper_arm.L", "head", "lShldr")
                copyBonePos(metarig, genesisRig, "forearm.L", "head", "lForeArm")
                copyBonePos(metarig, genesisRig, "forearm.L", "tail", "lForeArm")
                copyBonePos(metarig, genesisRig, "thumb.01.L", "head", "lThumb1")
                copyBonePos(metarig, genesisRig, "thumb.02.L", "head", "lThumb2")
                copyBonePos(metarig, genesisRig, "thumb.03.L", "head", "lThumb3")
                copyBonePos(metarig, genesisRig, "f_index.01.L", "head", "lIndex1")
                copyBonePos(metarig, genesisRig, "f_index.02.L", "head", "lIndex2")
                copyBonePos(metarig, genesisRig, "f_index.03.L", "head", "lIndex3")
                copyBonePos(metarig, genesisRig, "f_middle.01.L", "head", "lMid1")
                copyBonePos(metarig, genesisRig, "f_middle.02.L", "head", "lMid2")
                copyBonePos(metarig, genesisRig, "f_middle.03.L", "head", "lMid3")
                copyBonePos(metarig, genesisRig, "f_ring.01.L", "head", "lRing1")
                copyBonePos(metarig, genesisRig, "f_ring.02.L", "head", "lRing2")
                copyBonePos(metarig, genesisRig, "f_ring.03.L", "head", "lRing3")
                copyBonePos(metarig, genesisRig, "f_pinky.01.L", "head", "lPinky1")
                copyBonePos(metarig, genesisRig, "f_pinky.02.L", "head", "lPinky2")
                copyBonePos(metarig, genesisRig, "f_pinky.03.L", "head", "lPinky3")
                metarigFinishingTouches(metarig)
                setRolls(metarig)
                
                delVgroup(genesis, "metarig_head_tail")
                delVgroup(genesis, "metarig_chest_head")
                delVgroup(genesis, "metarig_spine_head")
                delVgroup(genesis, "metarig_hips_head")
                delVgroup(genesis, "metarig_toe_tail.L")
                delVgroup(genesis, "metarig_heel_tail.L")
                delVgroup(genesis, "metarig_heel02_head.L")
                delVgroup(genesis, "metarig_heel02_tail.L")
                delVgroup(genesis, "metarig_hand_tail.L")
                delVgroup(genesis, "metarig_thumbtip.L")
                delVgroup(genesis, "metarig_indextip.L")
                delVgroup(genesis, "metarig_midtip.L")
                delVgroup(genesis, "metarig_ringtip.L")
                delVgroup(genesis, "metarig_pinkytip.L")
                delVgroup(genesis, "metarig_indexcarp.L")
                delVgroup(genesis, "metarig_midcarp.L")
                delVgroup(genesis, "metarig_ringcarp.L")
                delVgroup(genesis, "metarig_pinkycarp.L")

                #face rig
                faceRig = createFaceRig()
                print(faceRig.name)
                faceRigSetParents(faceRig)
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "DEF-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "DEF-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "head", "metarig_eye_head.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "head", "metarig_eye_head.R")
                copyMeshPos(faceRig, genesis, "IK-eye.L", "tail", "metarig_eye_tail.L")
                copyMeshPos(faceRig, genesis, "IK-eye.R", "tail", "metarig_eye_tail.R")
                copyMeshPos(faceRig, genesis, "DEF-tonguetip", "tail", "metarig_tonguetip_tail")

                copyBonePos(faceRig, genesisRig, "DEF-tonguebase", "head", "tongueBase")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.01", "head", "tongue01")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.02", "head", "tongue02")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.03", "head", "tongue03")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.04", "head", "tongue04")
                copyBonePos(faceRig, genesisRig, "DEF-tongue.05", "head", "tongue05")
                copyBonePos(faceRig, genesisRig, "DEF-tonguetip", "head", "tongueTip")
                faceRigFinishingTouches(faceRig)

                delVgroup(genesis, "metarig_eye_head.L")
                delVgroup(genesis, "metarig_eye_head.R")
                delVgroup(genesis, "metarig_eye_tail.L")
                delVgroup(genesis, "metarig_eye_tail.R")
                delVgroup(genesis, "metarig_tonguetip_tail")
                
                bpy.ops.view3d.snap_cursor_to_center()
                
                bpy.ops.view3d.snap_cursor_to_center()
                bpy.context.scene.objects.active = metarig
                bpy.ops.pose.rigify_generate()
                rigifyRig = bpy.context.active_object
                rigifyRig.name = genesis.name + "-rig"
                #fix neck issue
                bpy.ops.object.khalibloo_rigify_neck_fix()
                parentWGTs()
                
                joinFaceRig(faceRig, rigifyRig)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.scene.objects.active = genesis
                genesis.select = True
        return {'FINISHED'}

class GenesisRigifyVgroups(bpy.types.Operator):
    """Mixes and renames the deformation vertex groups of a Genesis figure and/or selected Genesis item(s) to conform with Rigify. Backups are made before mixing, so no vertex groups are lost."""
    bl_idname = "object.khalibloo_genesis_rigify_vgroups"
    bl_label = "Rigify Vertex Groups"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'MESH'))

    def execute(self, context):
        selectionList = bpy.context.selected_objects
        objBackup = bpy.context.active_object
        global rigifyRig
        
        
        for obj in selectionList:
            bpy.context.scene.objects.active = bpy.data.objects[obj.name]
            if (len(obj.vertex_groups.keys())>0):
                mixVgroups(obj, "lToe", "lBigToe")
                mixVgroups(obj, "lToe", "lSmallToe1")
                mixVgroups(obj, "lToe", "lSmallToe2")
                mixVgroups(obj, "lToe", "lSmallToe3")
                mixVgroups(obj, "lToe", "lSmallToe4")
                mixVgroups(obj, "rToe", "rBigToe")
                mixVgroups(obj, "rToe", "rSmallToe1")
                mixVgroups(obj, "rToe", "rSmallToe2")
                mixVgroups(obj, "rToe", "rSmallToe3")
                mixVgroups(obj, "rToe", "rSmallToe4")
                mixVgroups(obj, "chest", "lPectoral")
                mixVgroups(obj, "chest", "rPectoral")
                #mixVgroups(obj, "head", "tongueBase")
                #mixVgroups(obj, "head", "tongue01")
                #mixVgroups(obj, "head", "tongue02")
                #mixVgroups(obj, "head", "tongue03")
                #mixVgroups(obj, "head", "tongue04")
                #mixVgroups(obj, "head", "tongue05")
                #mixVgroups(obj, "head", "tongueTip")
                mixVgroups(obj, "head", "lowerJaw")
                mixVgroups(obj, "head", "upperJaw")
                #mixVgroups(obj, "head", "lEye")
                #mixVgroups(obj, "head", "rEye")
                
                renameVgroups(obj, "head", "DEF-head")
                renameVgroups(obj, "neck", "DEF-neck")
                renameVgroups(obj, "chest", "DEF-chest")
                renameVgroups(obj, "abdomen2", "DEF-spine")
                renameVgroups(obj, "pelvis", "DEF-hips")
                renameVgroups(obj, "tongueBase", "DEF-tonguebase")
                renameVgroups(obj, "tongue01", "DEF-tongue.01")
                renameVgroups(obj, "tongue02", "DEF-tongue.02")
                renameVgroups(obj, "tongue03", "DEF-tongue.03")
                renameVgroups(obj, "tongue04", "DEF-tongue.04")
                renameVgroups(obj, "tongue05", "DEF-tongue.05")
                renameVgroups(obj, "tongueTip", "DEF-tonguetip")
                
                #LEFT
                renameVgroups(obj, "lEye", "DEF-eye.L")
                renameVgroups(obj, "lThigh", "DEF-thigh.01.L")
                renameVgroups(obj, "lShin", "DEF-shin.01.L")
                renameVgroups(obj, "lFoot", "DEF-foot.L")
                renameVgroups(obj, "lToe", "DEF-toe.L")
                renameVgroups(obj, "lCollar", "DEF-shoulder.L")
                renameVgroups(obj, "lShldr", "DEF-upper_arm.01.L")
                renameVgroups(obj, "lForeArm", "DEF-forearm.01.L")
                renameVgroups(obj, "lHand", "DEF-hand.L")
                renameVgroups(obj, "lCarpal2", "DEF-palm.04.L")
                renameVgroups(obj, "lCarpal1", "DEF-palm.01.L")
                renameVgroups(obj, "lThumb1", "DEF-thumb.01.L.02")
                renameVgroups(obj, "lThumb2", "DEF-thumb.02.L")
                renameVgroups(obj, "lThumb3", "DEF-thumb.03.L")
                renameVgroups(obj, "lIndex1", "DEF-f_index.01.L.01")
                renameVgroups(obj, "lIndex2", "DEF-f_index.02.L")
                renameVgroups(obj, "lIndex3", "DEF-f_index.03.L")
                renameVgroups(obj, "lMid1", "DEF-f_middle.01.L.01")
                renameVgroups(obj, "lMid2", "DEF-f_middle.02.L")
                renameVgroups(obj, "lMid3", "DEF-f_middle.03.L")
                renameVgroups(obj, "lRing1", "DEF-f_ring.01.L.01")
                renameVgroups(obj, "lRing2", "DEF-f_ring.02.L")
                renameVgroups(obj, "lRing3", "DEF-f_ring.03.L")
                renameVgroups(obj, "lPinky1", "DEF-f_pinky.01.L.01")
                renameVgroups(obj, "lPinky2", "DEF-f_pinky.02.L")
                renameVgroups(obj, "lPinky3", "DEF-f_pinky.03.L")
                
                #RIGHT
                renameVgroups(obj, "rEye", "DEF-eye.R")
                renameVgroups(obj, "rThigh", "DEF-thigh.01.R")
                renameVgroups(obj, "rShin", "DEF-shin.01.R")
                renameVgroups(obj, "rFoot", "DEF-foot.R")
                renameVgroups(obj, "rToe", "DEF-toe.R")
                renameVgroups(obj, "rCollar", "DEF-shoulder.R")
                renameVgroups(obj, "rShldr", "DEF-upper_arm.01.R")
                renameVgroups(obj, "rForeArm", "DEF-forearm.01.R")
                renameVgroups(obj, "rHand", "DEF-hand.R")
                renameVgroups(obj, "rCarpal2", "DEF-palm.04.R")
                renameVgroups(obj, "rCarpal1", "DEF-palm.01.R")
                renameVgroups(obj, "rThumb1", "DEF-thumb.01.R.02")
                renameVgroups(obj, "rThumb2", "DEF-thumb.02.R")
                renameVgroups(obj, "rThumb3", "DEF-thumb.03.R")
                renameVgroups(obj, "rIndex1", "DEF-f_index.01.R.01")
                renameVgroups(obj, "rIndex2", "DEF-f_index.02.R")
                renameVgroups(obj, "rIndex3", "DEF-f_index.03.R")
                renameVgroups(obj, "rMid1", "DEF-f_middle.01.R.01")
                renameVgroups(obj, "rMid2", "DEF-f_middle.02.R")
                renameVgroups(obj, "rMid3", "DEF-f_middle.03.R")
                renameVgroups(obj, "rRing1", "DEF-f_ring.01.R.01")
                renameVgroups(obj, "rRing2", "DEF-f_ring.02.R")
                renameVgroups(obj, "rRing3", "DEF-f_ring.03.R")
                renameVgroups(obj, "rPinky1", "DEF-f_pinky.01.R.01")
                renameVgroups(obj, "rPinky2", "DEF-f_pinky.02.R")
                renameVgroups(obj, "rPinky3", "DEF-f_pinky.03.R")

                #apply parent's transforms
                obj.parent.hide = False
                bpy.context.scene.layers[findLayer(obj.parent)] = True
                bpy.context.scene.objects.active = obj.parent
                obj.parent.select = True
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                if (rigifyRig is not None):
                    obj.parent = rigifyRig
                    setupArmatureModifier(obj, rigifyRig)
        
        bpy.ops.object.select_all(action='DESELECT')
        objBackup.select = True
        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class GenesisUnrigifyVgroups(bpy.types.Operator):
    """Renames the vertex groups of a rigified Genesis figure and/or selected Genesis item(s) to their original names"""
    bl_idname = "object.khalibloo_genesis_unrigify_vgroups"
    bl_label = "Unrigify Vertex Groups"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'MESH'))

    def execute(self, context):
        selectionList = bpy.context.selected_objects
        objBackup = bpy.context.active_object
        global genesisRig
        
        
        for obj in selectionList:
            bpy.context.scene.objects.active = bpy.data.objects[obj.name]
            if (len(obj.vertex_groups.keys())>0):
                
                renameVgroups(obj, "DEF-head", "head")
                renameVgroups(obj, "DEF-neck", "neck")
                renameVgroups(obj, "DEF-chest", "chest")
                renameVgroups(obj, "DEF-spine", "abdomen2")
                renameVgroups(obj, "DEF-hips", "pelvis")
                renameVgroups(obj, "DEF-tonguebase", "tongueBase")
                renameVgroups(obj, "DEF-tongue.01", "tongue01")
                renameVgroups(obj, "DEF-tongue.02", "tongue02")
                renameVgroups(obj, "DEF-tongue.03", "tongue03")
                renameVgroups(obj, "DEF-tongue.04", "tongue04")
                renameVgroups(obj, "DEF-tongue.05", "tongue05")
                renameVgroups(obj, "DEF-tonguetip", "tongueTip")
                #LEFT
                renameVgroups(obj, "DEF-eye.L", "lEye")
                renameVgroups(obj, "DEF-thigh.01.L", "lThigh")
                renameVgroups(obj, "DEF-shin.01.L", "lShin")
                renameVgroups(obj, "DEF-foot.L", "lFoot")
                renameVgroups(obj, "DEF-toe.L", "lToe")
                renameVgroups(obj, "DEF-shoulder.L", "lCollar")
                renameVgroups(obj, "DEF-upper_arm.01.L", "lShldr")
                renameVgroups(obj, "DEF-forearm.01.L", "lForeArm")
                renameVgroups(obj, "DEF-hand.L", "lHand")
                renameVgroups(obj, "DEF-palm.04.L", "lCarpal2")
                renameVgroups(obj, "DEF-palm.01.L", "lCarpal1")
                renameVgroups(obj, "DEF-thumb.01.L.02", "lThumb1")
                renameVgroups(obj, "DEF-thumb.02.L", "lThumb2")
                renameVgroups(obj, "DEF-thumb.03.L", "lThumb3")
                renameVgroups(obj, "DEF-f_index.01.L.01", "lIndex1")
                renameVgroups(obj, "DEF-f_index.02.L", "lIndex2")
                renameVgroups(obj, "DEF-f_index.03.L", "lIndex3")
                renameVgroups(obj, "DEF-f_middle.01.L.01", "lMid1")
                renameVgroups(obj, "DEF-f_middle.02.L", "lMid2")
                renameVgroups(obj, "DEF-f_middle.03.L", "lMid3")
                renameVgroups(obj, "DEF-f_ring.01.L.01", "lRing1")
                renameVgroups(obj, "DEF-f_ring.02.L", "lRing2")
                renameVgroups(obj, "DEF-f_ring.03.L", "lRing3")
                renameVgroups(obj, "DEF-f_pinky.01.L.01", "lPinky1")
                renameVgroups(obj, "DEF-f_pinky.02.L", "lPinky2")
                renameVgroups(obj, "DEF-f_pinky.03.L", "lPinky3")
                
                #RIGHT
                renameVgroups(obj, "DEF-eye.R", "rEye")
                renameVgroups(obj, "DEF-thigh.01.R", "rThigh")
                renameVgroups(obj, "DEF-shin.01.R", "rShin")
                renameVgroups(obj, "DEF-foot.R", "rFoot")
                renameVgroups(obj, "DEF-toe.R", "rToe")
                renameVgroups(obj, "DEF-shoulder.R", "rCollar")
                renameVgroups(obj, "DEF-upper_arm.01.R", "rShldr")
                renameVgroups(obj, "DEF-forearm.01.R", "rForeArm")
                renameVgroups(obj, "DEF-hand.R", "rHand")
                renameVgroups(obj, "DEF-palm.04.R", "rCarpal2")
                renameVgroups(obj, "DEF-palm.01.R", "rCarpal1")
                renameVgroups(obj, "DEF-thumb.01.R.02", "rThumb1")
                renameVgroups(obj, "DEF-thumb.02.R", "rThumb2")
                renameVgroups(obj, "DEF-thumb.03.R", "rThumb3")
                renameVgroups(obj, "DEF-f_index.01.R.01", "rIndex1")
                renameVgroups(obj, "DEF-f_index.02.R", "rIndex2")
                renameVgroups(obj, "DEF-f_index.03.R", "rIndex3")
                renameVgroups(obj, "DEF-f_middle.01.R.01", "rMid1")
                renameVgroups(obj, "DEF-f_middle.02.R", "rMid2")
                renameVgroups(obj, "DEF-f_middle.03.R", "rMid3")
                renameVgroups(obj, "DEF-f_ring.01.R.01", "rRing1")
                renameVgroups(obj, "DEF-f_ring.02.R", "rRing2")
                renameVgroups(obj, "DEF-f_ring.03.R", "rRing3")
                renameVgroups(obj, "DEF-f_pinky.01.R.01", "rPinky1")
                renameVgroups(obj, "DEF-f_pinky.02.R", "rPinky2")
                renameVgroups(obj, "DEF-f_pinky.03.R", "rPinky3")

                #apply parent's transforms
                bpy.context.scene.objects.active = obj.parent
                obj.parent.select = True
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                if (genesisRig is not None):
                    obj.parent = genesisRig
                    setupArmatureModifier(obj, genesisRig)
        
        
        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ReceiveTransparentShadows(bpy.types.Operator):
    """Sets all materials of the selected object(s) to receive transparent shadows"""
    bl_idname = "object.khalibloo_receive_transparent_shadows"
    bl_label = "Receive Transparent"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            if (len(obj.material_slots.keys()) > 0):
                for matSlot in obj.material_slots:
                    matSlot.material.use_transparent_shadows = True
        return {'FINISHED'}

class GenesisMaterialSetup(bpy.types.Operator):
    """Fixes the necessary settings on each of the materials and textures of the active Genesis figure.
    Note:for this to work, the materials must be using their default names."""
    bl_idname = "object.khalibloo_genesis_material_setup"
    bl_label = "Setup Materials"


    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (len(context.active_object.material_slots.keys()) != 0) and (bpy.context.scene.render.engine == 'BLENDER_RENDER'))

    def execute(self, context):
        obj = bpy.context.active_object
        originalMatList = obj.material_slots.keys()
        affect_textures = bpy.context.scene.khalibloo_affect_textures
        merge_mats = bpy.context.scene.khalibloo_merge_mats


        if (merge_mats):
            mergeMats(obj, originalMatList)
        
        
        #daz_3_SkinFoot
        guessName = "daz_3_SkinFoot"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Feet"
            check = checkForMatName(obj, guessName)
            if (check is None):
                guessName = "Limbs"
                check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Feet"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_6_Eyelash
        guessName = "daz_6_Eyelash"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Eyelashes"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Eyelashes"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            if (mat.texture_slots[0] is not None):
                mat.texture_slots[0].use_rgb_to_intensity = True
            check = None

        
        #daz_5_Sclera
        guessName = "daz_5_Sclera"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Sclera"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Sclera"
            if (merge_mats):
                name = "Irises"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            check = None

        
        #daz_5_Pupil
        guessName = "daz_5_Pupil"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Pupils"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Pupils"
            if (merge_mats):
                name = "Irises"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            check = None
        

        #daz_5_Iris
        guessName = "daz_5_Iris"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Irises"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            #print(mat.name)
            name = "Irises"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupBumpTex(mat, name)
            check = None

        #daz_5_Cornea if it's a Genesis 2 figure
        guessName = "Cornea"
        check = checkForMatName(obj, guessName)
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Cornea"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_shader = 'WARDISO'
            mat.specular_intensity = 1
            mat.specular_slope = 0.05
            mat.use_transparency = True
            mat.alpha = 0
            mat.specular_alpha = 0
            check = None

        if (len(obj.data.vertices.items()) == 19296):
            #daz_5_Cornea ONLY if it's a Genesis figure
            guessName = "daz_5_Cornea"
            check = checkForMatName(obj, guessName)
            if (check is None):
                guessName = "Cornea"
                check = checkForMatName(obj, guessName)
                
            if (check is not None):
                mat = obj.material_slots[check].material
                name = "Cornea"
                mat.name = name
                mat.diffuse_intensity = 1
                mat.use_transparent_shadows = True
                mat.specular_shader = 'WARDISO'
                mat.specular_intensity = 1
                mat.specular_slope = 0.05
                mat.use_transparency = True
                mat.alpha = 0
                check = None


        #EyeReflection
        guessName = "EyeReflection"
        check = checkForMatName(obj, guessName)
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "EyeReflection"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_shader = 'WARDISO'
            mat.specular_intensity = 1
            mat.specular_slope = 0.05
            mat.use_transparency = True
            mat.alpha = 0
            check = None
        

        #daz_4_Tongue
        guessName = "daz_4_Tongue"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Tongue"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Tongue"
            if (merge_mats):
                name = "InnerMouth"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 1
            mat.specular_hardness = 500
            if affect_textures:
                setupBumpTex(mat, name)
            check = None
        

        #daz_4_Teeth
        guessName = "daz_4_Teeth"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Teeth"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Teeth"
            if (merge_mats):
                name = "InnerMouth"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 1
            mat.specular_hardness = 500
            if affect_textures:
                setupBumpTex(mat, name)
            check = None
        

        #daz_4_InnerMouth
        guessName = "daz_4_InnerMouth"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "InnerMouth"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "InnerMouth"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 1
            mat.specular_hardness = 500
            if affect_textures:
                setupBumpTex(mat, name)
            check = None
        

        #daz_4_Gums
        guessName = "daz_4_Gums"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Gums"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Gums"
            if (merge_mats):
                name = "InnerMouth"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 1
            mat.specular_hardness = 500
            if affect_textures:
                setupBumpTex(mat, name)
            check = None
        

        #daz_3_SkinArm
        guessName = "daz_3_SkinArm"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Shoulders"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Shoulders"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_2_SkinTorso
        guessName = "daz_2_SkinTorso"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Torso"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_2_Nipple
        guessName = "daz_2_Nipple"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Nipples"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Nipples"
            if (merge_mats):
                name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_2_SkinNeck
        guessName = "daz_2_SkinNeck"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Neck"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Neck"
            if (merge_mats):
                name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_3_SkinForearm
        guessName = "daz_3_SkinForearm"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Forearms"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Forearms"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_3_SkinLeg
        guessName = "daz_3_SkinLeg"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Legs"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Legs"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_2_SkinHip
        guessName = "daz_2_SkinHip"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Hips"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Hips"
            if (merge_mats):
                name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_2_SkinHead
        guessName = "daz_2_SkinHead"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Head"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Head"
            if (merge_mats):
                name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_3_SkinHand
        guessName = "daz_3_SkinHand"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Hands"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Hands"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_7_Tear
        guessName = "daz_7_Tear"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Tears"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Tears"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_shader = 'WARDISO'
            mat.specular_intensity = 1
            mat.specular_slope = 0.05
            mat.use_transparency = True
            mat.alpha = 0
            check = None
        

        #daz_1_Nostril
        guessName = "daz_1_Nostril"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Nostrils"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Nostrils"
            if (merge_mats):
                name = "Face"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_1_Lip
        guessName = "daz_1_Lip"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Lips"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Lips"
            if (merge_mats):
                name = "Face"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0.6
            mat.specular_hardness = 400
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_5_Lacrimal
        guessName = "daz_5_Lacrimal"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Lacrimals"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Lacrimals"
            if (merge_mats):
                name = "Irises"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            check = None
        

        #daz_1_SkinFace
        guessName = "daz_1_SkinFace"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Face"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Face"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None


        #Ears
        guessName = "Ears"
        check = checkForMatName(obj, guessName)
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Ears"
            if (merge_mats):
                name = "Torso"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        

        #daz_3_Fingernail
        guessName = "daz_3_Fingernail"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Fingernails"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Fingernails"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None

        

        #daz_3_Toenail
        guessName = "daz_3_Toenail"
        check = checkForMatName(obj, guessName)
        if (check is None):
            guessName = "Toenails"
            check = checkForMatName(obj, guessName)
            
        if (check is not None):
            mat = obj.material_slots[check].material
            name = "Toenails"
            if (merge_mats):
                name = "Limbs"
            mat.name = name
            mat.diffuse_intensity = 1
            mat.use_transparent_shadows = True
            mat.specular_intensity = 0
            if affect_textures:
                setupSpecTex(mat, name)
                setupBumpTex(mat, name)
            check = None
        
        return {'FINISHED'}

class RigifyNeckFix(bpy.types.Operator):
    """Fixes a rare condition where the rigify rig's neck bone is a lot larger than it should be"""
    bl_idname = "object.khalibloo_rigify_neck_fix"
    bl_label = "Rigify Neck Fix"

    @classmethod
    def poll(cls, context):
        return ((context.active_object is not None) and (context.active_object.type == 'ARMATURE'))



    def execute(self, context):
        rig = bpy.context.active_object
        neck = rig.pose.bones["neck"].custom_shape
        bpy.context.scene.layers[findLayer(neck)] = True
        neck.hide = False
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = neck
        neck.select = True
        bpy.context.space_data.pivot_point = 'MEDIAN_POINT'
        bpy.context.object.scale[0] = 0.390
        bpy.context.object.scale[1] = 0.390
        bpy.context.object.scale[2] = 0.390
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.context.space_data.pivot_point = 'CURSOR'
        bpy.ops.transform.resize(value=(0.2442, 0.2442, 0.2442), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = rig

        return{'FINISHED'}

class ModifiersRealTimeOn(bpy.types.Operator):
    """Turn on real time display of modifiers of the selected objects"""
    bl_idname = "object.khalibloo_modifiers_realtime_on"
    bl_label = "Real Time Display On"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersRealTimeOn(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersRealTimeOff(bpy.types.Operator):
    """Turn off real time display of modifiers of the selected objects"""
    bl_idname = "object.khalibloo_modifiers_realtime_off"
    bl_label = "Real Time Display Off"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersRealTimeOff(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersRenderOn(bpy.types.Operator):
    """Turn on modifiers of the selected objects during rendering"""
    bl_idname = "object.khalibloo_modifiers_render_on"
    bl_label = "Render Display On"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersRenderOn(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersRenderOff(bpy.types.Operator):
    """Turn off modifiers of the selected objects during rendering"""
    bl_idname = "object.khalibloo_modifiers_render_off"
    bl_label = "Render Display Off"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersRenderOff(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersEditModeOn(bpy.types.Operator):
    """Turn on edit mode display of modifiers of the selected objects"""
    bl_idname = "object.khalibloo_modifiers_editmode_on"
    bl_label = "Edit Mode Display On"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersEditModeOn(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersEditModeOff(bpy.types.Operator):
    """Turn off edit mode display of modifiers of the selected objects"""
    bl_idname = "object.khalibloo_modifiers_editmode_off"
    bl_label = "Edit Mode Display Off"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersEditModeOff(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersApply(bpy.types.Operator):
    """Apply all modifiers of the selected objects in order"""
    bl_idname = "object.khalibloo_modifiers_apply"
    bl_label = "Apply"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersApply(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ModifiersRemove(bpy.types.Operator):
    """Delete all modifiers of the selected objects"""
    bl_idname = "object.khalibloo_modifiers_remove"
    bl_label = "Delete"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes

        for obj in bpy.context.selected_objects:
            modifiersRemove(obj, mod_filter_mode, mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ConstraintsMute(bpy.types.Operator):
    """Mute all constraints of the selected objects"""
    bl_idname = "object.khalibloo_constraints_mute"
    bl_label = "Mute Constraints"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            muteConstraints(obj)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ConstraintsUnmute(bpy.types.Operator):
    """Unmute all constraints of the selected objects"""
    bl_idname = "object.khalibloo_constraints_unmute"
    bl_label = "Unmute Constraints"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            unmuteConstraints(obj)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ConstraintsRemove(bpy.types.Operator):
    """Delete all constraints of the selected objects"""
    bl_idname = "object.khalibloo_constraints_remove"
    bl_label = "Delete Constraints"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            removeConstraints(obj)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class BoneConstraintsMute(bpy.types.Operator):
    """Mute all constraints of the selected bones"""
    bl_idname = "object.khalibloo_bone_constraints_mute"
    bl_label = "Mute Bone Constraints"

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'POSE') and (len(context.selected_pose_bones) > 0))
        #the 2nd parameter would spit an error if we are not in pose mode
        #so, it's importaant to check for pose mode before counting selected pose bones


    def execute(self, context):
        for bone in bpy.context.selected_pose_bones:
            muteConstraints(bone)
        return {'FINISHED'}
    
class BoneConstraintsUnmute(bpy.types.Operator):
    """Unmute all constraints of the selected bones"""
    bl_idname = "object.khalibloo_bone_constraints_unmute"
    bl_label = "Unmute Bone Constraints"

    @classmethod
    def poll(cls, context):
       return ((context.mode == 'POSE') and (len(context.selected_pose_bones) > 0))
        #the 2nd parameter would spit an error if we are not in pose mode
        #so, it's importaant to check for pose mode before counting selected pose bones


    def execute(self, context):
        for bone in bpy.context.selected_pose_bones:
            unmuteConstraints(bone)
        return {'FINISHED'}
    
class BoneConstraintsRemove(bpy.types.Operator):
    """Delete all constraints of the selected bones"""
    bl_idname = "object.khalibloo_bone_constraints_remove"
    bl_label = "Delete Bone Constraints"

    @classmethod
    def poll(cls, context):
        return ((context.mode == 'POSE') and (len(context.selected_pose_bones) > 0))
        #the 2nd parameter would spit an error if we are not in pose mode
        #so, it's importaant to check for pose mode before counting selected pose bones


    def execute(self, context):
        for bone in bpy.context.selected_pose_bones:
            removeConstraints(bone)
        return {'FINISHED'}

class TexturesOff(bpy.types.Operator):
    """Disable all textures of all materials of the selected objects"""
    bl_idname = "object.khalibloo_textures_off"
    bl_label = "Disable Textures"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        #objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            texturesOff(obj)

        #bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class TexturesOn(bpy.types.Operator):
    """Enable all textures of all materials of the selected objects"""
    bl_idname = "object.khalibloo_textures_on"
    bl_label = "Disable Textures"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        #objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            texturesOn(obj)

        #bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class MaterialsRemove(bpy.types.Operator):
    """Remove all materials from the selected objects"""
    bl_idname = "object.khalibloo_materials_remove"
    bl_label = "Remove Materials"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        objBackup = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            materialsRemove(obj)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class LocationApply(bpy.types.Operator):
    """Apply location transforms of the selected objects"""
    bl_idname = "object.khalibloo_apply_location"
    bl_label = "Apply Location"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class RotationApply(bpy.types.Operator):
    """Apply rotation transforms of the selected objects"""
    bl_idname = "object.khalibloo_apply_rotation"
    bl_label = "Apply Rotation"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class ScaleApply(bpy.types.Operator):
    """Apply scale transforms of the selected objects"""
    bl_idname = "object.khalibloo_apply_scale"
    bl_label = "Apply Scale"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object

        bpy.ops.object.mode_set(mode='OBJECT')
        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}

class HideSelect(bpy.types.Operator):
    """Make selected objects unselectable"""
    bl_idname = "object.khalibloo_hide_select"
    bl_label = "Hide Select"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        hideSelect()
        return {'FINISHED'}

class UnhideSelect(bpy.types.Operator):
    """Make all objects selectable"""
    bl_idname = "object.khalibloo_unhide_select"
    bl_label = "Unhide Select"

    @classmethod
    def poll(cls, context):
        return (len(context.scene.objects) > 0)


    def execute(self, context):
        unhideSelect()
        return {'FINISHED'}

class HideRender(bpy.types.Operator):
    """Make selected objects invisible in renders"""
    bl_idname = "object.khalibloo_hide_render"
    bl_label = "Hide Render"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        hideRender()
        return {'FINISHED'}

class UnhideRender(bpy.types.Operator):
    """Make selected objects visible in renders"""
    bl_idname = "object.khalibloo_unhide_render"
    bl_label = "Unhide Render"

    @classmethod
    def poll(cls, context):
        return (len(context.selected_objects) > 0)


    def execute(self, context):
        unhideRender()
        return {'FINISHED'}

class ModifierAdd(bpy.types.Operator):
    """Add the modifier specified above to the selected objects"""
    bl_idname = "object.khalibloo_add_modifier"
    bl_label = "Add Modifier"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None))


    def execute(self, context):
        objBackup = bpy.context.active_object
        mod_type = bpy.context.scene.khalibloo_enumModifierTypes
        nonMeshModList = ['MESH_CACHE', 'ARRAY', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 'MIRROR',
                           'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF', 'TRIANGULATE',
                           'ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'MESH_DEFORM',
                           'SHRINKWRAP', 'SIMPLE_DEFORM', 'SMOOTH', 'WARP', 'WAVE',
                           'SOFT_BODY']

        for obj in bpy.context.selected_objects:
            if (obj.type == 'MESH'):
                bpy.context.scene.objects.active = obj
                bpy.ops.object.modifier_add(type=mod_type)
                
            #if it's not a mesh, but is still a modifiable object
            elif (isModifierType(obj)):
                if (mod_type in nonMeshModList):
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.modifier_add(type=mod_type)

        bpy.context.scene.objects.active = objBackup
        return {'FINISHED'}


class GenesisImportMorphs(bpy.types.Operator):
    """Imports all Genesis morphs(.dsf) in the path specified as shape keys of the active Genesis figure"""
    bl_idname = "object.khalibloo_import_genesis_morphs"
    bl_label = "Import Morphs"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None) and (context.active_object.type == 'MESH'))


    def execute(self, context):
        import os
        obj = bpy.context.active_object
        morph_dir = bpy.context.scene.khalibloo_genesis_morph_dir

        for filename in os.listdir(morph_dir):
            filepath = morph_dir + filename
            name, extension = os.path.splitext(filepath)
            if (extension == ".obj"):
                try:
                    bpy.ops.import_scene.obj(filepath=filepath, filter_glob="*.obj;*.mtl",
                                use_ngons=True, use_edges=True, use_smooth_groups=True,
                                use_split_objects=False, use_split_groups=False,
                                use_groups_as_vgroups=False, use_image_search=False,
                                split_mode='OFF', global_clamp_size=0,
                                axis_forward='-Y', axis_up='Z')
                except AttributeError:
                    self.report({'ERROR'}, "Missing Addon: 'Import-Export: Wavefront OBJ format'")
                except RuntimeError:
                    self.report({'WARNING'}, "Ensure that only the relevant OBJ files are in the folder!")
            bpy.ops.object.khalibloo_apply_rotation()
            bpy.ops.object.join_shapes()
            bpy.ops.object.delete()

        return {'FINISHED'}

class FlattenUVx(bpy.types.Operator):
    """Flatten selected UV elements on the X axis"""
    bl_idname = "uv.khalibloo_uv_flatten_x"
    bl_label = "Flatten X"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None) and (context.active_object.type == 'MESH'))


    def execute(self, context):
        bpy.ops.transform.resize(value = (0, 1, 1), constraint_axis = (True, False, False), 
                                 constraint_orientation = 'GLOBAL', proportional = 'DISABLED')
        return {'FINISHED'}

class FlattenUVy(bpy.types.Operator):
    """Flatten selected UV elements on the Y axis"""
    bl_idname = "uv.khalibloo_uv_flatten_y"
    bl_label = "Flatten Y"

    @classmethod
    def poll(cls, context):
        return ((len(context.selected_objects) > 0) and (context.active_object is not None) and (context.active_object.type == 'MESH'))


    def execute(self, context):
        bpy.ops.transform.resize(value = (1, 0, 1), constraint_axis = (False, True, False), 
                                 constraint_orientation = 'GLOBAL', proportional = 'DISABLED')
        return {'FINISHED'}

#============================================================================
# DRAW PANEL
#============================================================================

class KhaliblooPanel(bpy.types.Panel):
    """Creates a Panel in the properties context of the 3D viewport"""
    bl_label = "Khalibloo"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "scene"



    def draw(self, context):
        layout = self.layout
        scene = context.scene
        platform_type = bpy.context.scene.khalibloo_enumPlatformTypes
        genesis_type = bpy.context.scene.khalibloo_enumGenesisTypes
        genesis2_type = bpy.context.scene.khalibloo_enumGenesis2Types
        category_type = bpy.context.scene.khalibloo_enumCategoryTypes
        mod_filter_mode = bpy.context.scene.khalibloo_enumModifierFilterMode


        #Platforn type
        layout.prop(scene, "khalibloo_enumPlatformTypes", expand=False)
        
#---------------------------------------------------------------------------------
        #GENERAL TOOLS
        if (platform_type == 'GENERAL'):
            #Category type
            layout.prop(scene, "khalibloo_enumCategoryTypes", expand=True)
            layout.row()
            layout.row()


            #OBJECT DATA TAB
            if (category_type == 'OBJECT DATA'):
                layout.row()
                layout.label(text="Apply: ")
                row = layout.row(align=True)
                row.operator("object.khalibloo_apply_location", text="Location")
                row.operator("object.khalibloo_apply_rotation", text="Rotation")
                row.operator("object.khalibloo_apply_scale", text="Scale")
                
                layout.row()
                layout.row()
                row = layout.row(align=True)
                row.operator("object.khalibloo_unhide_select", text="", icon='RESTRICT_SELECT_OFF')
                row.operator("object.khalibloo_hide_select", text="", icon='RESTRICT_SELECT_ON')
                row.operator("object.khalibloo_unhide_render", text="", icon='RESTRICT_RENDER_OFF')
                row.operator("object.khalibloo_hide_render", text="", icon='RESTRICT_RENDER_ON')
                

            #MESH DATA TAB
            if (category_type == 'MESH DATA'):
                layout.row()
                layout.operator("object.khalibloo_copy_all_shape_keys")
                #layout.row()
                #layout.row()
                #layout.prop(scene, "khalibloo_spread_harden_vgroups")
                #layout.operator("object.khalibloo_harden_weights")

            #MATERIALS TAB
            elif (category_type == 'MATERIALS'):
                layout.row()
                layout.operator("object.khalibloo_receive_transparent_shadows")
                layout.operator("object.khalibloo_materials_remove", text='Remove Materials', icon='X')

                layout.row()
                row = layout.row(align=True)
                row.label(text="Textures:", icon='TEXTURE')
                row.operator("object.khalibloo_textures_on", text='', icon='RESTRICT_VIEW_OFF')
                row.operator("object.khalibloo_textures_off", text='', icon='RESTRICT_VIEW_ON')

            #MODIFIERS TAB
            elif (category_type == 'MODIFIERS'):
                layout.row()
                layout.prop(scene, "khalibloo_enumModifierTypes", expand=False)
                layout.operator("object.khalibloo_add_modifier", text='Add Modifier', icon='ZOOMIN')
                
                layout.row()
                layout.prop(scene, "khalibloo_enumModifierFilterMode", expand=True)
                
                row = layout.row(align=True)
                row.operator("object.khalibloo_modifiers_realtime_on", text='', icon='RESTRICT_VIEW_OFF')
                row.operator("object.khalibloo_modifiers_realtime_off", text='', icon='RESTRICT_VIEW_ON')
                row.operator("object.khalibloo_modifiers_render_on", text='', icon='RESTRICT_RENDER_OFF')
                row.operator("object.khalibloo_modifiers_render_off", text='', icon='RESTRICT_RENDER_ON')
                #row.operator("object.khalibloo_modifiers_editmode_on", text='', icon='EDITMODE_HLT')
                #row.operator("object.khalibloo_modifiers_editmode_off", text='', icon='VIEW3D')
                row.operator("object.khalibloo_modifiers_apply", text='Apply')
                row.operator("object.khalibloo_modifiers_remove", text='', icon='X')

            #ARMATURES TAB
            elif (category_type == 'ARMATURES'):
                layout.row()
                layout.operator("object.khalibloo_rigify_neck_fix")

            #CONSTRAINTS TAB
            elif (category_type == 'CONSTRAINTS'):
                layout.row()
                row = layout.row(align=True)
                row.operator("object.khalibloo_constraints_unmute", text='', icon='RESTRICT_VIEW_OFF')
                row.operator("object.khalibloo_constraints_mute", text='', icon='RESTRICT_VIEW_ON')
                row.operator("object.khalibloo_constraints_remove", text='', icon='X')
                
                layout.row()
                
                row = layout.row(align=True)
                row.label(text="Bone Constraints:", icon='CONSTRAINT_BONE')
                row = layout.row(align=True)
                row.operator("object.khalibloo_bone_constraints_unmute", text='', icon='RESTRICT_VIEW_OFF')
                row.operator("object.khalibloo_bone_constraints_mute", text='', icon='RESTRICT_VIEW_ON')
                row.operator("object.khalibloo_bone_constraints_remove", text='', icon='X')

            
#-----------------------------------------------------------------------------------
        #GENESIS TOOLS
        elif (platform_type == 'DAZ GENESIS'):
            
            #Genesis Object type
            layout.prop(scene, "khalibloo_enumGenesisTypes", expand=True)
            layout.row()
            layout.row()

            #if it's a Genesis figure
            if (genesis_type == 'FIGURE'):
                
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_setup")
                        
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_vgroups")

                layout.operator("object.khalibloo_genesis_unrigify_vgroups")


                layout.label(text="  ")
                # Morphs
                layout.prop(scene, "khalibloo_genesis_morph_dir")
                
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_import_genesis_morphs")
                

                layout.label(text="  ")
                # Check boxes
                layout.prop(scene, "khalibloo_affect_textures")
                
                layout.prop(scene, "khalibloo_merge_mats")

                     
                
                #row = layout.row()
                layout.operator("object.khalibloo_genesis_material_setup")

            #If it's a Genesis item
            elif (genesis_type == 'ITEM'):
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_vgroups")

                layout.operator("object.khalibloo_genesis_unrigify_vgroups")

#-----------------------------------------------------------------------------------
        #GENESIS 2 TOOLS
        elif (platform_type == 'DAZ GENESIS 2'):
            
            #Genesis Object type
            layout.prop(scene, "khalibloo_enumGenesis2Types", expand=True)
            layout.row()
            layout.row()

            #if it's a Genesis 2 Male
            if (genesis2_type == 'MALE'):
                
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis2male_rigify_setup")
                        
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_vgroups")

                layout.operator("object.khalibloo_genesis_unrigify_vgroups")


                layout.label(text="  ")
                # Morphs
                layout.prop(scene, "khalibloo_genesis_morph_dir")
                
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_import_genesis_morphs")
                

                layout.label(text="  ")
                # Check boxes
                layout.prop(scene, "khalibloo_affect_textures")
                
                layout.prop(scene, "khalibloo_merge_mats")

                     
                
                layout.operator("object.khalibloo_genesis_material_setup")


            #if it's a Genesis 2 Female
            if (genesis2_type == 'FEMALE'):
                
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis2female_rigify_setup")

                layout.operator("object.khalibloo_rigify_neck_fix")
                        
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_vgroups")

                layout.operator("object.khalibloo_genesis_unrigify_vgroups")


                layout.label(text="  ")
                # Morphs
                layout.prop(scene, "khalibloo_genesis_morph_dir")
                
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_import_genesis_morphs")
                

                layout.label(text="  ")
                # Check boxes
                layout.prop(scene, "khalibloo_affect_textures")
                
                layout.prop(scene, "khalibloo_merge_mats")

                # Materials
                layout.operator("object.khalibloo_genesis_material_setup")


            #If it's a Genesis Item
            elif (genesis2_type == 'ITEM'):
                # Big button
                row = layout.row()
                row.scale_y = 2.0
                row.operator("object.khalibloo_genesis_rigify_vgroups")

                layout.operator("object.khalibloo_genesis_unrigify_vgroups")

class KhaliblooPanelUV(bpy.types.Panel):
    """Creates a Panel in the tool shelf of the UV/Image editor"""
    bl_label = "Khalibloo Panel"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "scene"



    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row(align = True)
        row.operator("uv.khalibloo_uv_flatten_x", text="Flatten X")
        row.operator("uv.khalibloo_uv_flatten_y", text="Flatten Y")
        
        #layout.prop(scene, "khalibloo_enumBatchBakeImages", expand = False)
        #layout.template_ID(bpy.context.space_data, "image", new="image.new")
        
        #row = layout.row(align = True)
        #row.prop(scene, "khalibloo_BatchBakeStartFrame")
        #row.prop(scene, "khalibloo_BatchBakeEndFrame")

def initialize():
    bpy.types.Scene.khalibloo_enumGenesisTypes = bpy.props.EnumProperty(items =(
                                         ('FIGURE', 'Figure',''),
                                         ('ITEM', 'Item','')),
                                name = ' ', 
                                default = 'FIGURE')

    bpy.types.Scene.khalibloo_enumGenesis2Types = bpy.props.EnumProperty(items =(
                                         ('MALE', 'Male',''),
                                         ('FEMALE', 'Female',''),
                                         ('ITEM', 'Item', '')),
                                name = ' ', 
                                default = 'MALE')

    bpy.types.Scene.khalibloo_enumPlatformTypes = bpy.props.EnumProperty(items =(
                                         ('GENERAL', 'General', ''),
                                         ('DAZ GENESIS', 'DAZ Genesis', ''),
                                         ('DAZ GENESIS 2', 'DAZ Genesis 2', '')),
                                name = '',
                                description = 'Choose platform type',
                                default = 'GENERAL')

    bpy.types.Scene.khalibloo_enumCategoryTypes = bpy.props.EnumProperty(items =(
                                         ('OBJECT DATA', 'Object Data','', 'OBJECT_DATA', 0),
                                         ('MESH DATA', 'Mesh Data','', 'MESH_DATA', 1),
                                         ('MATERIALS', 'Materials', '', 'MATERIAL', 2),
                                         ('MODIFIERS', 'Modifiers', '', 'MODIFIER', 3),
                                         ('ARMATURES', 'Armatures', '', 'ARMATURE_DATA', 4),
                                         ('CONSTRAINTS', 'Constraints', '', 'CONSTRAINT', 5)),
                                name = '',
                                description = 'Type of tools to display',
                                default = 'OBJECT DATA')
    
    bpy.types.Scene.khalibloo_enumModifierTypes = bpy.props.EnumProperty(items =(
                                         #Modify
                                         ('MESH_CACHE', 'Mesh Cache', '', 'MOD_MESHDEFORM', 0),
                                         ('UV_PROJECT', 'UV Project', '', 'MOD_UVPROJECT', 1),
                                         ('UV_WARP', 'UV Warp', '', 'MOD_UVPROJECT', 2),
                                         ('VERTEX_WEIGHT_EDIT', 'Vertex Weight Edit', '', 'MOD_VERTEX_WEIGHT', 3),
                                         ('VERTEX_WEIGHT_MIX', 'Vertex Weight Mix', '', 'MOD_VERTEX_WEIGHT', 4),
                                         ('VERTEX_WEIGHT_PROXIMITY', 'Vertex Weight Proximity', '', 'MOD_VERTEX_WEIGHT', 5),
                                         #Generate
                                         ('ARRAY', 'Array', '', 'MOD_ARRAY', 6),
                                         ('BEVEL', 'Bevel', '', 'MOD_BEVEL', 7),
                                         ('BOOLEAN', 'Boolean', '', 'MOD_BOOLEAN', 8),
                                         ('BUILD', 'Build', '', 'MOD_BUILD', 9),
                                         ('DECIMATE', 'Decimate', '', 'MOD_DECIM', 10),
                                         ('EDGE_SPLIT', 'Edge Split', '', 'MOD_EDGESPLIT', 11),
                                         ('MASK', 'Mask', '', 'MOD_MASK', 12),
                                         ('MIRROR', 'Mirror', '', 'MOD_MIRROR', 13),
                                         ('MULTIRES', 'Multiresolution', '', 'MOD_MULTIRES', 14),
                                         ('REMESH', 'Remesh', '', 'MOD_REMESH', 15),
                                         ('SCREW', 'Screw', '', 'MOD_SCREW', 16),
                                         ('SKIN', 'Skin', '', 'MOD_SKIN', 17),
                                         ('SOLIDIFY', 'Solidify', '', 'MOD_SOLIDIFY', 18),
                                         ('SUBSURF', 'Subsurface Division', '', 'MOD_SUBSURF', 19),
                                         ('TRIANGULATE', 'Triangulate', '', 'MOD_TRIANGULATE', 20),
                                         #Deform
                                         ('ARMATURE', 'Armature', '', 'MOD_ARMATURE', 21),
                                         ('CAST', 'Cast', '', 'MOD_CAST', 22),
                                         ('CURVE', 'Curve', '', 'MOD_CURVE', 23),
                                         ('DISPLACE', 'Displace', '', 'MOD_DISPLACE', 24),
                                         ('HOOK', 'Hook', '', 'HOOK', 25),
                                         ('LAPLACIANSMOOTH', 'Laplacian Smooth', '', 'MOD_SMOOTH', 26),
                                         ('LATTICE', 'Lattice', '', 'MOD_LATTICE', 27),
                                         ('MESH_DEFORM', 'Mesh Deform', '', 'MOD_MESHDEFORM', 28),
                                         ('SHRINKWRAP', 'Shrinkwrap', '', 'MOD_SHRINKWRAP', 29),
                                         ('SIMPLE_DEFORM', 'Simple Deform', '', 'MOD_SIMPLEDEFORM', 30),
                                         ('SMOOTH', 'Smooth', '', 'MOD_SMOOTH', 31),
                                         ('WARP', 'Warp', '', 'MOD_WARP', 32),
                                         ('WAVE', 'Wave', '', 'MOD_WAVE', 33),
                                         #Simulate
                                         ('CLOTH', 'Cloth', '', 'MOD_CLOTH', 34),
                                         ('COLLISION', 'Collision', '', 'MOD_PHYSICS', 35),
                                         ('DYNAMIC_PAINT', 'Dynamic Paint', '', 'MOD_DYNAMICPAINT', 36),
                                         ('EXPLODE', 'Explode', '', 'MOD_EXPLODE', 37),
                                         ('FLUID_SIMULATION', 'Fluid Simulation', '', 'MOD_FLUIDSIM', 38),
                                         ('OCEAN', 'Ocean', '', 'MOD_OCEAN', 39),
                                         ('PARTICLE_INSTANCE', 'Particle Instance', '', 'MOD_PARTICLES', 40),
                                         ('PARTICLE_SYSTEM', 'Particle System', '', 'MOD_PARTICLES', 41),
                                         ('SMOKE', 'Smoke', '', 'MOD_SMOKE', 42),
                                         ('SOFT_BODY', 'Soft Body', '', 'MOD_SOFT', 43)),
                                         name = '',
                                         description = 'Select type of modifier to be affected by the buttons below',
                                         default = 'SUBSURF')
    
    bpy.types.Scene.khalibloo_enumModifierFilterMode = bpy.props.EnumProperty(items =(
                                         ('ALL', 'All', 'Actions will affect all types of modifiers of all selected objects'),
                                         ('SPECIFIC', 'Specific', 'Actions will affect a specific type of modifier of all selected objects')),
                                name = ' ',
                                description = 'Choose whether to affect all types of modifiers or just a specific type',
                                default = 'ALL')
    
    bpy.types.Scene.khalibloo_spread_harden_vgroups = bpy.props.BoolProperty(
    name = "Spread Vertex Groups", 
    description = "Whether or not vertex group weights may spread to vertices that are not initially part of the vertex groups", 
    default=True)
    
    bpy.types.Scene.khalibloo_affect_textures = bpy.props.BoolProperty(
    name = "Textures", 
    description = "Whether or not the material setup affects textures as well", 
    default=True)
    
    bpy.types.Scene.khalibloo_merge_mats = bpy.props.BoolProperty(
    name = "Merge Materials", 
    description = "Merge materials with the same diffuse textures. Warning: This will affect EVERY material slot in the active Genesis figure, not just the default Genesis materials", 
    default = False)

    bpy.types.Scene.khalibloo_genesis_morph_dir = bpy.props.StringProperty(
    name = "",
    description = "Folder where your Genesis morphs of choice are located",
    subtype = "DIR_PATH",
    default = "c:/")
    
    bpy.types.Scene.khalibloo_enumBatchBakeImages = bpy.props.EnumProperty(items = (
                                ('Default', 'Default', ''),
                                ('Untitled', 'Untitled', '')),
                                name = "", 
                                description = "Image to save as",
                                default = 'Default')
    
    bpy.types.Scene.khalibloo_BatchBakeStartFrame = bpy.props.IntProperty(
    name = "Start Frame",
    description = "The frame from which to start baking",
    default = 1)
    
    bpy.types.Scene.khalibloo_BatchBakeEndFrame = bpy.props.IntProperty(
    name = "End Frame",
    description = "The frame on which to end baking",
    default = 250)




#============================================================================
# REGISTER AND UNREGISTER
#============================================================================

def register():
    initialize()
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
