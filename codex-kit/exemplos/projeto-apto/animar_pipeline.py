#!/usr/bin/env python3
"""Vídeo do pipeline: planta 2D -> mobília -> maquete 3D sobe e gira -> render Cycles.

Mesma cena do render_blender.py (Blender como biblioteca: pip install bpy numpy pillow imageio-ffmpeg).
  1) quadros da maquete:  python animar_pipeline.py m 100 299
  2) quadros do Cycles:   python animar_pipeline.py r 240 372     (~13 s/quadro no CPU)
  3) montar o vídeo:      python animar_pipeline.py video
Quadros em saida/animacao/ (ignorados pelo git; quadro já existente é pulado, dá para retomar).
Vídeo final em ../../../demos/demo-pipeline-planta-para-render.mp4. Dados fictícios.
"""
import math, sys, time
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import bpy
import render_blender as rb

OUT = AQUI / "saida" / "animacao"
OUT.mkdir(parents=True, exist_ok=True)
W, Hh = 1280, 720
FPS = 20

# ---------------------------------------------------------------- linha do tempo
F_RISE0, F_RISE1 = 100, 165      # paredes e móveis sobem
F_CAM0, F_END = 112, 372         # câmera começa a inclinar / para
TGT0, TGT1 = (5.35, 2.8, 0.0), (5.0, 3.1, 0.5)
D0, D1 = 28.7, 21.5
TILT1 = math.radians(56)
PSI1 = math.radians(40.6 + 360)


def sm(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def cam_params(f):
    u = (f - F_CAM0) / (F_END - F_CAM0)
    tilt = TILT1 * sm(F_CAM0, F_CAM0 + 110, f)
    # rotação: começa devagar, termina com frenagem suave
    if u <= 0:
        psi = 0.0
    elif u >= 1:
        psi = PSI1
    else:
        a = 0.18  # fração de aceleração / frenagem
        vmax = 1 / (1 - a)
        if u < a:
            s = vmax * u * u / (2 * a)
        elif u > 1 - a:
            s = 1 - vmax * (1 - u) ** 2 / (2 * a)
        else:
            s = vmax * (u - a / 2)
        psi = PSI1 * s
    k = sm(F_CAM0, F_CAM0 + 130, f)
    tgt = [TGT0[i] + (TGT1[i] - TGT0[i]) * k for i in range(3)]
    d = D0 + (D1 - D0) * k + 9.0 * math.sin(math.pi * k)
    return tilt, psi, tgt, d


# ---------------------------------------------------------------- cena
rb.limpar()
P = rb.paleta()
rb.construir_arquitetura(P, None, com_teto=False)
for mv in rb.LAYOUT["moveis"]:
    rb.build_movel(P, mv)
rb.iluminacao(P, "aerea")
sc = bpy.context.scene
# troca o terreno grande por um lote neutro (fundo transparente em volta)
bpy.data.objects.remove(bpy.data.objects["terreno"], do_unlink=True)
rb.caixa(None, -1.4, -3.2, -0.52, 11.6, 9.4, -0.44, rb.mat("lote", "#dcd6ca", 0.95), 0.01, nome="terreno")

cd = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cd)
rb.COL.objects.link(cam)
sc.camera = cam
cd.sensor_fit = "VERTICAL"
cd.sensor_height = 24
cd.lens = 50
cd.clip_end = 200

# objetos que "sobem"
fixos = ("laje", "terreno", "piso_")
sobe_arq, sobe_mov = [], []
for ob in bpy.data.objects:
    if ob.parent is not None or ob.type in ("CAMERA", "LIGHT") or ob.name.startswith(fixos):
        continue
    if ob.type == "EMPTY":
        sobe_mov.append((ob, ob.location.z))
    else:
        sobe_arq.append(ob)
xs = [o.location.x + o.location.y * 0.4 for o, _ in sobe_mov]
xmin, xmax = min(xs), max(xs)


