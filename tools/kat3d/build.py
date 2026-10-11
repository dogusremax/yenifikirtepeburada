"""Yeni Fikirtepe kat planı fotogerçekçi sahne üreticisi (Blender/bpy, Cycles).
Kullanım: python3 build.py <plan_id> <mode> [args]
  mode: top <out.png> <res>        tepeden ortografik
        spin <outdir> <n> <res>    n karelik tur (yükseklik açısı sabit)
        test <out.png> <res> <deg> tek perspektif kare
"""
import bpy, bmesh, json, math, sys, os, random
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
PID, MODE = args[0], args[1]
_pf = os.path.join(HERE, 'plans', PID + '.json')
if os.path.exists(_pf):
    PLAN = json.load(open(_pf)); EXTRA = PLAN.get('extra', {})
else:
    PLAN = [p for p in json.load(open(os.path.join(HERE, 'plans.json'))) if p['id'] == PID][0]
    EXTRA = json.load(open(os.path.join(HERE, 'extra.json'))).get(PID, {})
PLAN.setdefault('solid', []); PLAN.setdefault('opens', []); PLAN.setdefault('wins', []); PLAN.setdefault('furn', [])
random.seed(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene

# ---------------- geometri yardımcıları ----------------
def poly(r):
    g = r[4]
    return [[g[0], g[1]], [g[2], g[1]], [g[2], g[3]], [g[0], g[3]]] if isinstance(g[0], (int, float)) else g

def parea(p):
    s = 0
    for i in range(len(p)):
        a, b = p[i], p[(i + 1) % len(p)]
        s += a[0] * b[1] - b[0] * a[1]
    return abs(s) / 2

sa = sum(parea(poly(r)) for r in PLAN['rooms']); sm = sum(r[2] for r in PLAN['rooms'])
PPM = math.sqrt(sa / sm)
xs = [q[0] for r in PLAN['rooms'] for q in poly(r)]; ys = [q[1] for r in PLAN['rooms'] for q in poly(r)]
BB = [min(xs), min(ys), max(xs), max(ys)]
CX, CY = (BB[0] + BB[2]) / 2, (BB[1] + BB[3]) / 2
def X(px): return (px - CX) / PPM
def Y(py): return -(py - CY) / PPM
def M(px): return px / PPM
SX, SY = M(BB[2] - BB[0]), M(BB[3] - BB[1])
T = 0.17           # duvar kalınlığı (m)
H = 2.25           # duvar yüksekliği
FL = 0.0           # döşeme üst kotu

ROOMS = {r[0]: r for r in PLAN['rooms']}
def room_of(px, py):
    for r in PLAN['rooms']:
        p = poly(r); inside = False
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            if (a[1] > py) != (b[1] > py) and px < (b[0] - a[0]) * (py - a[1]) / (b[1] - a[1] + 1e-9) + a[0]:
                inside = not inside
        if inside: return r
    return None

# ---------------- malzemeler ----------------
MATS = {}
def node_mat(name, build):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    build(nt, bsdf)
    MATS[name] = m
    return m

def hexc(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0], c[1], c[2], a)

def simple(name, col, rough=0.5, metal=0.0, sheen=0.0, coat=0.0, trans=0.0, ior=1.45, spec=0.5, emit=None):
    def b(nt, p):
        p.inputs['Base Color'].default_value = hexc(col)
        p.inputs['Roughness'].default_value = rough
        p.inputs['Metallic'].default_value = metal
        if sheen: p.inputs['Sheen Weight'].default_value = sheen; p.inputs['Sheen Roughness'].default_value = 0.4
        if coat: p.inputs['Coat Weight'].default_value = coat
        if trans: p.inputs['Transmission Weight'].default_value = trans; p.inputs['IOR'].default_value = ior
        if emit: p.inputs['Emission Color'].default_value = hexc(emit[0]); p.inputs['Emission Strength'].default_value = emit[1]
    return node_mat(name, b)

def tex(nt, path, cs='sRGB'):
    n = nt.nodes.new('ShaderNodeTexImage')
    n.image = bpy.data.images.load(os.path.join(HERE, path), check_existing=True)
    n.image.colorspace_settings.name = cs
    return n

