bl_info = {
    "name": "Kalva Tools",
    "author": "João Kalva",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar (N) > Kalva Tools",
    "description": "Tool Bundle",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
import math
import os 
import subprocess

debugging = False

def ShowMessageBox(custom_message = "", custom_title = "", custom_icon = ""):
    def draw(self, context):
        self.layout.label(text=custom_message)
    
    bpy.context.window_manager.popup_menu(draw, title = custom_title, icon = custom_icon)

def copy2clip(txt):
    cmd='echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)

def switchCollection(Collection):
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                vlayer = bpy.context.scene.view_layers['View Layer']
                for layer_collection in vlayer.layer_collection.children:
                    layer_collection.hide_viewport = True
                vlayer.layer_collection.children[Collection].hide_viewport = False

def SelectUVChannel(i = 0):
    for obj in bpy.context.selected_objects:
        while len(obj.data.uv_layers) < i+1:
            obj.data.uv_layers.new()
        if i == 0:
            obj.data.uv_layers[i].name = "UVMap"
        else:
            obj.data.uv_layers[i].name = "UVMap.00" + str(i)
        obj.data.uv_layers.active_index = i
class OBJECT_OT_clean_mesh(bpy.types.Operator):
    """Remove overlapping vertices, apply scale and rotation, remove Custom Split Data, apply Auto Smooth and recalculate normals. Set instances to active object to apply scale"""
    bl_idname = "mesh.clean_mesh"
    bl_label = "Clean Mesh(s)"
    
    def execute(self, context):   
            
        selection_names = [obj.name for obj in bpy.context.selected_objects]
                
        if len(selection_names) == 0:
            ShowMessageBox("Select an object", "Warning", "ERROR") ,
            return {'FINISHED'}

        # Apply Scale to Instances
        bpy.ops.object.select_linked(type='OBDATA')
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.object.make_links_data(type='OBDATA')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.auto_smooth_angle = 1.29154

        for listObject in selection_names:
            bpy.context.object.data.use_auto_smooth = True
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

        ShowMessageBox(" ; ".join(selection_names), "Mesh(s) successfully cleaned", "INFO") 
        
        return {'FINISHED'}
    
class OBJECT_OT_uvs_by_angle(bpy.types.Operator):
    """Create a second UV channel with UV's generated by angle"""
    bl_idname = "mesh.uvs_by_angle"
    bl_label = "UV's by angle (UV1)"

    def execute(self, context):
        
        main_obj = bpy.context.scene.objects[1]
        bpy.context.view_layer.objects.active = main_obj
        bpy.context.active_object.select_set(state=True)
         
        if len(main_obj.data.uv_layers) == 1:
            bpy.ops.mesh.uv_texture_add()
            
        if len(main_obj.data.uv_layers) > 2:
            while len(main_obj.data.uv_layers) > 2:
                bpy.ops.mesh.uv_texture_remove()
            
        main_obj.data.uv_layers['UVMap.001'].active = True
        main_obj.data.uv_layers['UVMap.001'].active_render = True
        
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.edges_select_sharp(sharpness=1.0821)
        bpy.ops.mesh.mark_seam()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.005)
        

        ShowMessageBox("New UV's in UV01", "Success!", "INFO") 
        
        bpy.ops.mesh.select_all(action='DESELECT')
   
        return {'FINISHED'}

class OBJECT_OT_pallette_uvs(bpy.types.Operator):
    """Take the angle of the viewport, make a skinny UVW with a consistent height of 0.3 for gradients"""
    bl_idname = "mesh.pallette_uvs"
    bl_label = "Pallette UV's"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if context.active_object.mode == 'OBJECT':
                    ShowMessageBox("Make a selection in edit mode", "Warning", "ERROR")
                    return {'FINISHED'}
                #area.spaces[0].region_3d.view_perspective = 'ORTHO'
                #bpy.ops.view3d.view_axis(type='FRONT', align_active=False, relative=False)
                bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=True)
                old_type = area.type
                
                bpy.context.area.type = 'IMAGE_EDITOR'
                old_ui_type = bpy.context.area.ui_type
                bpy.context.area.ui_type = 'UV'
                
                bpy.context.scene.tool_settings.use_uv_select_sync = True
                bpy.ops.transform.resize(value=(0, .3, .3), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.385543, use_proportional_connected=False, use_proportional_projected=False)
                bpy.context.scene.tool_settings.use_uv_select_sync = False
                
                bpy.context.area.ui_type = old_ui_type            
                bpy.context.area.type = 'VIEW_3D'

        ShowMessageBox("Pallette UV's.", "Success!", "INFO") 
        return {'FINISHED'}