def aplicar_subida(f):
    s = sm(F_RISE0, F_RISE0 + 45, f)
    for ob in sobe_arq:
        ob.scale.z = max(s, 0.002)
    for (ob, z0), x in zip(sobe_mov, xs):
        a = F_RISE0 + 12 + 30 * (x - xmin) / (xmax - xmin)
        t = sm(a, a + 22, f)
        ob.scale.z = max(t, 0.002)
        ob.location.z = z0 * t


def aplicar_camera(f):
    tilt, psi, tgt, d = cam_params(f)
    ox, oy, oz = 0.0, -d * math.sin(tilt), d * math.cos(tilt)
    cx = ox * math.cos(psi) - oy * math.sin(psi)
    cy = ox * math.sin(psi) + oy * math.cos(psi)
    cam.location = (tgt[0] + cx, tgt[1] + cy, tgt[2] + oz)
    cam.rotation_euler = (tilt, 0.0, psi)


# ---------------------------------------------------------------- looks
def cor_base(m):
    if not m.use_nodes:
        return (0.8, 0.8, 0.8, 1)
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            i = n.inputs["Base Color"]
            if not i.is_linked:
                return tuple(i.default_value)
    for n in m.node_tree.nodes:   # pisos texturizados: pega a primeira cor de rampa/mistura
        if n.type in ("VALTORGB",):
            return tuple(n.color_ramp.elements[0].color)
        if n.type == "MIX" and not n.inputs[6].is_linked:
            return tuple(n.inputs[6].default_value)
        if n.type == "RGB":
            return tuple(n.outputs[0].default_value)
    return (0.6, 0.55, 0.5, 1)


MAQ = {}


def maquete(m):
    if m.name in MAQ:
        return MAQ[m.name]
    if m.name.startswith("vidro"):
        MAQ[m.name] = m
        return m
    c = cor_base(m)
    nm = bpy.data.materials.new("maq_" + m.name)
    nm.use_nodes = True
    b = nm.node_tree.nodes["Principled BSDF"]
    # cores de maquete: mais claras e um pouco dessaturadas
    l = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    cc = [0.88 * (c[i] * 0.8 + l * 0.2) + 0.12 * 0.8 for i in range(3)]
    if m.name in ("tinta", "teto"):
        cc = [0.70, 0.69, 0.66]
    b.inputs["Base Color"].default_value = (*cc, 1)
    b.inputs["Roughness"].default_value = 0.95
    MAQ[m.name] = nm
    return nm


ORIG = {}
for ob in bpy.data.objects:
    if ob.type == "MESH":
        ORIG[ob.name] = [s.material for s in ob.material_slots]


def look(qual):
    for ob in bpy.data.objects:
        if ob.type != "MESH":
            continue
        for s, m in zip(ob.material_slots, ORIG[ob.name]):
            if m is None:
                continue
            s.material = m if qual == "r" else maquete(m)
    sol = bpy.data.objects["sol"].data
    bg = sc.world.node_tree.nodes["Background"]
    cy = sc.cycles
    if qual == "m":
        sol.energy, sol.angle = 1.6, math.radians(12)
        bg.inputs["Strength"].default_value = 0.85
        cy.samples, cy.adaptive_threshold = 10, 0.05
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 3, 2, 1
        sc.view_settings.exposure = -0.2
    else:
        sol.energy, sol.angle = 2.6, math.radians(1.6)
        bg.inputs["Strength"].default_value = 0.9
        cy.samples, cy.adaptive_threshold = 28, 0.03
        cy.max_bounces, cy.diffuse_bounces, cy.glossy_bounces = 8, 4, 4
        sc.view_settings.exposure = -0.25


sc.render.engine = "CYCLES"
cy = sc.cycles
cy.device = "CPU"
cy.use_adaptive_sampling = True
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.transmission_bounces = 6
cy.caustics_reflective = cy.caustics_refractive = False
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, Hh, 100
sc.render.film_transparent = True
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "AgX"
sc.render.use_persistent_data = True