def wood_floor(name, rot=0.0, scale=0.55, tint='#ffffff'):
    def b(nt, p):
        tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Rotation'].default_value[2] = rot
        mp.inputs['Scale'].default_value = (scale, scale, scale)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        d = tex(nt, 'hardwood2_diffuse.jpg'); r = tex(nt, 'hardwood2_roughness.jpg', 'Non-Color'); bm = tex(nt, 'hardwood2_bump.jpg', 'Non-Color')
        for n in (d, r, bm): nt.links.new(mp.outputs[0], n.inputs['Vector'])
        hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 0.62; hsv.inputs['Value'].default_value = 1.18
        nt.links.new(d.outputs['Color'], hsv.inputs['Color'])
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1
        nt.links.new(hsv.outputs[0], mix.inputs[6]); mix.inputs[7].default_value = hexc(tint)
        nt.links.new(mix.outputs[2], p.inputs['Base Color'])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.28; mr.inputs['To Max'].default_value = 0.55
        nt.links.new(r.outputs['Color'], mr.inputs['Value']); nt.links.new(mr.outputs[0], p.inputs['Roughness'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; bp.inputs['Distance'].default_value = 0.002
        nt.links.new(bm.outputs['Color'], bp.inputs['Height']); nt.links.new(bp.outputs[0], p.inputs['Normal'])
        p.inputs['Coat Weight'].default_value = 0.15; p.inputs['Coat Roughness'].default_value = 0.2
    return node_mat(name, b)

def tile_floor(name, col='#d8d4cc', size=0.6, grout='#b9b4ab', rough=0.22, rect=False):
    def b(nt, p):
        tc = nt.nodes.new('ShaderNodeTexCoord')
        br = nt.nodes.new('ShaderNodeTexBrick')
        br.offset = 0.5 if rect else 0.0; br.squash = 1.0
        br.inputs['Scale'].default_value = 1.0 / size
        br.inputs['Mortar Size'].default_value = 0.0035 / size * 1.0
        br.inputs['Brick Width'].default_value = 1.0 if not rect else 2.0
        br.inputs['Row Height'].default_value = 1.0
        br.inputs['Mortar Smooth'].default_value = 0.1
        nt.links.new(tc.outputs['Object'], br.inputs['Vector'])
        ns = nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 3.0; ns.inputs['Detail'].default_value = 6
        nt.links.new(tc.outputs['Object'], ns.inputs['Vector'])
        c1 = nt.nodes.new('ShaderNodeMix'); c1.data_type = 'RGBA'; c1.inputs[6].default_value = hexc(col)
        c1.inputs[7].default_value = tuple(min(1, v * 1.06) for v in hexc(col)[:3]) + (1,)
        nt.links.new(ns.outputs['Fac'], c1.inputs['Factor'])
        br.inputs['Color1'].default_value = (1, 1, 1, 1); br.inputs['Color2'].default_value = (0.94, 0.94, 0.94, 1)
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
        nt.links.new(c1.outputs[2], mul.inputs[6]); nt.links.new(br.outputs['Color'], mul.inputs[7])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        nt.links.new(br.outputs['Fac'], mx.inputs['Factor']); nt.links.new(mul.outputs[2], mx.inputs[6]); mx.inputs[7].default_value = hexc(grout)
        nt.links.new(mx.outputs[2], p.inputs['Base Color'])
        rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = rough; rr.inputs['To Max'].default_value = 0.8
        nt.links.new(br.outputs['Fac'], rr.inputs['Value']); nt.links.new(rr.outputs[0], p.inputs['Roughness'])
        bp = nt.nodes.new('ShaderNodeBump'); bp.invert = True; bp.inputs['Strength'].default_value = 0.6; bp.inputs['Distance'].default_value = 0.002
        nt.links.new(br.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs[0], p.inputs['Normal'])
    return node_mat(name, b)

def fabric(name, col, rough=0.85, sheen=0.6, scale=180.0, bump=0.08):
    def b(nt, p):
        tc = nt.nodes.new('ShaderNodeTexCoord')
        ns = nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = scale; ns.inputs['Detail'].default_value = 2
        nt.links.new(tc.outputs['Object'], ns.inputs['Vector'])
        ns2 = nt.nodes.new('ShaderNodeTexNoise'); ns2.inputs['Scale'].default_value = 4; ns2.inputs['Detail'].default_value = 3
        nt.links.new(tc.outputs['Object'], ns2.inputs['Vector'])
        c = nt.nodes.new('ShaderNodeMix'); c.data_type = 'RGBA'; c.inputs[6].default_value = hexc(col)
        c.inputs[7].default_value = tuple(v * 0.86 for v in hexc(col)[:3]) + (1,)
        nt.links.new(ns2.outputs['Fac'], c.inputs['Factor']); nt.links.new(c.outputs[2], p.inputs['Base Color'])
        p.inputs['Roughness'].default_value = rough
        p.inputs['Sheen Weight'].default_value = sheen; p.inputs['Sheen Roughness'].default_value = 0.35
        bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.001
        nt.links.new(ns.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs[0], p.inputs['Normal'])
    return node_mat(name, b)

def marble(name, base='#f2f0ec', vein='#c9c5bf'):
    def b(nt, p):
        tc = nt.nodes.new('ShaderNodeTexCoord')
        ns = nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 2.2; ns.inputs['Detail'].default_value = 12; ns.inputs['Distortion'].default_value = 3.5
        nt.links.new(tc.outputs['Object'], ns.inputs['Vector'])
        wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 0.7; wv.inputs['Distortion'].default_value = 14; wv.inputs['Detail'].default_value = 8
        nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
        cr = nt.nodes.new('ShaderNodeValToRGB')
        cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = hexc(vein)
        cr.color_ramp.elements[1].position = 0.05; cr.color_ramp.elements[1].color = hexc(base)
        nt.links.new(wv.outputs['Fac'], cr.inputs['Fac'])
        nt.links.new(cr.outputs['Color'], p.inputs['Base Color'])
        p.inputs['Roughness'].default_value = 0.12; p.inputs['Coat Weight'].default_value = 0.3
    return node_mat(name, b)

def oak(name, tint='#ffffff', rough=0.5):
    return wood_floor(name, 0.0, 1.6, tint)

M_WALL = simple('wall', '#F4F2EE', 0.92)
M_CAP = simple('cap', '#0B1238', 0.6)
M_PLINTH = simple('plinth', '#FFFFFF', 0.7)
def _glass(nt, p):
    # yalnızca kameradan bakışta hafif yansıma; diğer tüm ışınlar için tam saydam
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (0.95, 0.97, 0.98, 1)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.03
    gl.inputs['Color'].default_value = (0.9, 0.93, 0.96, 1)
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.5
    lp = nt.nodes.new('ShaderNodeLightPath')
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'
    nt.links.new(fr.outputs[0], mu.inputs[0]); nt.links.new(lp.outputs['Is Camera Ray'], mu.inputs[1])
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(mu.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
M_GLASS = node_mat('glass', _glass)
M_FRAME = simple('frame', '#2B2F3A', 0.35, metal=0.6)
M_WHITE = simple('whitegloss', '#F6F6F4', 0.25, coat=0.2)
M_MATTE = simple('whitematte', '#EEEDEA', 0.6)
M_CERAMIC = simple('ceramic', '#FBFBFA', 0.08, coat=0.5)
M_CHROME = simple('chrome', '#E8E8E8', 0.08, metal=1.0)
M_BLACKM = simple('blackmetal', '#1E1F24', 0.4, metal=0.7)
M_BLACKG = simple('blackglass', '#0C0D10', 0.05, coat=1.0)
M_SCREEN = simple('screen', '#08090C', 0.12, coat=1.0)
M_STEEL = simple('steel', '#C9CCD1', 0.28, metal=1.0)
M_NAVYF = fabric('navyfabric', '#1C2552', 0.9, 0.8)
M_LINEN = fabric('linen', '#F3F1EC', 0.92, 0.3, 260, 0.05)
M_DUVET = fabric('duvet', '#E9E4DA', 0.9, 0.4, 220, 0.06)
M_THROW = fabric('throw', '#C9504F', 0.95, 0.6, 140, 0.12)
M_HEAD = fabric('headboard', '#8E97A8', 0.92, 0.6)
M_RUG = fabric('rug', '#ECE4D6', 0.98, 0.2, 90, 0.25)
M_RUGB = fabric('rugb', '#8C7B68', 0.98, 0.2, 90, 0.25)
M_CUSH = fabric('cushion', '#D8B48A', 0.9, 0.6)
M_CUSH2 = fabric('cushion2', '#F0E7DA', 0.9, 0.5)
M_OAK = oak('oakfurn', '#f2e6d8')
M_OAKD = oak('oakdark', '#9b8574')
M_MARBLE = marble('marble')
M_NAVYDOOR = simple('navydoor', '#121A44', 0.45, coat=0.3)
M_CAB = simple('cabinet', '#E9E7E2', 0.45)
M_CABN = simple('cabnavy', '#1A2350', 0.5)
M_LEAF = simple('leaf', '#4F6B3A', 0.6)
M_SHADOWC = None

# ---------------- mesh yardımcıları ----------------
COLL = bpy.data.collections.new('plan'); S.collection.children.link(COLL)
def link(o):
    COLL.objects.link(o); return o

def box(name, x1, y1, z1, x2, y2, z2, mat, bevel=0.004, seg=2, sub=0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.scale = (abs(x2 - x1), abs(y2 - y1), abs(z2 - z1))
    o.location = ((x1 + x2) / 2, (y1 + y2) / 2, (z1 + z2) / 2)
    bpy.context.view_layer.update()
    me.transform(Matrix.Diagonal((o.scale[0], o.scale[1], o.scale[2], 1))); o.scale = (1, 1, 1)
    me.materials.append(mat)
    if bevel > 0:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = min(bevel, min(abs(x2-x1), abs(y2-y1), abs(z2-z1)) / 2.2); b.segments = seg; b.limit_method = 'NONE'
    if sub:
        s = o.modifiers.new('sub', 'SUBSURF'); s.levels = sub; s.render_levels = sub
    for p in me.polygons: p.use_smooth = True
    return o

def cyl(name, x, y, z1, z2, r, mat, verts=48, bevel=0.003, rx=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=z2 - z1)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.location = (x, y, (z1 + z2) / 2)
    if rx: o.scale = (1, rx, 1)
    me.materials.append(mat)
    if bevel: b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'
    for p in me.polygons: p.use_smooth = True
    return o

def pillow(name, cx, cy, z, w, d, h, mat, rot=0.0):
    o = box(name, cx - w / 2, cy - d / 2, z, cx + w / 2, cy + d / 2, z + h, mat, bevel=min(w, d, h) * 0.45, seg=4, sub=2)
    o.rotation_euler[2] = rot
    return o

def offset_poly(pts, d):
    n = len(pts); ar = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sg = 1 if ar > 0 else -1
    def nrm(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        return (sg * dy / L, -sg * dx / L)
    out = []
    for i in range(n):
        a, c, b = pts[i - 1], pts[i], pts[(i + 1) % n]
        n1, n2 = nrm(a, c), nrm(c, b)
        if abs(n1[0] - n2[0]) < 1e-6 and abs(n1[1] - n2[1]) < 1e-6: m = n1
        else: m = (n1[0] + n2[0], n1[1] + n2[1])
        out.append([c[0] + d * m[0], c[1] + d * m[1]])
    return out

def poly_slab(name, pts, z1, z2, mat):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vb = [bm.verts.new((X(p[0]), Y(p[1]), z1)) for p in pts]
    f = bm.faces.new(vb)
    if f.normal.z < 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    for v in [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z = z2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); me.materials.append(mat)
    return o

def import_glb(fn, keep=None):
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, fn))
    names = [o.name for o in bpy.data.objects if o.name not in before]
    for n in names:
        o = bpy.data.objects[n]
        for c in list(o.users_collection): c.objects.unlink(o)
        COLL.objects.link(o)
    drop = [n for n in names if bpy.data.objects[n].type == 'MESH' and keep and not any(k in n for k in keep)]
    for n in drop: bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)
    names = [n for n in names if n not in drop]
    par = bpy.data.objects.new(fn + '_root', None); link(par)
    for n in names:
        o = bpy.data.objects[n]
        if o.parent is None: o.parent = par
    return par

# ---------------- duvarlar ----------------
def segments():
    TOL = 0.22 * PPM
    cuts = PLAN['doors'] + PLAN['opens'] + PLAN['wins']
    walls, rails = [], []
    for r in PLAN['rooms']:
        p = poly(r); bal = r[3] == 'balk'
        for i in range(len(p)):
            a, b = p[i], p[(i + 1) % len(p)]
            o = 'h' if a[1] == b[1] else 'v'; c = a[1] if o == 'h' else a[0]
            lo = min(a[0], b[0]) if o == 'h' else min(a[1], b[1]); hi = max(a[0], b[0]) if o == 'h' else max(a[1], b[1])
            segs = [[lo, hi, 1, 1]]
            for k in cuts:
                if k[0] != o or abs(k[1] - c) > TOL: continue
                n = []
                for s in segs:
                    if k[3] <= s[0] or k[2] >= s[1]: n.append(s); continue
                    if k[2] > s[0]: n.append([s[0], k[2], s[2], 0])
                    if k[3] < s[1]: n.append([k[3], s[1], 0, s[3]])
                segs = n
            for s in segs:
                if s[1] - s[0] > 1:
                    ext = T / 2 * PPM
                    (rails if bal else walls).append((o, c, s[0] - (ext if s[2] else 0), s[1] + (ext if s[3] else 0)))
    return merge(walls), merge(rails)

def merge(ws):
    # yakın ve paralel duvarları tek duvarda birleştir (çakışan yüzleri önler)
    snap = 0.9 * T * PPM
    out = []
    for o in ('h', 'v'):
        group = sorted([w for w in ws if w[0] == o], key=lambda w: w[1])
        clusters = []
        for w in group:
            if clusters and abs(w[1] - clusters[-1][0]) < snap:
                cl = clusters[-1]; cl[1].append(w)
                cl[0] = sum(x[1] for x in cl[1]) / len(cl[1])
            else:
                clusters.append([w[1], [w]])
        for c, items in clusters:
            iv = sorted([[w[2], w[3]] for w in items])
            m = []
            for a, b in iv:
                if m and a <= m[-1][1] + 0.5: m[-1][1] = max(m[-1][1], b)
                else: m.append([a, b])
            for a, b in m: out.append((o, round(c, 2), a, b))
    return out

def wall_box(name, o, c, a, b, z1, z2, mat, t=T, bevel=0.0):
    if o == 'h':
        return box(name, X(a), Y(c) - t / 2, z1, X(b), Y(c) + t / 2, z2, mat, bevel)
    return box(name, X(c) - t / 2, Y(b), z1, X(c) + t / 2, Y(a), z2, mat, bevel)

def build_walls():
    walls, rails = segments()
    for i, w in enumerate(walls):
        wall_box('wall%d' % i, *w, FL, H, M_WALL)
        wall_box('cap%d' % i, *w, H, H + 0.012, M_CAP, T + 0.004)
    for i, w in enumerate(rails):
        wall_box('railg%d' % i, *w, FL, 1.0, M_GLASS, 0.012)
        wall_box('railt%d' % i, *w, 1.0, 1.04, M_FRAME, 0.05)
        wall_box('railb%d' % i, *w, FL, 0.06, M_FRAME, 0.05)
    for s in PLAN['solid']:
        box('solid', X(s[0]), Y(s[3]), FL, X(s[2]), Y(s[1]), H, M_WALL, 0)
        box('solidcap', X(s[0]), Y(s[3]), H, X(s[2]), Y(s[1]), H + 0.012, M_CAP, 0)
    # pencereler
    for i, k in enumerate(PLAN['wins']):
        o, c, a, b = k
        full = room_of(*( (a + b) / 2, c + 0.4 * PPM) if o == 'h' else (c + 0.4 * PPM, (a + b) / 2))
        full2 = room_of(*( (a + b) / 2, c - 0.4 * PPM) if o == 'h' else (c - 0.4 * PPM, (a + b) / 2))
        door = (full and full[3] == 'balk') or (full2 and full2[3] == 'balk')
        sill = 0.0 if door else 0.85
        if sill > 0: wall_box('sill%d' % i, o, c, a, b, FL, sill, M_WALL)
        wall_box('lint%d' % i, o, c, a, b, 2.15, H, M_WALL)
        wall_box('lcap%d' % i, o, c, a, b, H, H + 0.012, M_CAP, T + 0.004)
        wall_box('glass%d' % i, o, c, a, b, sill, 2.15, M_GLASS, 0.02)
        wall_box('fb%d' % i, o, c, a, b, sill, sill + 0.05, M_FRAME, 0.07)
        wall_box('ft%d' % i, o, c, a, b, 2.1, 2.15, M_FRAME, 0.07)
        L = b - a; n = max(1, round(M(L) / 0.9))
        for j in range(n + 1):
            q = a + L * j / n; w = 0.025 * PPM
            wall_box('fm%d_%d' % (i, j), o, c, q - w, q + w, sill, 2.15, M_FRAME, 0.07)
        if sill > 0:
            wall_box('sillstone%d' % i, o, c, a, b, sill - 0.02, sill + 0.01, M_MARBLE, T + 0.06)
    # kapılar: lento + kanat
    for i, d in enumerate(PLAN['doors']):
        o, c, a, b, hg = d[0], d[1], d[2], d[3], d[4]
        s = d[5]; main = len(d) > 6 and d[6]
        wall_box('dl%d' % i, o, c, a, b, 2.08, H, M_WALL)
        wall_box('dlc%d' % i, o, c, a, b, H, H + 0.012, M_CAP, T + 0.004)
        L = M(b - a) - 0.02
        hpx = a if hg == 'a' else b; fr = b if hg == 'a' else a; dir_ = 1 if fr > hpx else -1
        leaf = box('leaf%d' % i, 0, -0.02, FL + 0.005, L, 0.02, 2.08, M_NAVYDOOR if main else M_WHITE, 0.004)
        hd = cyl('handle%d' % i, L - 0.08, 0.05, 1.0, 1.02, 0.012, M_CHROME, 16, 0)
        hd2 = cyl('handle%db' % i, L - 0.08, -0.05, 1.0, 1.02, 0.012, M_CHROME, 16, 0)
        piv = link(bpy.data.objects.new('dpiv%d' % i, None))
        for ob in (leaf, hd, hd2): ob.parent = piv
        # kapalı yön ve açılış yönü (dünya koordinatında)
        if o == 'h':
            piv.location = (X(hpx), Y(c), 0); closed = (dir_, 0); opn = (0, -s)
        else:
            piv.location = (X(c), Y(hpx), 0); closed = (0, -dir_); opn = (s, 0)
        ac = math.atan2(closed[1], closed[0]); ao = math.atan2(opn[1], opn[0]); da = (ao - ac + math.pi) % (2 * math.pi) - math.pi
        piv.rotation_euler[2] = ac + da * 0.92
        # kasa
        for side in (a, b):
            q = side
            wall_box('jamb%d' % i, o, c, q - 0.012 * PPM, q + 0.012 * PPM, FL, 2.12, M_WHITE, T + 0.03)

# ---------------- döşeme ve kaide ----------------
def build_floors():
    # kaide dairenin kendi dış hattını izler (L planlarda boş köşe kalmaz)
    for r in PLAN['rooms']:
        p = poly(r)
        poly_slab('plinth_' + r[0], offset_poly(p, 0.16 * PPM), -0.32, -0.02, M_PLINTH)
        poly_slab('plinthline_' + r[0], offset_poly(p, 0.164 * PPM), -0.36, -0.31, M_CAP)
    for r in PLAN['rooms']:
        poly_slab('screed_' + r[0], offset_poly(poly(r), 0.1 * PPM), -0.03, -0.005, simple('screed', '#E7E5E1', 0.9))
    for r in PLAN['rooms']:
        p = poly(r); w = max(q[0] for q in p) - min(q[0] for q in p); h = max(q[1] for q in p) - min(q[1] for q in p)
        if r[3] == 'wood':
            m = wood_floor('wood_' + r[0], 0.0 if w >= h else math.pi / 2)
        elif r[3] == 'balk':
            m = tile_floor('balk', '#B9B3AA', 0.6, '#8f8a83', 0.6, rect=True)
        elif r[0].startswith('mut'):
            m = tile_floor('kitchentile', '#ECE8E1', 0.6, '#d2cdc4', 0.18)
        elif r[0].startswith('gh') or r[0].startswith('kor'):
            m = tile_floor('halltile', '#E9E5DF', 0.8, '#cfcac2', 0.15)
        else:
            m = tile_floor('bathtile', '#DCD8D1', 0.3, '#f0eee9', 0.12, rect=True)
        poly_slab('floor_' + r[0], p, -0.008, FL, m)
        if r[3] != 'balk':
            # süpürgelik
            for i in range(len(p)):
                a, b = p[i], p[(i + 1) % len(p)]
                o = 'h' if a[1] == b[1] else 'v'
    # banyo duvar seramiği: banyo odalarının iç yüzlerine ince seramik kaplama
    for r in PLAN['rooms']:
        if r[3] != 'tile' or r[0].startswith(('mut', 'gh', 'kor')): continue
        p = poly(r); x1, x2 = min(q[0] for q in p), max(q[0] for q in p); y1, y2 = min(q[1] for q in p), max(q[1] for q in p)
        bt = tile_floor('bathwall', '#E9E6E0', 0.3, '#f6f4f0', 0.08, rect=True)
        e = 0.008; th = 0.01
        box('bw1', X(x1) + e, Y(y1) - e - th, FL, X(x2) - e, Y(y1) - e, 2.2, bt, 0)
        box('bw2', X(x1) + e, Y(y2) + e, FL, X(x2) - e, Y(y2) + e + th, 2.2, bt, 0)
        box('bw3', X(x1) + e, Y(y2) + e, FL, X(x1) + e + th, Y(y1) - e, 2.2, bt, 0)
        box('bw4', X(x2) - e - th, Y(y2) + e, FL, X(x2) - e, Y(y1) - e, 2.2, bt, 0)

# ---------------- mobilyalar ----------------
def rect_m(b):
    return X(b[0]), Y(b[3]), X(b[2]), Y(b[1])   # x1, y1(alt), x2, y2(üst)

def wall_side(b):
    """dolabın/ünitenin yaslandığı duvar: en yakın oda kenarı"""
    cxp, cyp = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    r = room_of(cxp, cyp)
    if not r: return 't'
    p = poly(r); xs_ = [q[0] for q in p]; ys_ = [q[1] for q in p]
    d = {'l': b[0] - min(xs_), 'r': max(xs_) - b[2], 't': b[1] - min(ys_), 'b': max(ys_) - b[3]}
    return min(d, key=d.get)

def bed(b, head, double):
    x1, y1, x2, y2 = rect_m(b)
    # yön: head = t/b/l/r (görsel koordinatlarında; t = -y görsel = +Y dünya)
    hd = {'t': (0, 1), 'b': (0, -1), 'l': (-1, 0), 'r': (1, 0)}[head]
    box('bedframe', x1, y1, 0.06, x2, y2, 0.3, M_OAK, 0.01)
    box('bedleg', x1 + 0.03, y1 + 0.03, 0, x2 - 0.03, y2 - 0.03, 0.06, M_BLACKM, 0.0)
    mt = 0.03
    box('mattress', x1 + mt, y1 + mt, 0.3, x2 - mt, y2 - mt, 0.5, M_LINEN, 0.05, 3)
    L = abs(y2 - y1) if hd[0] == 0 else abs(x2 - x1)
    # yorgan: baş ucundan %28 sonra
    k = 0.28
    if hd == (0, 1): dv = (x1 + 0.01, y1 - 0.02, x2 - 0.01, y2 - L * k)
    elif hd == (0, -1): dv = (x1 + 0.01, y1 + L * k, x2 - 0.01, y2 + 0.02)
    elif hd == (-1, 0): dv = (x1 + L * k, y1 + 0.01, x2 + 0.02, y2 - 0.01)
    else: dv = (x1 - 0.02, y1 + 0.01, x2 - L * k, y2 - 0.01)
    box('duvet', dv[0] - 0.02, dv[1] - 0.02 if hd[1] == 0 else dv[1], 0.42, dv[2] + 0.02, dv[3], 0.58, M_DUVET, 0.07, 4, 1)
    # ayak ucu şal
    tb = 0.38
    if hd == (0, 1): th = (x1 - 0.015, y1 + 0.12, x2 + 0.015, y1 + 0.12 + tb)
    elif hd == (0, -1): th = (x1 - 0.015, y2 - 0.12 - tb, x2 + 0.015, y2 - 0.12)
    elif hd == (-1, 0): th = (x2 - 0.12 - tb, y1 - 0.015, x2 - 0.12, y2 + 0.015)
    else: th = (x1 + 0.12, y1 - 0.015, x1 + 0.12 + tb, y2 + 0.015)
    box('throw', *th[:2], 0.5, *th[2:], 0.6, M_THROW, 0.04, 3, 1)
    # yastıklar
    n = 2 if double else 1
    W = abs(x2 - x1) if hd[0] == 0 else abs(y2 - y1)
    for i in range(n):
        off = (i - (n - 1) / 2) * W / n
        pw, pd = min(0.66, W / n * 0.86), 0.42
        if hd[0] == 0:
            cy = (y2 - 0.3) if hd[1] > 0 else (y1 + 0.3); cx = (x1 + x2) / 2 + off
            pillow('pil', cx, cy, 0.5, pw, pd, 0.16, M_LINEN)
            pillow('pil2', cx, cy - 0.12 * hd[1], 0.56, pw * 0.8, 0.3, 0.13, M_CUSH if double else M_CUSH2)
        else:
            cx = (x1 + 0.3) if hd[0] < 0 else (x2 - 0.3); cy = (y1 + y2) / 2 + off
            pillow('pil', cx, cy, 0.5, pd, pw, 0.16, M_LINEN)
            pillow('pil2', cx - 0.12 * hd[0], cy, 0.56, 0.3, pw * 0.8, 0.13, M_CUSH if double else M_CUSH2)
    # başlık (yastıklı)
    if hd == (0, 1): box('headboard', x1 - 0.04, y2, 0.2, x2 + 0.04, y2 + 0.09, 1.15, M_HEAD, 0.03, 3, 1)
    elif hd == (0, -1): box('headboard', x1 - 0.04, y1 - 0.09, 0.2, x2 + 0.04, y1, 1.15, M_HEAD, 0.03, 3, 1)
    elif hd == (-1, 0): box('headboard', x1 - 0.09, y1 - 0.04, 0.2, x1, y2 + 0.04, 1.15, M_HEAD, 0.03, 3, 1)
    else: box('headboard', x2, y1 - 0.04, 0.2, x2 + 0.09, y2 + 0.04, 1.15, M_HEAD, 0.03, 3, 1)

def sofa(b, back):
    x1, y1, x2, y2 = rect_m(b)
    bk = {'t': 'n', 'b': 's', 'l': 'w', 'r': 'e'}[back]
    box('sofabase', x1, y1, 0.08, x2, y2, 0.4, M_NAVYF, 0.03, 3)
    box('sofafeet', x1 + 0.05, y1 + 0.05, 0, x2 - 0.05, y2 - 0.05, 0.08, M_BLACKM, 0)
    dep = 0.22
    if bk == 'w': bx = (x1, y1, x1 + dep, y2); L = y2 - y1; along = 'y'
    elif bk == 'e': bx = (x2 - dep, y1, x2, y2); L = y2 - y1; along = 'y'
    elif bk == 's': bx = (x1, y1, x2, y1 + dep); L = x2 - x1; along = 'x'
    else: bx = (x1, y2 - dep, x2, y2); L = x2 - x1; along = 'x'
    box('sofaback', bx[0], bx[1], 0.35, bx[2], bx[3], 0.8, M_NAVYF, 0.08, 4, 1)
    n = max(1, round(L / 0.85)); seg = L / n
    for i in range(n):
        if along == 'y':
            a0 = y1 + seg * i + 0.02; a1 = y1 + seg * (i + 1) - 0.02
            sx1, sx2 = (x1 + dep, x2 - 0.02) if bk == 'w' else (x1 + 0.02, x2 - dep)
            box('seat', sx1, a0, 0.38, sx2, a1, 0.52, M_NAVYF, 0.06, 4, 1)
            cx = x1 + dep + 0.1 if bk == 'w' else x2 - dep - 0.1
            pillow('bc', cx, (a0 + a1) / 2, 0.5, 0.18, seg * 0.8, 0.42, M_NAVYF)
        else:
            a0 = x1 + seg * i + 0.02; a1 = x1 + seg * (i + 1) - 0.02
            sy1, sy2 = (y1 + dep, y2 - 0.02) if bk == 's' else (y1 + 0.02, y2 - dep)
            box('seat', a0, sy1, 0.38, a1, sy2, 0.52, M_NAVYF, 0.06, 4, 1)
            cy = y1 + dep + 0.1 if bk == 's' else y2 - dep - 0.1
            pillow('bc', (a0 + a1) / 2, cy, 0.5, seg * 0.8, 0.18, 0.42, M_NAVYF)
    # süs yastıkları
    if along == 'y':
        cx = x1 + dep + 0.15 if bk == 'w' else x2 - dep - 0.15
        pillow('dec', cx, y1 + 0.3, 0.55, 0.14, 0.42, 0.38, M_CUSH)
        pillow('dec', cx, y2 - 0.3, 0.55, 0.14, 0.42, 0.38, M_CUSH2)
    else:
        cy = y1 + dep + 0.15 if bk == 's' else y2 - dep - 0.15
        pillow('dec', x1 + 0.3, cy, 0.55, 0.42, 0.14, 0.38, M_CUSH)
        pillow('dec', x2 - 0.3, cy, 0.55, 0.42, 0.14, 0.38, M_CUSH2)

def table(b, chairs=True):
    x1, y1, x2, y2 = rect_m(b)
    box('ttop', x1, y1, 0.72, x2, y2, 0.76, M_OAK, 0.006)
    for lx, ly in ((x1 + 0.06, y1 + 0.06), (x2 - 0.06, y1 + 0.06), (x1 + 0.06, y2 - 0.06), (x2 - 0.06, y2 - 0.06)):
        box('tleg', lx - 0.025, ly - 0.025, 0, lx + 0.025, ly + 0.025, 0.72, M_BLACKM, 0.003)
    if not chairs: return
    w, d = x2 - x1, y2 - y1
    long_x = w >= d
    L = w if long_x else d
    n = max(1, int(L / 0.62))
    for side in (-1, 1):
        for i in range(n):
            t = (i + 0.5) / n
            if long_x: cx, cy, rot = x1 + w * t, (y1 - 0.22 if side < 0 else y2 + 0.22), (0 if side < 0 else math.pi)
            else: cx, cy, rot = (x1 - 0.22 if side < 0 else x2 + 0.22), y1 + d * t, (-math.pi / 2 if side < 0 else math.pi / 2)
            if room_of(*px_of(cx, cy)) is None: continue
            chair(cx, cy, rot)

def px_of(x, y): return x * PPM + CX, -y * PPM + CY

def chair(cx, cy, rot):
    g = link(bpy.data.objects.new('chair', None)); g.location = (cx, cy, 0); g.rotation_euler[2] = rot
    parts = [box('cs', -0.22, -0.22, 0.44, 0.22, 0.22, 0.49, M_CUSH2, 0.02, 3, 1),
             box('cb', -0.22, -0.26, 0.47, 0.22, -0.21, 0.88, M_CUSH2, 0.02, 3, 1)]
    for lx, ly in ((-0.19, -0.19), (0.19, -0.19), (-0.19, 0.19), (0.19, 0.19)):
        parts.append(box('cl', lx - 0.015, ly - 0.015, 0, lx + 0.015, ly + 0.015, 0.45, M_OAKD, 0.003))
    for p in parts: p.parent = g

def ctab(b):
    x1, y1, x2, y2 = rect_m(b); cx, cy, r = (x1 + x2) / 2, (y1 + y2) / 2, (x2 - x1) / 2
    cyl('ctop', cx, cy, 0.38, 0.42, r, M_MARBLE)
    cyl('cbase', cx, cy, 0, 0.38, r * 0.35, M_BLACKM)
    # dekor: kitap ve vazo
    box('book', cx - 0.12, cy - 0.08, 0.42, cx + 0.1, cy + 0.08, 0.45, simple('bookc', '#C64B45', 0.7), 0.003)
    cyl('vase', cx + 0.13, cy + 0.05, 0.42, 0.58, 0.05, M_CERAMIC)

def counter(b, side):
    x1, y1, x2, y2 = rect_m(b)
    box('cabbase', x1, y1, 0.1, x2, y2, 0.86, M_CAB, 0.004)
    box('toekick', x1 + 0.05, y1 + 0.05, 0, x2 - 0.05, y2 - 0.05, 0.1, M_BLACKM, 0)
    box('ctop', x1 - 0.01, y1 - 0.01, 0.86, x2 + 0.01, y2 + 0.01, 0.9, M_MARBLE, 0.004)
    long_x = (x2 - x1) >= (y2 - y1); L = (x2 - x1) if long_x else (y2 - y1)
    n = max(1, int(L / 0.6))
    for i in range(1, n):
        q = (x1 if long_x else y1) + L * i / n
        if long_x:
            yy = y1 - 0.002 if side == 't' else y2 + 0.002
            box('groove', q - 0.003, min(yy, yy + 0.004), 0.12, q + 0.003, max(yy, yy + 0.004), 0.84, M_BLACKM, 0)
        else:
            xx = x2 + 0.002 if side == 'l' else x1 - 0.004
            box('groove', xx, q - 0.003, 0.12, xx + 0.004, q + 0.003, 0.84, M_BLACKM, 0)
    if L > 1.5:
        # evye + ocak
        if long_x:
            cy = (y1 + y2) / 2
            box('sink', x1 + L * 0.3 - 0.3, cy - 0.2, 0.88, x1 + L * 0.3 + 0.3, cy + 0.2, 0.905, M_STEEL, 0.01)
            box('sinkin', x1 + L * 0.3 - 0.26, cy - 0.17, 0.75, x1 + L * 0.3 + 0.26, cy + 0.17, 0.906, simple('sinkdark', '#5c6066', 0.3, metal=1.0), 0.02)
            cyl('tap', x1 + L * 0.3, cy + 0.22 * (1 if side == 't' else -1), 0.9, 1.15, 0.015, M_CHROME, 16, 0)
            box('hob', x1 + L * 0.72 - 0.3, cy - 0.26, 0.9, x1 + L * 0.72 + 0.3, cy + 0.26, 0.906, M_BLACKG, 0.004)
            for dx in (-0.14, 0.14):
                for dy in (-0.1, 0.1):
                    cyl('ring', x1 + L * 0.72 + dx, cy + dy, 0.906, 0.907, 0.08, simple('ringc', '#2a2c33', 0.4), 32, 0)
        else:
            cx = (x1 + x2) / 2
            box('sink', cx - 0.2, y1 + L * 0.5 - 0.3, 0.88, cx + 0.2, y1 + L * 0.5 + 0.3, 0.905, M_STEEL, 0.01)
    # üst dolaplar
    if long_x:
        if side == 't': box('upper', x1, y2 - 0.35, 1.45, x2, y2, 2.15, M_CAB, 0.004)
        elif side == 'b': box('upper', x1, y1, 1.5, x2, y1 + 0.35, 2.15, M_CAB, 0.004)
    else:
        if side == 'l': box('upper', x1, y1, 1.5, x1 + 0.35, y2, 2.15, M_CAB, 0.004)
        elif side == 'r': box('upper', x2 - 0.35, y1, 1.5, x2, y2, 2.15, M_CAB, 0.004)

def fridge(b):
    x1, y1, x2, y2 = rect_m(b)
    box('fridge', x1, y1, 0, x2, y2, 2.0, M_STEEL, 0.01)

def ward(b, side):
    x1, y1, x2, y2 = rect_m(b)
    box('ward', x1, y1, 0, x2, y2, 2.15, M_MATTE, 0.004)
    long_x = (x2 - x1) >= (y2 - y1); L = (x2 - x1) if long_x else (y2 - y1)
    n = max(1, round(L / 0.5))
    for i in range(n):
        q0 = (x1 if long_x else y1) + L * i / n; q1 = q0 + L / n
        if long_x:
            yy = y1 - 0.004 if side == 't' else y2
            box('wd', q0 + 0.003, yy, 0.02, q1 - 0.003, yy + 0.004, 2.13, M_MATTE, 0.002)
            hx = q1 - 0.05 if i % 2 == 0 else q0 + 0.05
            box('wh', hx - 0.006, yy - 0.025 if side == 't' else yy + 0.004, 0.9, hx + 0.006, yy if side == 't' else yy + 0.03, 1.4, M_BLACKM, 0.003)
        else:
            xx = x2 if side == 'l' else x1 - 0.004
            box('wd', xx, q0 + 0.003, 0.02, xx + 0.004, q1 - 0.003, 2.23, M_MATTE, 0.002)
            hy = q1 - 0.05 if i % 2 == 0 else q0 + 0.05
            box('wh', xx + 0.004 if side == 'l' else xx - 0.025, hy - 0.006, 0.9, xx + 0.03 if side == 'l' else xx, hy + 0.006, 1.4, M_BLACKM, 0.003)

def wc(b, side):
    x1, y1, x2, y2 = rect_m(b); cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    d = {'t': (0, 1), 'b': (0, -1), 'l': (-1, 0), 'r': (1, 0)}[side]
    wx, wy = cx + d[0] * 0.25, cy + d[1] * 0.25
    # duvara asma klozet + rezervuar paneli
    if d[0] == 0: box('tank', cx - 0.22, wy - 0.06 if d[1] > 0 else wy - 0.02, 0, cx + 0.22, wy + 0.02 if d[1] > 0 else wy + 0.06, 1.1, M_CERAMIC, 0.01)
    else: box('tank', wx - 0.06 if d[0] > 0 else wx - 0.02, cy - 0.22, 0, wx + 0.02 if d[0] > 0 else wx + 0.06, cy + 0.22, 1.1, M_CERAMIC, 0.01)
    bx, by = cx - d[0] * 0.02, cy - d[1] * 0.02
    o = cyl('bowl', bx, by, 0.28, 0.42, 0.19, M_CERAMIC, 48, 0.02)
    o.scale = (1.0 if d[0] == 0 else 1.45, 1.45 if d[0] == 0 else 1.0, 1)
    o2 = cyl('seat', bx, by, 0.42, 0.44, 0.19, M_CERAMIC, 48, 0.01); o2.scale = o.scale
    pb = box('flush', wx - 0.08 if d[0] == 0 else wx - d[0] * 0.03 - 0.005, wy - 0.005 if d[0] == 0 else wy - 0.08, 0.95, wx + 0.08 if d[0] == 0 else wx - d[0] * 0.03 + 0.005, wy + 0.005 if d[0] == 0 else wy + 0.08, 1.05, M_CHROME, 0.003)

def sink(b, side):
    x1, y1, x2, y2 = rect_m(b); cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    w = max(x2 - x1, y2 - y1); d = {'t': (0, 1), 'b': (0, -1), 'l': (-1, 0), 'r': (1, 0)}[side]
    W, D = max(0.6, w), 0.46
    if d[0] == 0:
        y_wall = cy + d[1] * (abs(y2 - y1) / 2 + 0.02); ya, yb = sorted((y_wall, y_wall - d[1] * D))
        box('vanity', cx - W / 2, ya, 0.45, cx + W / 2, yb, 0.82, M_OAK, 0.006)
        box('vtop', cx - W / 2, ya, 0.82, cx + W / 2, yb, 0.85, M_CERAMIC, 0.006)
        o = cyl('basin', cx, (ya + yb) / 2, 0.85, 0.97, 0.19, M_CERAMIC, 48, 0.02); o.scale = (1.3, 1, 1)
        cyl('tap', cx, y_wall - d[1] * 0.05, 0.85, 1.12, 0.012, M_CHROME, 16, 0)
        box('mirror', cx - W / 2 + 0.05, y_wall - 0.012 if d[1] > 0 else y_wall, 1.1, cx + W / 2 - 0.05, y_wall if d[1] > 0 else y_wall + 0.012, 1.9, M_CHROME, 0.004)
    else:
        x_wall = cx + d[0] * (abs(x2 - x1) / 2 + 0.02); xa, xb = sorted((x_wall, x_wall - d[0] * D))
        box('vanity', xa, cy - W / 2, 0.45, xb, cy + W / 2, 0.82, M_OAK, 0.006)
        box('vtop', xa, cy - W / 2, 0.82, xb, cy + W / 2, 0.85, M_CERAMIC, 0.006)
        o = cyl('basin', (xa + xb) / 2, cy, 0.85, 0.97, 0.19, M_CERAMIC, 48, 0.02); o.scale = (1, 1.3, 1)
        cyl('tap', x_wall - d[0] * 0.05, cy, 0.85, 1.12, 0.012, M_CHROME, 16, 0)
        box('mirror', x_wall - 0.012 if d[0] > 0 else x_wall, cy - W / 2 + 0.05, 1.1, x_wall if d[0] > 0 else x_wall + 0.012, cy + W / 2 - 0.05, 1.9, M_CHROME, 0.004)

def shower(b):
    x1, y1, x2, y2 = rect_m(b)
    box('tray', x1 + 0.01, y1 + 0.01, 0, x2 - 0.01, y2 - 0.01, 0.04, M_CERAMIC, 0.008)
    box('drain', (x1 + x2) / 2 - 0.05, (y1 + y2) / 2 - 0.05, 0.04, (x1 + x2) / 2 + 0.05, (y1 + y2) / 2 + 0.05, 0.042, M_CHROME, 0)
    r = room_of(*px_of((x1 + x2) / 2, (y1 + y2) / 2)); p = poly(r)
    rx1, rx2 = X(min(q[0] for q in p)), X(max(q[0] for q in p)); ry1, ry2 = Y(max(q[1] for q in p)), Y(min(q[1] for q in p))
    tol = 0.12
    if abs(x1 - rx1) > tol: box('sg', x1, y1, 0.04, x1 + 0.01, y2, 2.0, M_GLASS, 0)
    if abs(x2 - rx2) > tol: box('sg', x2 - 0.01, y1, 0.04, x2, y2, 2.0, M_GLASS, 0)
    if abs(y1 - ry1) > tol: box('sg', x1, y1, 0.04, x2, y1 + 0.01, 2.0, M_GLASS, 0)
    if abs(y2 - ry2) > tol: box('sg', x1, y2 - 0.01, 0.04, x2, y2, 2.0, M_GLASS, 0)
    cyl('head', (x1 + x2) / 2, (y1 + y2) / 2, 2.05, 2.07, 0.12, M_CHROME, 32, 0)

def bath(b):
    # küvet: akrilik gövde, içi oyuk
    x1, y1, x2, y2 = rect_m(b)
    t = box('tub', x1 + 0.01, y1 + 0.01, 0, x2 - 0.01, y2 - 0.01, 0.55, M_CERAMIC, 0.02)
    o = box('tubin', x1 + 0.08, y1 + 0.08, 0.2, x2 - 0.08, y2 - 0.08, 0.7, M_CERAMIC, 0.06, 3)
    o.hide_render = True; o.hide_viewport = True
    mod = t.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = o
    long_x = (x2 - x1) >= (y2 - y1)
    if long_x: cyl('tubtap', x1 + 0.06, (y1 + y2) / 2, 0.55, 0.75, 0.014, M_CHROME, 16, 0)
    else: cyl('tubtap', (x1 + x2) / 2, y2 - 0.06, 0.55, 0.75, 0.014, M_CHROME, 16, 0)

def tv(b, side):
    x1, y1, x2, y2 = rect_m(b); long_x = (x2 - x1) >= (y2 - y1)
    if long_x:
        L = x2 - x1; yw = y2 if side == 't' else y1; s = -1 if side == 't' else 1
        ya, yb = sorted((yw, yw + s * 0.42))
        box('tvunit', x1 - 0.2, ya, 0.18, x2 + 0.2, yb, 0.5, M_OAK, 0.006)
        ya2, yb2 = sorted((yw + s * 0.02, yw + s * 0.05))
        box('tv', (x1 + x2) / 2 - 0.62, ya2, 0.9, (x1 + x2) / 2 + 0.62, yb2, 1.62, M_SCREEN, 0.004)
    else:
        L = y2 - y1; xw = x2 if side == 'r' else x1; s = -1 if side == 'r' else 1
        xa, xb = sorted((xw, xw + s * 0.42))
        box('tvunit', xa, y1 - 0.1, 0.18, xb, y2 + 0.1, 0.5, M_OAK, 0.006)
        xa2, xb2 = sorted((xw + s * 0.02, xw + s * 0.05))
        tw = min(0.62, L / 2 + 0.1)
        box('tv', xa2, (y1 + y2) / 2 - tw, 0.9, xb2, (y1 + y2) / 2 + tw, 1.62 - (0.62 - tw) * 0.6, M_SCREEN, 0.004)

def wm(b):
    x1, y1, x2, y2 = rect_m(b); cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    box('wm', x1, y1, 0, x2, y2, 0.85, M_WHITE, 0.02)

def rug(b):
    x1, y1, x2, y2 = rect_m(b)
    box('rugb', x1, y1, 0, x2, y2, 0.010, M_RUGB, 0.003)
    box('rug', x1 + 0.08, y1 + 0.08, 0.002, x2 - 0.08, y2 - 0.08, 0.013, M_RUG, 0.003)

def desk(b):
    x1, y1, x2, y2 = rect_m(b)
    box('desk', x1, y1, 0.72, x2, y2, 0.75, M_OAK, 0.004)
    box('dleg1', x1 + 0.02, y1 + 0.02, 0, x1 + 0.05, y2 - 0.02, 0.72, M_WHITE, 0.003)
    box('dleg2', x2 - 0.05, y1 + 0.02, 0, x2 - 0.02, y2 - 0.02, 0.72, M_WHITE, 0.003)
    box('laptop', (x1 + x2) / 2 - 0.16, (y1 + y2) / 2 - 0.11, 0.75, (x1 + x2) / 2 + 0.16, (y1 + y2) / 2 + 0.11, 0.765, simple('alu', '#B8BCC2', 0.3, metal=1.0), 0.004)

def armchair(cx, cy, rot, scale=1.0):
    r = import_glb('SheenChair.glb', keep=['fabric', 'wood', 'metal'])
    r.location = (cx, cy, 0); r.rotation_euler = (0, 0, rot); r.scale = (scale,) * 3

def plant(cx, cy, scale=1.5):
    r = import_glb('DiffuseTransmissionPlant.glb', keep=['pot', 'leaves', 'dirt'])
    r.location = (cx, cy, 0); r.rotation_euler = (0, 0, random.random() * 6.28); r.scale = (scale,) * 3

def build_furniture():
    for f in PLAN['furn']:
        k, b = f[0], f[1]; o = f[2] if len(f) > 2 else None
        side = EXTRA.get('side', {}).get(str(b), None) or wall_side(b)
        if k == 'bed2': bed(b, o, True)
        elif k == 'bed1': bed(b, o, False)
        elif k == 'sofa': sofa(b, o)
        elif k == 'table': table(b, True)
        elif k == 'desk': desk(b)
        elif k == 'ctab': ctab(b)
        elif k == 'counter': counter(b, side)
        elif k == 'fridge': fridge(b)
        elif k == 'ward': ward(b, side)
        elif k == 'wc': wc(b, side)
        elif k == 'sink': sink(b, side)
        elif k == 'shower': shower(b)
        elif k == 'bath': bath(b)
        elif k == 'tv': tv(b, side)
        elif k == 'wm': wm(b)
        elif k == 'rug': rug(b)
        elif k == 'chair':
            x1, y1, x2, y2 = rect_m(b); armchair((x1 + x2) / 2, (y1 + y2) / 2, EXTRA.get('chairrot', 0), 0.8)
    for p in EXTRA.get('plants', []):
        plant(X(p[0]), Y(p[1]), p[2] if len(p) > 2 else 1.5)
    for a in EXTRA.get('armchairs', []):
        armchair(X(a[0]), Y(a[1]), math.radians(a[2]), a[3] if len(a) > 3 else 1.0)
    for d in EXTRA.get('desks_chairs', []):
        chair(X(d[0]), Y(d[1]), math.radians(d[2]))

# ---------------- ışık ve render ----------------
def setup_world():
    w = bpy.data.worlds.new('sky'); S.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    try: sky.sky_type = 'NISHITA'
    except Exception: pass
    try:
        sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(215); sky.sun_size = math.radians(3.0)
    except Exception: pass
    bg.inputs['Strength'].default_value = 0.08
    nt.links.new(sky.outputs[0], bg.inputs[0])
    # yansımalarda karanlık gökyüzü yerine aydınlık stüdyo ortamı (cam ve seramikler kararmasın)
    lp = nt.nodes.new('ShaderNodeLightPath'); st = nt.nodes.new('ShaderNodeBackground')
    st.inputs[0].default_value = (0.86, 0.88, 0.92, 1); st.inputs['Strength'].default_value = 0.85
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Glossy Ray'], mx.inputs[0]); nt.links.new(bg.outputs[0], mx.inputs[1]); nt.links.new(st.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    # güneş
    sd = bpy.data.lights.new('sun', 'SUN'); sd.energy = 3.4; sd.angle = math.radians(4.0); sd.color = (1.0, 0.96, 0.9)
    so = bpy.data.objects.new('sun', sd); S.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(0), math.radians(-40))
    # tavan yumuşak alan ışığı (dolgu)
    ad = bpy.data.lights.new('fill', 'AREA'); ad.energy = 120; ad.size = max(SX, SY) * 1.4; ad.color = (0.95, 0.97, 1.0)
    ao = bpy.data.objects.new('fill', ad); S.collection.objects.link(ao); ao.location = (0, 0, 9)
    # gölge yakalayıcı zemin
    me = bpy.data.meshes.new('ground'); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60); bm.to_mesh(me); bm.free()
    g = bpy.data.objects.new('ground', me); S.collection.objects.link(g); g.location = (0, 0, -0.36); g.is_shadow_catcher = True