class OBJECT_OT_automate_blocking(bpy.types.Operator):
    """Automate blocking and export for UE4"""
    bl_idname = "mesh.automate_blocking"
    bl_label = "UE4 Automate Blocking"

    def execute(self, context):
        try: 
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    if context.active_object.mode == 'EDIT':
                        ShowMessageBox("Make a selection in object mode", "Warning", "ERROR")
                        return {'FINISHED'}
            
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":0.385543, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
            bpy.ops.object.move_to_collection(collection_index=2)
            bpy.ops.object.hide_collection(collection_index=2)

            # Delete previous objects
            bpy.ops.object.select_all(action='INVERT')
            bpy.ops.object.delete(use_global=False)
            bpy.ops.object.select_all(action='INVERT')

            main_obj = bpy.context.scene.objects[1]
            bpy.context.view_layer.objects.active = main_obj
            bpy.context.active_object.select_set(state=True)
            
            bpy.ops.object.convert(target='MESH', keep_original=False)
            bpy.ops.object.join()

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = 0.907571


            bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')

            bpy.context.object.modifiers["WeightedNormal"].keep_sharp = True
            bpy.context.object.modifiers["WeightedNormal"].weight = 100
            bpy.ops.object.modifier_apply(modifier="WeightedNormal")
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            fbxpath = "D:\\João\\Documents\\3D\\CGMA Modularity\\Definitive Environment\\Everything.fbx"
            bpy.ops.export_scene.fbx(filepath=fbxpath, check_existing=True, axis_forward='-Y', axis_up='Z', filter_glob="*.fbx", use_selection=True, global_scale=1, apply_unit_scale=True, bake_space_transform=False, object_types={'MESH'}, use_mesh_modifiers=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=True, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0)

            ShowMessageBox("Exported as " + os.path.basename(os.path.normpath(fbxpath)), "Success!", "INFO") 
            return {'FINISHED'}

        except:
            ShowMessageBox("Select and active object", "Warning", "ERROR")
            return {'FINISHED'}

class OBJECT_OT_select_uv0(bpy.types.Operator):
    """If none, creates and selects UV1 for multiple objects"""
    bl_idname = "mesh.select_uv0"
    bl_label = "Select UV0"

    def execute(self, context):
        SelectUVChannel(0)
        # for area in bpy.context.screen.areas:
        #     if area.type == "VIEW_3D":
        #         bpy.ops.object.select_all(action='SELECT')
        #         bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class OBJECT_OT_select_uv1(bpy.types.Operator):
    """If none, creates and selects UV1 for multiple objects"""
    bl_idname = "mesh.select_uv1"
    bl_label = "Select UV1"

    def execute(self, context):
        SelectUVChannel(1)
        # for area in bpy.context.screen.areas:
        #     if area.type == "VIEW_3D":
        #         bpy.ops.object.select_all(action='SELECT')
        #         bpy.ops.object.select_all(action='DESELECT')
        return {'FINISHED'}

