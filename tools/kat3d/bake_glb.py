"""Gerçek zamanlı 3D model: build.py sahnesini kurar, tüm ışığı (Cycles) tek bir dokuya pişirir ve GLB olarak yazar.
Kullanım: python3 tools/kat3d/bake_glb.py <plan_id> <out.glb> [doku_boyutu=4096] [örnek=64]
Tarayıcıda ışık hesabı gerekmez: model her açıdan fotoğraftaki ışıkla görünür. Yer gölgesi yoktur."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
PID, OUT = sys.argv[1], os.path.abspath(sys.argv[2])
RES = int(sys.argv[3]) if len(sys.argv) > 3 else 4096
SAMP = int(sys.argv[4]) if len(sys.argv) > 4 else 64
sys.argv = [os.path.join(HERE, 'build.py'), PID, 'glb']
exec(compile(open(sys.argv[0]).read(), sys.argv[0], 'exec'))
t0 = time.time()
g = bpy.data.objects.get('ground')
if g: bpy.data.objects.remove(g, do_unlink=True)
setup_render(512, 512, SAMP)
S.cycles.use_denoising = False
dg = bpy.context.evaluated_depsgraph_get()
glass, solid = [], []
for o in list(S.objects):
    if o.type != 'MESH' or o.hide_render: continue
    isg = any(s.material and s.material.name.startswith('glass') for s in o.material_slots)
    # değiştiricileri uygula, dünya koordinatına çevir, ebeveynden kopar
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    me.transform(o.matrix_world)
    n = bpy.data.objects.new(o.name + '_m', me); S.collection.objects.link(n)
    # çok ayrıntılı nesneleri (bitki, yuvarlatılmış eşya) sadeleştir: tarayıcıda hızlı açılsın
    if len(me.vertices) > 3000:
        dm = n.modifiers.new('dec', 'DECIMATE'); dm.ratio = max(0.08, 3000 / len(me.vertices))
        me2 = bpy.data.meshes.new_from_object(n.evaluated_get(bpy.context.evaluated_depsgraph_get())); n.modifiers.clear(); n.data = me2
    (glass if isg else solid).append(n)
for o in list(S.objects):
    if o.type in ('MESH', 'EMPTY') and o not in glass and o not in solid: bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in solid: o.select_set(True)
bpy.context.view_layer.objects.active = solid[0]
bpy.ops.object.join(); plan = bpy.context.view_layer.objects.active; plan.name = 'plan'
me = plan.data
if not me.uv_layers: me.uv_layers.new(name='UVMap')
render_uv = me.uv_layers[0]; render_uv.active_render = True
bake_uv = me.uv_layers.new(name='bake'); me.uv_layers.active = bake_uv
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.001, area_weight=0.0, scale_to_bounds=True)
try: bpy.ops.uv.pack_islands(rotate=True, margin=0.0012, shape_method='CONCAVE')
except TypeError: bpy.ops.uv.pack_islands(rotate=True, margin=0.0012)
bpy.ops.object.mode_set(mode='OBJECT')
img = bpy.data.images.new('bake', RES, RES, alpha=False, float_buffer=True)
for s in plan.material_slots:
    m = s.material
    if not m or not m.use_nodes: continue
    nd = m.node_tree.nodes.new('ShaderNodeTexImage'); nd.image = img
    m.node_tree.nodes.active = nd
print('hazırlık %.0f sn, bake başlıyor' % (time.time() - t0), flush=True)
S.render.bake.margin = 6; S.render.bake.use_pass_direct = True; S.render.bake.use_pass_indirect = True
bpy.ops.object.select_all(action='DESELECT'); plan.select_set(True); bpy.context.view_layer.objects.active = plan
bpy.ops.object.bake(type='COMBINED')
print('bake %.0f sn' % (time.time() - t0), flush=True)
# pişmiş ışığı OIDN ile temizle ve sahneyle aynı renk dönüşümüyle (AgX) PNG'ye çevir
import subprocess
img.filepath_raw = OUT + '.exr'; img.file_format = 'OPEN_EXR'; img.save()
subprocess.run([sys.executable, os.path.join(HERE, 'denoise.py'), OUT + '.exr', OUT + '.png'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
lit = bpy.data.images.load(OUT + '.png')
# tek, ışıksız malzeme
for u in list(me.uv_layers):
    if u.name != 'bake': me.uv_layers.remove(u)
me.materials.clear()
mat = bpy.data.materials.new('baked'); mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial'); bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = lit
nt.links.new(tx.outputs[0], bsdf.inputs['Base Color']); nt.links.new(bsdf.outputs[0], out.inputs[0])
me.materials.append(mat)
gm = bpy.data.materials.new('glass_rt'); gm.use_nodes = True; b = gm.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value = (0.85, 0.9, 0.95, 1); b.inputs['Alpha'].default_value = 0.18; b.inputs['Roughness'].default_value = 0.05
for o in glass:
    o.data.materials.clear(); o.data.materials.append(gm)
# oda etiketleri için 3B noktalar (glTF ekseni: x, z, -y), oda adları ve alanları
import json
lab = []
for r in PLAN['rooms']:
    c = r[5] if len(r) > 5 else None
    if not c:
        p = poly(r); c = [sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)]
    lab.append([r[0], r[1].replace('Ebeveyn Yatak Odası', 'Ebeveyn Y. Odası'), r[2], [round(X(c[0]), 3), 0.15, round(-Y(c[1]), 3)]])
json.dump({'rooms': lab}, open(os.path.splitext(OUT)[0] + '.json', 'w'), ensure_ascii=False, separators=(',', ':'))
bpy.ops.object.select_all(action='DESELECT')
for o in [plan] + glass: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_image_format='WEBP', export_image_quality=86,
                          export_apply=True, export_normals=False, export_tangents=False, export_yup=True, export_materials='EXPORT', export_draco_mesh_compression_enable=False)
print('bitti %.0f sn' % (time.time() - t0), flush=True)