def setup_render(res_x, res_y, samples):
    S.render.engine = 'CYCLES'
    c = S.cycles; c.device = 'CPU'; c.samples = samples; c.use_denoising = True; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    c.max_bounces = 6; c.diffuse_bounces = 3; c.glossy_bounces = 3; c.transmission_bounces = 6; c.transparent_max_bounces = 8
    c.caustics_reflective = False; c.caustics_refractive = False; c.blur_glossy = 1.0
    S.render.film_transparent = True
    S.render.resolution_x = res_x; S.render.resolution_y = res_y; S.render.resolution_percentage = 100
    S.view_settings.view_transform = 'AgX'
    try: S.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    S.view_settings.exposure = -0.4
    S.render.image_settings.file_format = 'PNG'; S.render.image_settings.color_mode = 'RGBA'
    try: c.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass

def camera_persp(az_deg, el_deg, aspect):
    cd = bpy.data.cameras.new('cam'); cd.lens = 50; cd.sensor_width = 36
    co = bpy.data.objects.new('cam', cd); S.collection.objects.link(co); S.camera = co
    span = max(SX, SY) + 1.2
    # yeterli mesafe: plan köşegeni görüş alanına sığsın
    fov_h = 2 * math.atan(18 / cd.lens)
    fov = fov_h if aspect >= 1 else 2 * math.atan(math.tan(fov_h / 2) * aspect)
    diag = math.hypot(SX, SY) + 1.0
    dist = diag / 2 / math.tan(fov / 2) * 0.76
    if aspect >= 1:
        fov_v = 2 * math.atan(math.tan(fov_h / 2) / aspect)
        dist = max(dist * 0.86, (diag * math.sin(math.radians(el_deg)) * 0.62 + 1.2) / 2 / math.tan(fov_v / 2) * 1.6)
    az, el = math.radians(az_deg), math.radians(el_deg)
    co.location = (dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el) + 0.6)
    tgt = Vector((0, 0, 0.6))
    co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
    return co

