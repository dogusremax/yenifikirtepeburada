"""Pişmiş ışık dokusunu (EXR) OIDN ile temizler ve sahneyle aynı renk dönüşümüyle (AgX) PNG'ye yazar.
Kullanım: python3 tools/kat3d/denoise.py <giriş.exr> <çıkış.png>"""
import bpy, sys
src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
img = bpy.data.images.load(src)
S.render.resolution_x, S.render.resolution_y = img.size; S.render.resolution_percentage = 100
S.render.engine = 'CYCLES'; S.cycles.samples = 1
cam = bpy.data.objects.new('c', bpy.data.cameras.new('c')); S.collection.objects.link(cam); S.camera = cam
ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); S.compositing_node_group = ng
ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
a = ng.nodes.new('CompositorNodeImage'); a.image = img
d = ng.nodes.new('CompositorNodeDenoise'); o = ng.nodes.new('NodeGroupOutput')
ng.links.new(a.outputs[0], d.inputs[0]); ng.links.new(d.outputs[0], o.inputs[0])
S.view_settings.view_transform = 'AgX'
try: S.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
S.view_settings.exposure = -0.4
S.render.image_settings.file_format = 'PNG'; S.render.image_settings.color_mode = 'RGB'; S.render.image_settings.color_depth = '8'
S.render.filepath = dst
bpy.ops.render.render(write_still=True)