class OBJECT_OT_hyperbolica_export(bpy.types.Operator):
    """Automate export and error correction for Hyperbolica (takes .blend file name)"""
    bl_idname = "mesh.hyperbolica_export"
    bl_label = "Hyperbolica Export"

    def execute(self, context):
        # Disable VIEW_3D fullscreen 
        areas = 0
        for area in bpy.context.screen.areas:
            areas += 1 

        print("Areas: " + str(areas))

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if areas == 1:
                    bpy.ops.screen.screen_full_area({'area': area})
                    break

        switchCollection("Export")
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        switchCollection("Backup")

        currentpath = bpy.path.abspath("//")
        filename = os.path.basename(os.path.normpath(bpy.data.filepath)).replace('.blend', '')
        exportpath = currentpath + filename + '.fbx'

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        switchCollection("Backup")
                        try:
                            bpy.ops.object.hide_view_clear()
                        except:
                            ShowMessageBox("Export in windowed mode", "Warning", "ERROR")
                            return {'FINISHED'}

                        main_obj = bpy.data.collections["Backup"].objects[0]

                        bpy.context.view_layer.objects.active = main_obj
                        bpy.context.active_object.select_set(state=True)

                        bpy.ops.object.select_all(action='SELECT')
                        bpy.ops.object.duplicate()
                        bpy.ops.object.move_to_collection(collection_index=2)

                        switchCollection("Export")

                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
                        bpy.ops.object.convert(target='MESH', keep_original=False)

                        bpy.ops.object.join()
                        override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                        bpy.ops.view3d.view_all(override, center=True)
                        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.remove_doubles()
                        bpy.ops.object.mode_set(mode='OBJECT')

                        bpy.ops.mesh.customdata_custom_splitnormals_clear()
                        bpy.context.object.data.auto_smooth_angle = 1.6057
                        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

                        if len(main_obj.data.materials) > 1:
                            times = len(main_obj.data.materials) - 1
                            for n in range(times):
                                bpy.ops.object.material_slot_remove()

                        bpy.context.object.name = filename
        
        SelectUVChannel(0)

        bpy.ops.object.modifier_add(type='WEIGHTED_NORMAL')
        bpy.context.object.modifiers["WeightedNormal"].keep_sharp = True
        bpy.context.object.modifiers["WeightedNormal"].weight = 100
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.ops.object.modifier_add(type='WELD')
        bpy.context.object.modifiers["Weld"].merge_threshold = 1e-05

        # Use_mesh_modifiers on -> cannot export shape keys
        bpy.ops.export_scene.fbx(filepath=exportpath, axis_forward='-Z', axis_up='Y', use_selection=True, global_scale=1, bake_space_transform=True, apply_scale_options='FBX_SCALE_NONE', apply_unit_scale=True, object_types={'MESH', 'LIGHT'}, use_mesh_modifiers=True, mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=True, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0)

        copy2clip(filename)
        ShowMessageBox("Exported as " + exportpath, "Success!", "INFO") 
        return {'FINISHED'}

# Panel UI
class MyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Kalva Tools"
    bl_label = "Kalva Tools"
    bl_idname = "OBJECT_OT_clean_mesh"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        if debugging:
            self.layout.label(text="DEVELOPMENT", icon="ERROR")
        
        row = layout.row(align=True)
        row.operator("mesh.clean_mesh")

        row = layout.row(align=True)
        row.operator("mesh.uvs_by_angle")
        
        row = layout.row(align=True)
        row.operator("mesh.pallette_uvs")
        
        row = layout.row(align=True)
        row.operator("mesh.automate_blocking")

        self.layout.label(text="Hyperbolica")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('mesh.select_uv0', icon="UV_DATA")
        row.operator('mesh.select_uv1', icon="UV_DATA")
        row2 = col.row(align=True)
        row2.operator('mesh.hyperbolica_export', icon="EXPORT")

# Registration
def add_object_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_object.bl_idname,
        text="Add Object",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(MyPanel)
    bpy.utils.register_class(OBJECT_OT_clean_mesh)
    bpy.utils.register_class(OBJECT_OT_uvs_by_angle)   
    bpy.utils.register_class(OBJECT_OT_pallette_uvs)   
    bpy.utils.register_class(OBJECT_OT_automate_blocking)  
    bpy.utils.register_class(OBJECT_OT_select_uv0)  
    bpy.utils.register_class(OBJECT_OT_select_uv1)  
    bpy.utils.register_class(OBJECT_OT_hyperbolica_export)  
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    
def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(OBJECT_OT_clean_mesh)
    bpy.utils.unregister_class(OBJECT_OT_uvs_by_angle)
    bpy.utils.unregister_class(OBJECT_OT_pallette_uvs)
    bpy.utils.unregister_class(OBJECT_OT_automate_blocking)
    bpy.utils.unregister_class(OBJECT_OT_select_uv0)  
    bpy.utils.unregister_class(OBJECT_OT_select_uv1)  
    bpy.utils.unregister_class(OBJECT_OT_hyperbolica_export)  
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()