def camera_top(res_x, res_y):
    cd = bpy.data.cameras.new('camtop'); cd.type = 'ORTHO'; cd.sensor_fit = 'HORIZONTAL'
    pad = 0.9
    w, h = SX + pad, SY + pad
    cd.ortho_scale = w
    co = bpy.data.objects.new('camtop', cd); S.collection.objects.link(co); S.camera = co
    co.location = (0, 0, 20); co.rotation_euler = (0, 0, 0)
    return co

def labels_for(cam):
    bpy.context.view_layer.update()
    out = {}
    for r in PLAN['rooms']:
        c = r[5] if len(r) > 5 else None
        if not c:
            p = poly(r); c = [sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)]
        v = world_to_camera_view(S, cam, Vector((X(c[0]), Y(c[1]), 0.15)))
        out[r[0]] = [round(v.x, 4), round(1 - v.y, 4)]
    return out

build_floors(); build_walls(); build_furniture(); setup_world()

if MODE == 'top':
    outp, res = os.path.abspath(args[2]), int(args[3])
    rx = res; ry = int(res * (SY + 0.9) / (SX + 0.9)) if SY > SX else int(res * 0.75)
    ry = int(res * (SY + 0.9) / (SX + 0.9))
    setup_render(rx, ry, int(args[4]) if len(args) > 4 else 96)
    cam = camera_top(rx, ry)
    g = bpy.data.objects.get('ground')
    if g: g.hide_render = True
    # tepeden görünümde tavan kenarındaki kapakları gizlemeye gerek yok
    S.render.filepath = outp; bpy.ops.render.render(write_still=True)
    # oda poligonlarını görüntü koordinatına dönüştür
    polys = {}
    for r in PLAN['rooms']:
        polys[r[0]] = [[round(world_to_camera_view(S, cam, Vector((X(q[0]), Y(q[1]), 0))).x, 4), round(1 - world_to_camera_view(S, cam, Vector((X(q[0]), Y(q[1]), 0))).y, 4)] for q in poly(r)]
    json.dump({'w': rx, 'h': ry, 'labels': labels_for(cam), 'polys': polys}, open(outp + '.json', 'w'))
