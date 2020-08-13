bl_info = {
    "name": "GoEPIK Tools",
    "author": "João Kalva",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Misc > GoEPIK Tools",
    "description": "Bundle de ferramentas GoEPIK",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
import math 

debugging = False

def ShowMessageBox(custom_message = "", custom_title = "", custom_icon = ""):
    def draw(self, context):
        self.layout.label(text=custom_message)
    
    bpy.context.window_manager.popup_menu(draw, title = custom_title, icon = custom_icon)
        

class OBJECT_OT_clean_mesh(bpy.types.Operator):
    """Remove vértices duplas, aplica escala e rotação, limpa Custom Split Data, aplica Auto Smooth e recalcula normais."""
    bl_idname = "mesh.clean_mesh"
    bl_label = "Limpar Mesh(s)"
    
    def execute(self, context):   
            
        selection_names = [obj.name for obj in bpy.context.selected_objects]
        
        if len(selection_names) == 0:
            ShowMessageBox("Nenhum objeto foi selecionado", "Aviso", "ERROR") ,
            return {'FINISHED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=True)
        bpy.ops.mesh.customdata_custom_splitnormals_clear()
        bpy.ops.object.shade_smooth()

        for listObject in selection_names:
            bpy.context.object.data.use_auto_smooth = True
            bpy.context.object.data.auto_smooth_angle = math.pi/2.5
            bpy.ops.mesh.customdata_custom_splitnormals_clear()

        ShowMessageBox(" ; ".join(selection_names), "Mesh(s) limpa(s) com sucesso", "INFO") 
        
        return {'FINISHED'}
    
class OBJECT_OT_uvs_by_angle(bpy.types.Operator):
    """Cria um segundo canal de UV com UVs por angulo."""
    bl_idname = "mesh.uvs_by_angle"
    bl_label = "UV's por ângulo (na UV1)"

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
        

        ShowMessageBox("Novas UV's na UV01", "Sucesso!", "INFO") 
        
        bpy.ops.mesh.select_all(action='DESELECT')
   
        return {'FINISHED'}

class OBJECT_OT_pallette_uvs(bpy.types.Operator):
    """Pega o angulo do viewport atual, faz automaticamente o UVW com tamanho constante de 0.3 de altura para gradientes."""
    bl_idname = "mesh.pallette_uvs"
    bl_label = "UV's para Pallette"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if context.active_object.mode == 'OBJECT':
                    ShowMessageBox("Faça uma seleção no modo de ediçao", "Aviso", "ERROR")
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
                
                bpy.context.area.ui_type = old_ui_type
                bpy.context.area.type = 'VIEW_3D'

        ShowMessageBox("UV's para Pallette.", "Sucesso!", "INFO") 
        return {'FINISHED'}


class OBJECT_OT_automate_blocking(bpy.types.Operator):
    """Automatiza o processo de Blocking. Selecione os objetos, e o resultado é a mesh pronta para a UE4."""
    bl_idname = "mesh.automate_blocking"
    bl_label = "Automate Blocking"

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                if context.active_object.mode == 'EDIT':
                    ShowMessageBox("Faça uma seleção no modo de objeto", "Aviso", "ERROR")
                    return {'FINISHED'}
    
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":True, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":0.385543, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
        bpy.ops.object.move_to_collection(collection_index=2)
        bpy.ops.object.hide_collection(collection_index=2)
    
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
        bpy.context.object.data.auto_smooth_angle = 1.25664

        ShowMessageBox("Blocking Setup.", "Sucesso!", "INFO") 
        return {'FINISHED'}

# Panel UI

class MyPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "GoEPIK Tools"
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
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    
def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(OBJECT_OT_clean_mesh)
    bpy.utils.unregister_class(OBJECT_OT_uvs_by_angle)
    bpy.utils.unregister_class(OBJECT_OT_pallette_uvs)
    bpy.utils.unregister_class(OBJECT_OT_automate_blocking)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()