# ---------------------------------------------------------------- montagem do vídeo (2D + quadros)
import numpy as np
import imageio_ffmpeg
from PIL import Image

BG = (247, 246, 242)
N = 420                       # 21 s a 20 qps (últimos quadros seguram a imagem final)
ppm = Hh / (D0 * 24 / 50)     # px por metro na vista de cima inicial
base0 = Image.open(AQUI / "saida" / "planta-base.png").convert("RGB")
mob0 = Image.open(AQUI / "saida" / "planta-mobiliada.png").convert("RGB")

BG = (247, 246, 242)
N = 420




def plano(f):
    """planta 2D (base -> mobiliada com varredura suave), com leve zoom que termina alinhado ao 3D."""
    k = 1.06 - 0.06 * sm(0, 100, f)
    sc = ppm / 100 * k
    pw, ph = round(1330 * sc), round(1300 * sc)
    b = base0.resize((pw, ph), Image.LANCZOS)
    m = mob0.resize((pw, ph), Image.LANCZOS)
    t = sm(40, 82, f)
    if t <= 0:
        img = b
    elif t >= 1:
        img = m
    else:  # varredura diagonal suave (noroeste -> sudeste)
        yy, xx = np.mgrid[0:ph, 0:pw]
        g = (xx / pw * 0.6 + yy / ph * 0.4)
        edge = t * 1.3 - 0.15
        a = np.clip((edge - g) / 0.15, 0, 1)[..., None]
        img = Image.fromarray((np.asarray(b) * (1 - a) + np.asarray(m) * a).astype(np.uint8))
    can = Image.new("RGB", (W, Hh), BG)
    can.paste(img, ((W - pw) // 2, (Hh - ph) // 2))
    return can


def render(path):
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", (W, Hh), BG + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def frame(f):
    if f < 100:
        out = np.asarray(plano(f), dtype=np.float32)
    elif f < 240:
        out = np.asarray(render(str(OUT) + f"/m_{f:04d}.png"), dtype=np.float32)
        a = 1 - sm(100, 120, f)
        if a > 0:
            out = out * (1 - a) + np.asarray(plano(100), dtype=np.float32) * a
    elif f < 300:
        m = np.asarray(render(str(OUT) + f"/m_{f:04d}.png"), dtype=np.float32)
        r = np.asarray(render(str(OUT) + f"/r_{f:04d}.png"), dtype=np.float32)
        a = sm(240, 300, f)
        out = m * (1 - a) + r * a
    else:
        out = np.asarray(render(str(OUT) + f"/r_{min(f, 372):04d}.png"), dtype=np.float32)
    if f < 6:  # entrada suave
        out = np.array(BG, np.float32) * (1 - f / 6) + out * (f / 6)
    return out.clip(0, 255).astype(np.uint8)



def montar_video():
    w = imageio_ffmpeg.write_frames(str(AQUI.parents[2] / "demos" / "demo-pipeline-planta-para-render.mp4"), (W, Hh), fps=FPS,
                                    codec="libx264", pix_fmt_out="yuv420p", quality=None,
                                    output_params=["-crf", "20", "-preset", "slow", "-movflags", "+faststart"])
    w.send(None)
    for f in range(N):
        fr = frame(f)
        w.send(fr.tobytes())
    w.close()
    print("ok")


if __name__ == "__main__":
    if sys.argv[1] == "video":
        montar_video()
        sys.exit()
    qual, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    passo = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    look(qual)
    for f in range(f0, f1 + 1, passo):
        p = OUT / f"{qual}_{f:04d}.png"
        if p.exists():
            continue
        t = time.time()
        aplicar_subida(f)
        aplicar_camera(f)
        sc.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)
        print(f"frame {qual} {f} {time.time() - t:.1f}s", flush=True)