elif MODE == 'test':
    outp, res, az = os.path.abspath(args[2]), int(args[3]), float(args[4])
    el = float(args[5]) if len(args) > 5 else 50
    samples = int(args[6]) if len(args) > 6 else 64
    rx, ry = res, int(res * 0.75)
    setup_render(rx, ry, samples)
    cam = camera_persp(az, el, rx / ry)
    S.render.filepath = outp; bpy.ops.render.render(write_still=True)
    json.dump({'labels': labels_for(cam)}, open(outp + '.json', 'w'))
elif MODE == 'spin':
    outd, n, res = os.path.abspath(args[2]), int(args[3]), int(args[4])
    samples = int(args[5]) if len(args) > 5 else 64
    el = float(args[6]) if len(args) > 6 else 48
    start = int(args[7]) if len(args) > 7 else 0
    os.makedirs(outd, exist_ok=True)
    rx, ry = res, int(res * 0.75)
    setup_render(rx, ry, samples)
    meta = {}
    az0 = EXTRA.get('az0', -60)
    cam = camera_persp(az0, el, rx / ry)
    for i in range(start, n):
        az = az0 + 360 * i / n
        S.collection.objects.unlink(cam); bpy.data.objects.remove(cam)
        cam = camera_persp(az, el, rx / ry)
        fp = os.path.join(outd, 'f%02d.png' % i)
        if not os.path.exists(fp):
            S.render.filepath = fp; bpy.ops.render.render(write_still=True)
        meta[i] = labels_for(cam)
        json.dump(meta, open(os.path.join(outd, 'labels_%d.json' % start), 'w'))
