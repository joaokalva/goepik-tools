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

def ShowMessageBox(custom_message = "", custom_title = "", custom_icon = ""):
    def draw(self, context):
        self.layout.label(text=custom_message)
    
    bpy.context.window_manager.popup_menu(draw, title = custom_title, icon = custom_icon)
        

class OBJECT_OT_clean_mesh(bpy.types.Operator):
    """Remove vértices duplas, aplica escala e rotação, limpa Custom Split Data, aplica Auto Smooth e recalcula normais"""
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
    """Remove vertices duplas, aplica escala e rotação, limpa Custom Split Data, aplica Auto Smooth e recalcula normais"""
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

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='EDIT')

        main_obj.data.uv_layers['UVMap.001'].active_render = True

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.edges_select_sharp(sharpness=1.0821)
        bpy.ops.mesh.mark_seam()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='CONFORMAL', margin=0.001)
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.005)
        
        main_obj.data.uv_layers['UVMap.001'].active_render = True

        ShowMessageBox("", "Uv's aplicadas com sucesso", "INFO") 
        
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
        
        row = layout.row(align=True)
        row.operator("mesh.clean_mesh")

        row = layout.row(align=True)
        row.operator("mesh.uvs_by_angle")

        my_bool : BoolProperty(
            name="Enable or Disable",
            description="A simple bool property",
            default = True) 

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
    bpy.types.VIEW3D_MT_mesh_add.append(add_object_button)
    
def unregister():
    bpy.utils.unregister_class(MyPanel)
    bpy.utils.unregister_class(OBJECT_OT_clean_mesh)
    bpy.utils.unregister_class(OBJECT_OT_uvs_by_angle)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_object_button)

if __name__ == "__main__":
    register()