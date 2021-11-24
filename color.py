import bpy

from bpy.props import (
    IntProperty,
    FloatProperty,
    IntVectorProperty,
    FloatVectorProperty,
    EnumProperty,
    BoolProperty,
)

bl_info = {
    'name': 'Blender Addon Color Palette',
    'author': 'ms16183',
    'version': (1, 0),
    'blender': (2, 93, 5),
    'location': '3DViewport > Sidebar',
    'description': 'Color Palette UI',
    'warning': '',
    'support': 'TESTING',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'User Interface'
}


class ColorPalette_OT_Nop(bpy.types.Operator):

    bl_idname = 'object.colorpalette_nop'
    bl_label = 'NOP'
    bl_description = 'NOP Op'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {'FINISHED'}


'''
class ColorPalette_MT_NopMenu(bpy.types.Menu):

    bl_idname = 'ColorPalette_MT_NopMenu'
    bl_label = 'NOP'
    bl_description = 'NOP Op'

    def draw(self, context):
        layout = self.layout
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Analogous')
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Triad')
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Square')

'''


# 0~1 -> 0~1
def rgb2hsv(R, G, B):
    maxval = max(R, G, B)
    minval = min(R, G, B)
    H = maxval - minval
    if H > 0.0:
        if maxval == R:
            H = (G - B) / H
            if H < 0.0:
                H += 6.0
        elif maxval == G:
            H = 2.0 + (B - R) / H
        else:
            H = 4.0 + (R - G) / H
    H /= 6.0
    S = (maxval - minval)
    if maxval != 0.0:
        S /= maxval
    V = maxval
    return H, S, V


# 0~1 -> 0~1
def hsv2rgb(H, S, V):
    R = G = B = V
    if S > 0.0:
        H *= 6.0
        i = int(H)
        F = H - float(i)
        if i == 0:
            G *= 1 - S * (1-F)
            B *= 1 - S
        if i == 1:
            R *= 1 - S * F
            B *= 1 - S
        if i == 2:
            R *= 1 - S
            B *= 1 - S * (1-F)
        if i == 3:
            R *= 1 - S
            G *= 1 - S * F
        if i == 4:
            R *= 1 - S * (1-F)
            G *= 1 - S
        if i == 5:
            G *= 1 - S
            B *= 1 - S * F
    return R, G, B


class VIEW3D_PT_ColorPalatte(bpy.types.Panel):

    bl_label = 'Color Palette'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Color Palette'
    #bl_context = 'objectmode'

    # Generate colors when updates.
    def generate_palette(self, context):
        # Generate a palette.
        palette_name = "AddonColorPalette"
        pal = bpy.data.palettes.get(palette_name)
        if pal is None:
            pal = bpy.data.palettes.new(palette_name)

        if pal:
            # Clear all colors on the palette.
            pal.colors.clear()
            
            for i in range(self.colorpalette_number_of_generate_color):
                # Get color wheel color.
                R, G, B = self.colorpalette_color
                # RGB(0~1) -> HSV(0~1)
                H, S, V = rgb2hsv(R, G, B)

                # HSV(0~1) -> H(0~360), SV(0~100)
                H *= 360
                S *= 100
                V *= 100

                # Add offset HSV for HSV.
                diff_H, diff_S, diff_V = self.colorpalette_diff_hsv
                H += diff_H * i
                S += diff_S * i
                V += diff_V * i

                # H(0~360), SV(0~100) -> HSV(0~1)
                H /= 360
                S /= 100
                V /= 100

                # HSV(0~1) -> RGB(0~1)
                R, G, B = hsv2rgb(H, S, V)

                # Generate colors on the palette.
                color = pal.colors.new()
                color.color = (R, G, B)
                color.weight = 1.0
                pal.colors.active = color

        context.tool_settings.image_paint.palette = pal
        return


    # Properties
    scene = bpy.types.Scene
    scene.colorpalette_color = FloatVectorProperty(
        name='',
        description='float(RGB) vector',
        subtype='COLOR_GAMMA',
        default=(1.0, 0.0, 1.0),
        min=0.0,
        max=1.0,
        update=generate_palette,
    )
    scene.colorpalette_diff_hsv = IntVectorProperty(
        name='Diff HSV',
        description='int vector',
        default=(12, 0, 3),
        min=-180,
        max=180,
        update=generate_palette,
    )
    scene.colorpalette_number_of_generate_color = IntProperty(
        name='Num of color',
        description='int',
        default=5,
        min=1,
        max=64,
        update=generate_palette,
    )
    '''
    scene.colorpalette_hermony_type = EnumProperty(
        name='',
        description='enum',
        items=[
            ('E_1', 'Analogous', 'Analogous'),
            ('E_2', 'Triad', 'Triad'),
            ('E_3', 'Square', 'Square'),
        ],
        default='E_1'
    )
    '''

    # Check if methods of this class is executable.
    @classmethod
    def poll(cls, context):
        return True

    # Custom header
    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='COLOR')

    # Menu
    def draw(self, context):

        layout = self.layout
        scene = context.scene

        # Color wheel
        layout.label(text='Base Color:')
        layout.template_color_picker(scene, 'colorpalette_color', value_slider=True)
        layout.prop(scene, 'colorpalette_color')

        layout.separator()

        # Diff HSV
        box = layout.row().box()

        box.prop(scene, 'colorpalette_diff_hsv', text='Diff HSV')

        box.label(text='Palette:')
        if context.tool_settings.image_paint.palette:
            box.prop(scene, 'colorpalette_number_of_generate_color', text='num')
            box.template_palette(context.tool_settings.image_paint, 'palette', color=True)

        layout.separator()


def clear_props():
    scene = bpy.types.Scene
    del scene.colorpalette_color
    del scene.colorpalette_diff_hsv
    del scene.colorpalette_number_of_generate_color


classes = [
    #ColorPalette_OT_Nop,
    #ColorPalette_MT_NopMenu,
    VIEW3D_PT_ColorPalatte,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)
    #VIEW3D_PT_ColorPalatte.init_props()


def unregister():
    clear_props()
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()

