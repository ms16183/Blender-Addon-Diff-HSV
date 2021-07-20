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
    'blender': (2, 83, 12),
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


class ColorPalette_MT_NopMenu(bpy.types.Menu):

    bl_idname = 'ColorPalette_MT_NopMenu'
    bl_label = 'NOP'
    bl_description = 'NOP Op'

    def draw(self, context):
        layout = self.layout
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Analogous')
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Triad')
        layout.operator(ColorPalette_OT_Nop.bl_idname, text='Square')



# カスタムパネル
class VIEW3D_PT_ColorPalatte(bpy.types.Panel):

    bl_label = 'Color Palette'         # パネルのヘッダに表示される文字列
    bl_space_type = 'VIEW_3D'           # パネルを登録するスペース
    bl_region_type = 'UI'               # パネルを登録するリージョン
    bl_category = 'Color Palette'        # パネルを登録するタブ名
    #bl_context = 'objectmode'           # パネルを表示するコンテキスト

    # パレット生成
    pal = bpy.data.palettes.get("Addon Color Palette")
    pal2 = bpy.data.palettes.get("Addon Color Palette2")
    if pal is None:
        pal = bpy.data.palettes.new("Addon Color Palette")
    if pal2 is None:
        pal2 = bpy.data.palettes.new("Addon Color Palette2")

    ts = bpy.context.tool_settings   
    ts.image_paint.palette = pal

    # カラー変更時にパレットの色を生成する
    def generate_palette(self, context):
        # パレット取得
        ts = context.tool_settings
        pal = ts.image_paint.palette
        if pal:
            # パレットの色をすべてクリア
            pal.colors.clear()
            
            # TODO: RGB->HSV等は関数として処理
            for i in range(self.colorpalette_number_of_generate_color):
                # カラーホイールのRGBを取得
                R, G, B = self.colorpalette_color
                # RGB(0~1) -> HSV(0~1)
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

                # HSV(0~1) -> H(0~360), SV(0~100)
                H *= 360
                S *= 100
                V *= 100

                # ずらす値を取得
                diff_H, diff_S, diff_V = self.colorpalette_diff_hsv
                # ずらす
                H += diff_H * i
                S += diff_S * i
                V += diff_V * i

                # H(0~360), SV(0~100) -> HSV(0~1)
                H /= 360
                S /= 100
                V /= 100

                # HSV(0~1) -> RGB(0~1)
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
                        B *- 1 - S * F

                # パレット作成
                color = pal.colors.new()
                color.color = (R, G, B)
                color.weight = 1.0
                pal.colors.active = color
        return

    # プロパティ生成
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
        default=(0, 0, 0),
        min=-180,
        max=180,
        update=generate_palette,
    )
    scene.colorpalette_number_of_generate_color = IntProperty(
        name='Num of color',
        description='int',
        default=5,
        min=1,
        max=16,
        update=generate_palette,
    )
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

    # 本クラスの処理が実行可能かを判定する
    @classmethod
    def poll(cls, context):
        return True

    # ヘッダーのカスタマイズ
    def draw_header(self, context):
        layout = self.layout
        layout.label(icon='COLOR')

    # メニューの描画処理
    def draw(self, context):

        layout = self.layout
        scene = context.scene

        # カラーホイールを追加
        layout.label(text='Base Color:')
        layout.template_color_picker(scene, 'colorpalette_color', value_slider=True)
        layout.prop(scene, 'colorpalette_color')

        # セパレータを追加
        layout.separator()

        # Diff HSV
        box = layout.row().box()

        # テキストボックスを追加
        box.prop(scene, 'colorpalette_diff_hsv', text='Diff HSV')

        # パレットを追加
        box.label(text='Palette:')
        ts = context.tool_settings
        if ts.image_paint.palette:
            box.prop(scene, 'colorpalette_number_of_generate_color', text='num')
            box.template_palette(ts.image_paint, 'palette', color=True)

        # セパレータを追加
        layout.separator()


# プロパティを削除
def clear_props():
    scene = bpy.types.Scene
    del scene.colorpalette_color
    del scene.colorpalette_diff_hsv


classes = [
    ColorPalette_OT_Nop,
    ColorPalette_MT_NopMenu,
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

