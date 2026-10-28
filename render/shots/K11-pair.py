"""K11-pair: the VanQuish set of two. Two identical canonical rackets (shots/kq_canon.py) of one feel (--weave command
= K04/K10's baked 3K twill, 2.6 mm tows; --weave pace = 12K spread tow, 8 mm tapes), presented as a matched, numbered
pair: parallel, both at the same 3/4 face, the second one a step behind (7 cm along the face normal), 19 cm along the
face to the right and 3.5 cm up, fanned like two cards. One continuous graphite studio (camera-only backdrop: graphite
edges, a soft halo peaking behind the heads' centre, no seam) and one neutral (6500 K) light family shared by both
rackets: ONE hard-edged band card in the faces' mirror direction. Parallel faces mirror the same card, so a single
light blade (crisp lower edge with a hot line, short upper fall-off) crosses the front face and continues across the
rear one; the card falls off from the front face's mirror point to the rear's (DEPTH_R), so the stripe peaks on the
front racket and the rear one sits a step back in the light. Also shared: an overhead key slit, an off-specular weave
card (twill / spread-tow shimmer, same depth fall-off), a top-edge card (white hairlines on both top curves), a rim
card behind-right whose lower part fades out (one neutral hairline on each head's upper right curve, gone before the
throat shoulder; it was ember red until 2026-10-23, RIM_EMBER), a cool rim on the near edges, a wall card (graded highlight on the visible left wall), a near-camera
bore lamp (one thin crescent on each hole's gloss lip; the carbon-lined bores darken with depth, so the holes read as
through-holes), grip strips (the rear one dimmer) and a small cap softbox per racket (the satin cap's groove and K).

Canonical racket (2026-10-22): 455.0 mm, crown of 8 + 34 holes, one-piece neck into the neutral-black helical overgrip,
satin anodised cap with a groove and an engraved Q (the company logo), the weave folding over the 1.5 mm edge onto the
side wall under the same gloss (no plain-lacquer edge any more), KINETIQ / SWISS MADE laser-frosted on the side walls.
Command is WHITE 3K twill (owner, 2026-10-22; kq_canon mat_white, k04_tex2 maps, 2.6 mm tows; --set WHITE=0 gives the
previous black). White needs real diffuse light (canon lighting note 8): one soft spot pool per racket from the front
face's upper left (16 deg, the rear's at W_POOL_REAR and unshadowed by the front), a weak fill, the black-carbon cards
graded down (W_* multipliers: the band stays as one sheen blade, the weave card and the throat rake are off); the
set-number frost is graphite on white. Pace keeps the black-carbon studio exactly. Pace is the
canon 12K (anisotropy 0.65, organic tape variation, K11's 30 % coat flip): the old aniso 0.9 read as a flat
checkerboard at card size.
Throat mark (owner override, 2026-10-22, RENDER_NOTES.md): the pair edition is numbered; BOTH rackets carry the set
number "027/500" laser-frosted on the throat in K10's mark (Archivo wdth 125 / wght 360, cap 5.6 mm, tracking 0.09 em,
centred at y -0.1372) over K10's 1.55 mm KINETIQ sub-line (wght 560, tracking 0.62 em, y -0.1446), frosted into the
face lacquer (k10_lib's etch-in-material technique). --set MARK=0 gives the audit's per-racket serials instead
(KQ-000427 front, KQ-000428 rear, the canon's Saira mark). Command and Pace differ only in the carbon: same camera,
lights and framing.

Page: /reserve gallery (16:9 desktop, the 0.45-wide card band on phones) and the VanQuish Editions card (card = x
0.275-0.725, full height). Both heads, both throat marks and both caps sit inside that band; nothing important in the
bottom 12%. The script frames itself (camera distance, height and the pair's x are solved from the projected
geometry), prints the framing, writes <out>.png and <out>_card.png and runs fillcheck.py on both.

Usage (from the blender dir, through the render lock):
  flock render.lock ../bpyenv/bin/python shots/K11-pair.py --weave command --w 960 --h 540 --spp 32 --out k11c/K11_p01
Finals (about 15 min each on 4 cores):
  flock render.lock ../bpyenv/bin/python shots/K11-pair.py --weave command --w 3200 --h 1800 --spp 256 --out final/K11-pair-command
  flock render.lock ../bpyenv/bin/python shots/K11-pair.py --weave pace --w 3200 --h 1800 --spp 256 --out final/K11-pair-pace
  (each also writes <out>_view.png, an 8-bit dithered copy, and <out>_card.png, the 4:5 band, and fill-checks both).
Detail checks: --crop x0 x1 y0 y1 (frame fractions, y from the top; skips the view/card/fill step).
Look metrics: shots/k11_measure.py <out>_view.png <out>_masks.json (front vs rear stripe and shade, grips, halo).
--dry builds the scene and writes the masks only; --rimmap prints which ember-card height each bevel facet mirrors.
Overrides: --set KEY=VALUE[,KEY=VALUE] for any upper-case layout/look constant below (floats).
Pre-canon version: shots/K11-pair.precanon.bak.
Stage 3a (art director's critique, 2026-10-22; before: K11-pair.v4-white-precrit3a.bak; helpers in feels_lib.py):
- Pace: K11-pace's 12K exactly again (PACE_ANISO 0.9, PACE_ORGANIC 0, flip 0.30) under the pre-canon band (26, hot line
  1.0) with K08's 45 mm fall-off (P_BAND_*): the hole field and tapes read over about half of each head.
- White Command: a steeper pool (14.5 deg, 250 W; fill 0.6): upper left about 200 falling to about 120 low right; the
  band is one crisp clearcoat streak (luma about 235-240), honeycombed to the coat's mirror path and glossy-only
  (W_BAND_*), so it does not grey the white; the rim card is neutral on white (no pink ember fringe); a weak fill on the
  rear racket's left wall (W_WALLR; it rendered at luma 0); white bores lifted (W_BORE_OCC / W_BORE_COL: graphite with a
  lit lip crescent, not printed black dots).
- Cap: the Q turned round the handle axis to face the camera (feels_lib.turn_mark, which also lifts the turned mark
  outside the oval cap: kq_canon's shrinkwrap buried it) and lit by feels_lib.cap_lights (a side rim strip and an
  off-axis gradient card): a satin gradient, the groove and a crisp bright-cut Q instead of a dead-black lump.
- CLAMP_IND 4: no fireflies on the 12K at final sample counts.
Pace pass (site review rounds 1 and 3, 2026-10-23; before: K11-pair.v5-prepace12k.bak):
- Pace is the canon v5 "fibre" 12K (kq_canon.PACE, shared with K08; PACE_V4=1 gives the stage 3a 12K back): the stage 3a
  tapes read as a flat grey/black checkerboard with crisp squares at card size. Now within a few percent of albedo
  from tape to tape, one uniform coat (no 30 % flip), the checker only in the fibres' sheen direction, with a fine
  fibre normal, roughness streaks and a slight crimp per tape.
- The right-hand rim is neutral 6500 K for Pace too (RIM_EMBER 0; P_RIM 0.25 of RIM_S: #ff3a1e has about a quarter of
  white's luminance): the ember hairline read as a red trim the product does not have. Only the face follows the feel.
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import k789_lib as L  # noqa: E402
from k789_lib import Matrix, Vector, bpy, racket, studio  # noqa: E402
import k10_lib as T  # noqa: E402
import kq_canon as C  # noqa: E402
import feels_lib as FL  # noqa: E402

# ------------------------------------------------------------------ layout (metres, degrees)
LENS = 85.0
YAW = 28.0          # both faces turned toward camera-right (world yaw, same for both: a parallel pair)
ROLL = 0.0          # in-plane lean, same for both
GAP = 0.07          # rear racket behind the front one, along the face normal
SHIFT = 0.19        # ... and along the face (to the right)
RISE = 0.035        # ... and up
TOP = 0.085         # framing: highest point of the pair (fraction of frame height from the top)
BOT = 0.845         # framing: lowest point (caps), clear of the bottom 12% (gallery controls)
CX = 0.5            # framing: horizontal centre of the pair
HC = 1.0            # front racket model origin (head centre) height

# ------------------------------------------------------------------ marks and racket options
MARK = 1.0          # 1 = the set number 027/500 on both throats (owner override); 0 = KQ-000427 / KQ-000428
SUBLINE = 1.0       # 1 = K10's KINETIQ sub-line under the set number
WALLS = 1.0         # 1 = the canon's side-wall etches (KINETIQ right, SWISS MADE left)
SET_TEXT = "027/500"
SET_CAP, SET_Y, SET_TRACK, SET_WGHT = 0.0056, -0.1372, 0.09, 360.0     # K10's mark
SUB_CAP, SUB_DY, SUB_TRACK, SUB_WGHT, SUB_LEVEL = 0.00155, -0.0074, 0.62, 560.0, 0.80
WHITE = 1.0         # 1 = Command is WHITE 3K twill (owner, 2026-10-22: kq_canon mat_white); 0 = the previous black
PACE_ANISO = 0.9    # stage 3a (art director): K11-pace's 12K exactly (mat_carbon_aniso + the 30 % coat flip); the
PACE_ORGANIC = 0.0  # canon's 0.65 + organic sank the Pace head to a black void (card: 14 -> 7 % lit)
PACE_FLIP = 0.30    # alternate tapes mirror the light 30 % weaker (K11's in-band tile flip)
PACE_V4 = 0.0       # 2026-10-23: 0 = the canon v5 "fibre" 12K (kq_canon.PACE, shared with K08: near-uniform black, the
                    # tapes show through the fibres' sheen direction, fine fibre normal and roughness streaks); 1 = the
                    # stage 3a 12K above (PACE_*: a flat grey/black checkerboard with crisp squares at card size)
P_BAND_S = 10.0     # Pace: the pre-canon K11-pace band (26, hot line 1.0) with K08's 45 mm fall-off (the old 14 mm
P_BAND_DECAY = 0.045  # showed about 8 of 42 holes; at 45 mm the hole field and the 12K tapes read over about half of
P_BAND_LINE = 1.0     # each head, still low-key); the canon's 13 / 6 mm / 2.5 was tuned for the baked twill
CLAMP_IND = 4.0     # indirect clamp (fireflies on the 12K at final sample counts); 0 = off
MARK_AZ = 1.0       # 1 = the cap's Q turned round the handle axis to face the camera (it sat 27 deg off, at the cap's
                    # right edge); 0 = the canon's model +Z

# ------------------------------------------------------------------ look (one light family)
K_COL = 6500.0      # neutral white light lines (stage 3: was 5800, read as a bronze cast)
N_COL = 6400.0      # bore lamp, grip and cap lights (stage 3: were 5200-5600)
KEY_S = 18.0
BAND_S = 13.0       # canon: 26 greyed the baked twill's anisotropic base across the whole face
BAND_EDGE = -0.02
BAND_DECAY = 0.006   # canon: a 6 mm fall-off (was 14): a crisper blade, far less glow in the metallic base
BAND_LINE = 2.5     # the hot line carries the stripe's peak at the lower card strength
BAND_UP = 2.5
BAND_FLIP = -1.0    # which side of the band edge is bright (+1 / -1)
BAND_D = 1.6
BAND_W = 1.05       # stage 3: 0.75 put the front face's left end in the card's border fade (front stripe dimmer)
DEPTH_R = 0.35      # band / weave / key strength at the rear face's mirror point, relative to the front's
DEPTH_S0 = 0.0      # ... the fall-off starts at the front face's centre (0) and reaches DEPTH_R at the rear's (1)
DEPTH_MIN = 0.22
WEAVE_S = 9.0
WEAVE_UP = 24.0
WEAVE_AXIS = 0.0    # 0 = graded vertically on the card, 1 = horizontally
WEAVE_LO = 0.0
WEAVE_HI = 1.0
WEAVE_FLOOR = 0.0   # round 6: Pace weave floor 0.25 -> 0 (an even grid)
WEAVE_W = 1.2
TOP_S = 18.0
RIM_S = 33.0        # ember card on the right (receding) edges: separates the front racket from the rear face
RIM_LO = 0.38       # ember card fades out below this card height (v), so the throat shoulders never mirror it
RIM_HI = 0.56
RIM_EMBER = 0.0     # 1 = ember rim (stage 3a), 0 = neutral 6500 K (2026-10-23: the ember read as a red trim the product
                    # does not have, and Command's rim is neutral: only the face follows the feel)
P_RIM = 0.25        # Pace's neutral rim, relative to RIM_S (#ff3a1e has about a quarter of white's luminance)
RIM_L = 120.0       # hairline on the left (near) edges
WALL_S = 0.7
BORE_E = 18.0       # near-camera lamp on the hole lips
GRIP_E = 2.1
GRIP_REAR = 0.30    # the rear grip a step back in the light too (canon grip: at 0.55 it read brighter than the front)
CAP_S = 0.15        # cap softbox, 80 cm, 35 cm away, 20 deg off the cap's mirror direction (canon's 0.3 W in the mirror
                    # direction read as a lit badge behind the Q here; off-axis the bright-cut Q reads alone on satin black)
CAP_SIZE = 0.80
CAP_D = 0.35
CAP_YAW = -20.0     # degrees: turns the cap softbox about the vertical off the cap's mirror direction (a highlight
                    # rolling round the cap's corner instead of a flat lit front)
CAP_CARD = 1.0      # stage 3a: 1 = the cap light set (feels_lib.cap_lights), linked to the cap and its Q, which is now
                    # turned to face the camera: a tall side strip (CAP_RS W, CAP_RSIDE deg round the handle axis from
                    # the camera, negative = camera-left) draws one rim line down the satin cap and flashes the Q's
                    # bright-cut chamfer; a soft gradient card in the mirror direction (CAP_CS) grades the cap's front;
                    # the canon proof's box (CAP_BS W). 0 = the old area light above (20 deg off-axis: a dead-black lump)
CAP_BS = 0.0        # canon box energy (W), size, distance
CAP_BSZ = 0.30
CAP_BD = 0.35
CAP_RS = 0.6        # rim strip energy (W), side angle (deg), size (m) and distance (m)
CAP_RSIDE = -75.0
CAP_RW, CAP_RH = 0.04, 0.50
CAP_RD = 0.30
CAP_CS = 20.0        # gradient card strength, size, distance, grade (u: across the cap) and floor
CAP_CW, CAP_CH = 0.30, 0.45
CAP_CD = 0.40
CAP_LO, CAP_HI, CAP_FLOOR = 0.0, 1.0, 0.15
CAP_CAZ = 28.0       # the card's reference normal turned this far (deg) past the Q's: off-axis, so the chamfer flashes
PACE_WEAVE = 0.9    # Pace only: weave-card multiplier (halves the tile contrast in shade)
CMD_WEAVE = 0.35    # Command only: weave-card multiplier (the baked twill's metallic base greys under the full card)
CMD_FLOOR = 0.0     # Command only: weave-card floor (0: the twill shimmer fades out down the face)
CMD_ANISO = -1.0    # Command only: the twill's anisotropy (-1 = the canon's 0.95)
RAKE_S = 1.0        # throat-mark rake per racket (K10's: 50 x 5 mm strip, 16 deg above the face, from camera-left)
RAKE_REAR = 0.7     # ... the rear racket's
RAKE_CMD = 1.0      # Command multiplier (the baked twill answers a rake more than the 12K does)
RAKE_D = 0.125
RAKE_EL = 16.0
RAKE_AZ = -135.0    # degrees from the face's +Y (head) direction: -135 = from the lower left (handle side), on the
                    # tapes' diagonal, so both tape directions answer it alike: the 12K stays black round the mark
                    # (from -75, K10's side light, the tapes lit as a chessboard round the throat)
RAKE_SPREAD = 180.0  # degrees (30 concentrated the strip and lit the tiles harder)
BG_EDGE = 0.018
BG_MID = 0.030
BG_HALO = 0.090
BG_GROUND = 0.008
HALO_DX = 0.04      # halo behind the heads, nudged toward the light (right)
HALO_V = 0.30       # halo peak height, frame fraction from the top (stage 3: it peaked at the top edge)
HALO_RX = 0.30
HALO_RY = 0.22
BG_TINT = 1.0       # 1 = slightly cool graphite

# ------------------------------------------------------------------ white Command (canon lighting note 8)
# Black carbon is lit by reflections only; under that studio white renders a flat mid-grey. White gets real diffuse
# light: a soft spot pool (lit upper side, shade falling away across both faces, the rear racket a step back in it), a
# weak fill so the shade stays white-in-shadow, and the reflection cards dimmed to a sheen and one gloss blade. Pool
# position: unit components in the FRONT face's frame (t = model +X, up = world Z, n = out of the face), W_POOL_D away
# from the aim point (model x, y on the front face). Pool, fill and wall are linked to the head parts only.
W_POOL = 250.0
W_POOL_DEG = 14.5
W_POOL_BLEND = 1.0  # spot blend (1 = the softest edge)
W_POOL_T, W_POOL_U, W_POOL_N = -0.53, 0.485, 0.70
W_POOL_D = 1.2
W_POOL_TX, W_POOL_TY = -0.08, 0.10
W_POOL_R = 0.06
W_POOL_REAR = 0.60  # the rear racket's pool, relative to the front's
W_AKEY = 0.0       # a close raking area key instead of / beside the pool: its inverse-square fall-off sets the
W_AKEY_T, W_AKEY_U, W_AKEY_N = -0.55, 0.65, 0.52   # gradient across the face (components as the pool's)
W_AKEY_D = 0.7
W_AKEY_SZ = 0.30
W_AKEY_TX, W_AKEY_TY = -0.06, 0.08
W_FILL = 0.60       # 1 m area light, front right
W_BAND = 1.60       # multipliers on the black-carbon light family
W_BAND_BODY = 0.35  # stage 3a: the band's soft body on white (x W_BAND), so the face keeps the pool's gradient ...
W_BAND_LINE = 14.0   # ... and its hot line (x BAND_S x W_BAND): one crisp clearcoat streak at luma 235-245
W_BAND_LW = 0.0025  # line width on the card (m)
W_BAND_HC = 2.6     # honeycomb tolerance (deg): the band emits only along the coat's mirror path to the camera and
                    # is glossy-only, so the fibres' broad sheen cannot gather it into a grey wash (K05 v6); 0 = off
W_RIM = 0.55        # the rim card on white: neutral (no ember: a red hairline on white read as a pink fringe), dimmer
W_WALLR = 4.0       # weak fill on the REAR racket's left wall (its shade side between the heads rendered at luma 0)
W_WALLR_D = 0.45
W_BORE_OCC = 0.50   # white bores: canon 0.82 / 0.025 left the holes at luma 1-4 (printed dots); a graphite gradient
W_BORE_COL = 0.07   # with the lit lip crescent, as K10 and the canon proof
W_WEAVE = 0.0
W_KEY = 0.4
W_TOP = 0.6
W_WALL = 1.6
W_BORE = 0.6
W_RAKE = 0.0        # the graphite frost reads in any light; a rake turns it pale (canon note)


def parse(argv):
    o = L.parse_args(argv, "k11c/K11_prev")
    o["weave"] = "command"
    i = 0
    while i < len(argv):
        if argv[i] == "--weave":
            o["weave"] = argv[i + 1]
        elif argv[i] == "--pace":   # canon Pace material keys for this run (tuning): --pace aniso=0.6,fib_h=1.5
            for kv in argv[i + 1].split(","):
                k, v = kv.split("=")
                C.PACE[k] = float(v)
        elif argv[i] == "--set":
            for kv in argv[i + 1].split(","):
                k, v = kv.split("=")
                globals()[k] = float(v)
        i += 1
    assert o["weave"] in ("command", "pace"), o["weave"]
    return o


# ------------------------------------------------------------------ helpers


def frame_dirs():
    yw = math.radians(YAW)
    n = Vector((math.sin(yw), -math.cos(yw), 0.0))   # front-face normal (toward camera, turned right)
    t = Vector((math.cos(yw), math.sin(yw), 0.0))    # model +X in world
    return n, t


def place(front, rear, x0, cam):
    n, t = frame_dirs()
    F = Vector((x0, 0.0, HC))
    B = F - n * GAP + t * SHIFT + Vector((0, 0, RISE))
    L.pose(front, tuple(F), yaw_deg=YAW, roll_deg=ROLL)
    L.pose(rear, tuple(B), yaw_deg=YAW, roll_deg=ROLL)
    bpy.context.view_layer.update()
    return F, B


def project(objs, cam, W, H):
    """Frame fractions (x from the left, y from the top) of every vertex of objs, for a level camera looking +Y."""
    k = LENS / 36.0
    pts = []
    for ob in objs:
        me = ob.data
        if not hasattr(me, "vertices") or len(me.vertices) == 0:
            continue
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        mw = np.array(ob.matrix_world)
        wc = co @ mw[:3, :3].T + mw[:3, 3]
        pts.append(wc[::7] if len(wc) > 20000 else wc)
    p = np.concatenate(pts)
    dy = p[:, 1] - cam.y
    u = 0.5 + k * (p[:, 0] - cam.x) / dy
    v = 0.5 - k * (W / H) * (p[:, 2] - cam.z) / dy
    return u, v


def bbox(root, cam, W, H):
    objs = [c for c in root.children if c.type == "MESH"]
    u, v = project(objs, cam, W, H)
    return float(u.min()), float(u.max()), float(v.min()), float(v.max())


def solve_frame(front, rear, W, H):
    """Camera distance, height and the pair's x so that the pair spans TOP..BOT and is centred at CX."""
    x0, D, Z = 0.0, 3.0, HC - 0.07
    for _ in range(6):
        place(front, rear, x0, None)
        cam = Vector((0.0, -D, Z))
        b = [bbox(r, cam, W, H) for r in (front, rear)]
        u0, u1 = min(b[0][0], b[1][0]), max(b[0][1], b[1][1])
        v0, v1 = min(b[0][2], b[1][2]), max(b[0][3], b[1][3])
        # height: scale distance by current span / target span
        D *= (v1 - v0) / (BOT - TOP)
        # vertical: move the camera so the span's centre lands at (TOP+BOT)/2
        vm, vt = (v0 + v1) / 2, (TOP + BOT) / 2
        Z -= (vm - vt) * (D * 36.0 / LENS) * (H / W)
        um = (u0 + u1) / 2
        x0 -= (um - CX) * (D * 36.0 / LENS)
    place(front, rear, x0, None)
    cam = Vector((0.0, -D, Z))
    return cam, x0



# ------------------------------------------------------------------ the canonical racket and its marks
def pace_opts():
    if PACE_V4:
        return dict(C.PACE_V4, aniso=PACE_ANISO, organic=PACE_ORGANIC, flip=PACE_FLIP)
    return None   # the canon Pace (kq_canon.PACE)


def set_etch():
    """K10's throat mark: the set number over the KINETIQ sub-line (k10_lib.etch_mask: Archivo-var, PIL layout)."""
    lines = [(SET_TEXT, SET_CAP, SET_Y, SET_TRACK, SET_WGHT, 125, 1.0)]
    if SUBLINE:
        lines.append(("KINETIQ", SUB_CAP, SET_Y + SUB_DY, SUB_TRACK, SUB_WGHT, 125, SUB_LEVEL))
    os.makedirs(C.ASSETS, exist_ok=True)
    path = os.path.join(C.ASSETS, "etch_set_%s%s.png" % (SET_TEXT.replace("/", "_"), "_sub" if SUBLINE else ""))
    return T.etch_mask(path, lines, bevel=0.00003)


def is_white(feel):
    return feel == "command" and WHITE > 0


def set_face_mat(feel, etch):
    """The canon face carbon of `feel` carrying the set-number etch (shared by both rackets of the set). White Command:
    kq_canon.mat_white, whose laser frost is graphite on white."""
    name = "K11_face_%s_set" % feel
    if is_white(feel):
        return C.mat_white(name, white_opts(), etch=etch)
    if feel == "command":
        return T.mat_carbon_k10(name, dict(C.COMMAND, **({"aniso": CMD_ANISO} if CMD_ANISO >= 0 else {})), etch=etch)
    return C.mat_pace(name, etch=etch, o=pace_opts())


def white_opts():
    return dict(bore_occ=W_BORE_OCC, bore_col=W_BORE_COL)


def build_pair(feel):
    """Front and rear canonical rackets (the rear a linked clone); returns (front, rear, etch box or None)."""
    if feel == "pace":
        mo = pace_opts()
    elif is_white(feel):
        mo = white_opts()
    else:
        mo = dict(white=0, **({"aniso": CMD_ANISO} if CMD_ANISO >= 0 else {}))
    if MARK:
        front, _ = C.build_racket("KQA", feel=feel, serial="", walls=bool(WALLS), mat_opts=mo)
        rear, _ = C.clone(front, "KQB")
        etch = set_etch()
        fm = set_face_mat(feel, etch)
        for r in (front, rear):
            L.override_material(C.parts(r)["face"], fm)
            r["kq_serial"] = SET_TEXT
        box = (etch[1], etch[1] + etch[3], etch[2], etch[2] + etch[4])
    else:
        front, _ = C.build_racket("KQA", feel=feel, serial="KQ-000427", walls=bool(WALLS), mat_opts=mo)
        rear, _ = C.clone(front, "KQB", serial="KQ-000428")
        if mo:  # clone() makes the rear face with the default material options; give it the shot's
            L.override_material(C.parts(rear)["face"], C.mat_carbon(feel, "face", "KQ-000428", mo))
        box = C.serial_box("KQ-000427")
    return front, rear, box


def centre(ob):
    """World centre of an object's bounding box (canon parts keep their origin at the racket's head centre)."""
    bpy.context.view_layer.update()
    c = sum((Vector(v) for v in ob.bound_box), Vector()) / 8.0
    return ob.matrix_world @ c


def rake_light(name, root, box, energy):
    """K10's throat rake, per racket: a 50 x 5 mm strip RAKE_EL above the face, from the lower left (RAKE_AZ from the
    head direction), RAKE_D from the mark, linked to the face: the frosted mark lights up, the gloss around it does not
    mirror it."""
    P = C.parts(root)
    mw = root.matrix_world
    S = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, C.T2))
    az, el = math.radians(RAKE_AZ), math.radians(RAKE_EL)
    hdir = Vector((math.sin(az), math.cos(az), 0.0))
    rd = (hdir * math.cos(el) + Vector((0, 0, 1)) * math.sin(el)).normalized()
    loc = mw @ (S + rd * RAKE_D)
    tgt = mw @ (S + Vector((0, 0.004, 0)))
    lt = studio.area_light(name, tuple(loc), 0.05, energy, color=(1.0, 0.985, 0.965), size_y=0.005, target=tuple(tgt))
    lt.data.spread = math.radians(RAKE_SPREAD)
    lt.visible_camera = False
    L.link_receivers(lt, [P["face"]], "recv_" + name)
    return lt


def cap_light(name, root, cam, energy):
    """canon_test.cap_light in world space: a small softbox in the mirror direction of the cap's front band, linked to
    the cap and its K, so the groove and the bright-cut K read on satin black."""
    P = C.parts(root)
    pr = C.cap_profile()
    yk = -0.2998 + C.CAP_SHIFT
    s_k = float(np.interp(-yk, [-y for (_, y) in pr], [s_ for (s_, _) in pr]))
    G, _ = C.section(64, grow=C.TAPE)
    mw = root.matrix_world
    Pc = mw @ Vector((0.0, yk, float(G[:, 1].max()) * s_k))
    nw = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    r = Matrix.Rotation(math.radians(CAP_YAW), 3, "Z") @ L.mirror_dir(nw, Pc, cam)
    lt = studio.area_light(name, tuple(Pc + r * CAP_D), CAP_SIZE, energy, color=L.kelvin(N_COL), size_y=CAP_SIZE * 0.35,
                           target=tuple(Pc))
    lt.visible_camera = False
    L.link_receivers(lt, [P["cap"], P["capmark"]], "recv_" + name)
    return lt


def depth_fn(card, cam, F, B, n):
    """World-space fall-off on a light card from the front racket to the rear one: 1 at the point of the card the
    FRONT face's centre mirrors, DEPTH_R at the point the rear face's centre mirrors, linear between (and on past
    the rear, down to DEPTH_MIN). Returns fn(nb) -> socket, in the card's object coordinates."""
    bpy.context.view_layer.update()
    mw = card.matrix_world
    inv = mw.inverted()
    cn = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    c0 = mw.translation

    def hit(p):
        r = L.mirror_dir(n, p, cam)
        t_ = (c0 - p).dot(cn) / r.dot(cn)
        return inv @ (p + r * t_)

    hF, hB = hit(F), hit(B)
    a = (hB - hF)
    a.z = 0.0
    ln = a.length
    a.normalize()
    k = (1.0 - DEPTH_R) / max(1e-6, 1.0 - DEPTH_S0)

    def fn(nb):
        x, y, _ = nb.coords("Object")
        s = nb.math("DIVIDE", nb.math("MULTIPLY_ADD", nb.math("SUBTRACT", x, hF.x), a.x,
                                      nb.math("MULTIPLY", nb.math("SUBTRACT", y, hF.y), a.y)), ln)
        f = nb.math("SUBTRACT", 1.0, nb.math("MULTIPLY", nb.math("SUBTRACT", s, DEPTH_S0), k))
        return nb.math("MINIMUM", nb.math("MAXIMUM", f, DEPTH_MIN), 1.0)

    print(f"depth on {card.name}: front hit ({hF.x:.3f}, {hF.y:.3f}) rear hit ({hB.x:.3f}, {hB.y:.3f}) "
          f"span {ln:.3f} m", flush=True)
    return fn


def band_card_d(name, loc, size, strength, target, grad_world, depth, edge=0.0, soft=0.006, decay=0.10, line=0.0,
                line_w=0.004, color=(1, 1, 1)):
    """k789_lib.band_card (hard edge, hot line, exponential fall-off toward the bright side) times a front-to-rear
    depth fall-off, so the one continuous stripe peaks on the front face and decays across the rear."""
    ob = L.plane(name, size, loc, normal_to=target)
    bpy.context.view_layer.update()
    mw = ob.matrix_world.to_3x3()
    g = Vector(grad_world).normalized()
    gx, gy = mw.col[0].normalized().dot(g), mw.col[1].normalized().dot(g)
    ln = math.hypot(gx, gy) or 1
    gx, gy = gx / ln, gy / ln
    dfn = depth(ob)

    def s(nb):
        x, y, _ = nb.coords("Object")
        t_ = nb.math("SUBTRACT", nb.math("MULTIPLY_ADD", x, gx, nb.math("MULTIPLY", y, gy)), edge)
        stepf = nb.smooth(t_, -soft / 2, soft / 2)
        fall = nb.math("EXPONENT", nb.math("DIVIDE", nb.math("MINIMUM", nb.math("MULTIPLY", t_, -1.0), 0.0), decay))
        f = nb.math("MULTIPLY", stepf, fall)
        if line:
            dd = nb.math("DIVIDE", t_, line_w)
            f = nb.math("ADD", f, nb.math("MULTIPLY", nb.math("EXPONENT", nb.math("MULTIPLY", nb.math("MULTIPLY", dd, dd), -1.0)), line))
        u, v, _ = nb.coords("UV")
        e = nb.math("MULTIPLY", nb.math("MULTIPLY", nb.smooth(u, 0.0, 0.08), nb.smooth(u, 1.0, 0.92)),
                    nb.math("MULTIPLY", nb.smooth(v, 0.0, 0.08), nb.smooth(v, 1.0, 0.92)))
        return nb.math("MULTIPLY", nb.math("MULTIPLY", nb.math("MULTIPLY", f, e), dfn(nb)), strength)

    ob.data.materials.append(L.emitter_mat(name + "Mat", color, s, additive=True))
    L.visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def gradient_card_d(name, loc, size, strength, target, depth=None, color=(1, 1, 1), axis="v", lo=0.0, hi=1.0,
                    floor=0.0, soft_o=0.25):
    """k789_lib.gradient_card with an optional depth fall-off (see depth_fn)."""
    ob = L.plane(name, size, loc, normal_to=target)
    dfn = depth(ob) if depth else None

    def s(nb):
        u, v, _ = nb.coords("UV")
        a_ = u if axis == "u" else v
        g = nb.smooth(a_, lo, hi)
        o_ = v if axis == "u" else u
        e = nb.math("MULTIPLY", nb.smooth(o_, 0.0, soft_o), nb.smooth(o_, 1.0, 1.0 - soft_o))
        g = nb.math("MULTIPLY_ADD", g, 1 - floor, floor)
        f = nb.math("MULTIPLY", g, e)
        if dfn:
            f = nb.math("MULTIPLY", f, dfn(nb))
        return nb.math("MULTIPLY", f, strength)

    ob.data.materials.append(L.emitter_mat(name + "Mat", color, s, additive=True))
    L.visibility(ob, camera=False, diffuse=True, glossy=True, shadow=False)
    return ob


def rim_map(card, bevel_objs, cam, label=""):
    """Which card height (v, 0 bottom .. 1 top) each right-hand bevel facet of the front racket mirrors toward the
    camera, against its model y: sets RIM_LO / RIM_HI so the ember line fades out above the throat shoulder."""
    bpy.context.view_layer.update()
    mw = card.matrix_world
    inv = mw.inverted()
    cn = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
    c0 = mw.translation
    sx = max(abs(v.co.x) for v in card.data.vertices) * 2
    sy = max(abs(v.co.y) for v in card.data.vertices) * 2
    rows = {}
    for ob in bevel_objs:
        mwo = ob.matrix_world
        nm = mwo.to_3x3().inverted().transposed()
        for p_ in ob.data.polygons:
            if p_.center.x < 0.02:
                continue
            pw = mwo @ p_.center
            nw = (nm @ p_.normal).normalized()
            vv = (cam - pw).normalized()
            if nw.dot(vv) <= 0:
                continue
            r = 2 * nw.dot(vv) * nw - vv
            if r.dot(cn) >= 0:
                continue
            t_ = (c0 - pw).dot(cn) / r.dot(cn)
            if t_ <= 0:
                continue
            hl = inv @ (pw + r * t_)
            u, v = hl.x / sx + 0.5, hl.y / sy + 0.5
            if 0 <= u <= 1 and -0.5 <= v <= 1.5:
                key = round(p_.center.y, 2)
                rows.setdefault(key, []).append(v)
    if "--rimmap" in sys.argv:
        for k_ in sorted(rows):
            vs = rows[k_]
            print(f"rim map {label}: model y {k_:+.2f}  card v {min(vs):.2f}..{max(vs):.2f}  (n {len(vs)})", flush=True)


def backdrop(cam, centre, span_h):
    """Camera-only graphite backdrop: lifts from the frame edges toward the pair, a soft halo behind the heads, a
    faint ground glow below the caps, fine grain against banding. One continuous field (no seam)."""
    y = 1.8
    D = y - cam.y
    s = D / (centre.y - cam.y)
    fh = span_h / (BOT - TOP)          # frame height at the pair's depth
    fw = fh * 16 / 9
    W, H = fw * s * 1.3, fh * s * 1.3
    ob = L.plane("Backdrop", (W, H), (cam.x, y, cam.z), normal_to=(cam.x, cam.y, cam.z))
    bpy.context.view_layer.update()
    # backdrop object space: x right, y up (the plane faces the camera)
    hx = (centre.x - cam.x) * s
    hz = (centre.z - cam.z) * s

    def strength(nb):
        x, yy, _ = nb.coords("Object")

        def blob(cx, cy, rx, ry):
            dx = nb.math("DIVIDE", nb.math("SUBTRACT", x, cx), rx)
            dy = nb.math("DIVIDE", nb.math("SUBTRACT", yy, cy), ry)
            r2 = nb.math("ADD", nb.math("MULTIPLY", dx, dx), nb.math("MULTIPLY", dy, dy))
            return nb.math("EXPONENT", nb.math("MULTIPLY", r2, -1.0))

        base = nb.math("MULTIPLY_ADD", blob(hx + 0.03 * fw * s, hz + 0.05 * fh * s, 0.80 * fw * s, 0.85 * fh * s),
                       BG_MID - BG_EDGE, BG_EDGE)
        # halo peak at frame height HALO_V (from the top), behind the heads' centre
        hv = (0.5 - HALO_V) * fh * s
        e = nb.math("MULTIPLY_ADD", blob(hx + HALO_DX * fw * s, hv, HALO_RX * fw * s, HALO_RY * fh * s),
                    BG_HALO, base)
        e = nb.math("MULTIPLY_ADD", blob(hx, hz - 0.46 * fh * s, 0.40 * fw * s, 0.24 * fh * s), BG_GROUND, e)
        tcg = nb.n.new("ShaderNodeTexCoord")
        gr = nb.n.new("ShaderNodeTexWhiteNoise"); gr.noise_dimensions = "3D"
        mpg = nb.n.new("ShaderNodeMapping"); mpg.inputs["Scale"].default_value = (2600.0, 2600.0, 2600.0)
        nb.l.new(tcg.outputs["Object"], mpg.inputs["Vector"]); nb.l.new(mpg.outputs["Vector"], gr.inputs["Vector"])
        return nb.math("MULTIPLY", e, nb.math("MULTIPLY_ADD", gr.outputs["Value"], 0.06, 0.97))

    col = (0.94, 0.97, 1.0) if BG_TINT else (1.0, 1.0, 1.0)
    m = L.cam_only_mat("BackdropMat", strength, color=col, glossy=False)
    ob.data.materials.append(m)
    L.visibility(ob, camera=True, diffuse=False, glossy=False, shadow=False)
    return ob



# ------------------------------------------------------------------ scene


def build(o):
    sc = studio.reset()
    studio.settings(o["w"], o["h"], o["spp"])
    sc.cycles.light_sampling_threshold = 0.0
    if CLAMP_IND > 0:
        sc.cycles.sample_clamp_indirect = CLAMP_IND
    W, H = o["w"], o["h"]
    feel = o["weave"]
    front, rear, mark_box = build_pair(feel)
    cam, x0 = solve_frame(front, rear, W, H)
    if MARK_AZ:
        # the clones share the mark's mesh: one angle, the mean of what each racket needs
        azs = [FL.face_az(r, cam) for r in (front, rear)]
        FL.turn_mark([front, rear], sum(azs) / 2)
        AZ_USED[0] = sum(azs) / 2
        print("cap Q turned %.1f deg to face the camera (front %.1f, rear %.1f)" % (sum(azs) / 2, *azs), flush=True)
    F = Vector(front.matrix_world.translation)
    B = Vector(rear.matrix_world.translation)
    FP, RP = C.parts(front), C.parts(rear)
    fp, rp = L.parts(front), L.parts(rear)
    allp = fp + rp
    n, t = frame_dirs()
    up = Vector((0, 0, 1))

    # canon parts in the old builder's light-linking groups (k789: _Head = face + back + wall + neck, HeadBevel = rim,
    # _HeadInner = holes + throat + bridgewall)
    heads = C.objs(FP, "_Head", style="k789") + C.objs(RP, "_Head", style="k789")
    bevels = C.objs(FP, "HeadBevel", style="k789") + C.objs(RP, "HeadBevel", style="k789")
    inner = C.objs(FP, "_HeadInner", style="k789") + C.objs(RP, "_HeadInner", style="k789")
    etches = C.objs(FP, "etchR", "etchL") + C.objs(RP, "etchR", "etchL")

    # framing report
    for nm, r in (("front", front), ("rear", rear)):
        b = bbox(r, cam, W, H)
        print(f"framing {nm}: x {b[0]:.3f}-{b[1]:.3f}  y {b[2]:.3f}-{b[3]:.3f}", flush=True)
    M = (F + B) / 2
    fh = (M.y - cam.y) * 36.0 / LENS * (H / W)  # frame height at the pair (sensor 36 mm wide)
    print(f"camera {tuple(round(c, 3) for c in cam)}  pair x0 {x0:.3f}  frame h at pair {fh:.3f} m", flush=True)

    backdrop(cam, Vector((M.x, M.y, M.z - 0.03)), fh * (BOT - TOP))

    kc = L.kelvin(K_COL)
    wh = is_white(feel)
    wk = (lambda k_: k_) if wh else (lambda k_: 1.0)   # white-only multiplier
    # --- key: one slit overhead and slightly in front: rakes down both faces, draws both top curves
    key = L.strip("Key", tuple(M + Vector((0.0, -0.30, 0.95))), (2.4, 0.05), KEY_S * wk(W_KEY), tuple(M + Vector((0, 0, 0.1))),
                  color=kc, soft_ends=0.3)
    L.link_receivers(key, allp, "recv_key")

    # --- band: ONE hard-edged card in the faces' mirror direction; parallel faces mirror it as one sweep
    d = L.mirror_dir(n, M, cam)
    h = Vector((-d.y, d.x, 0)).normalized() * BAND_FLIP
    bright = (h + up * BAND_UP).normalized()
    # the card falls off from the front face's mirror point to the rear's, so the stripe peaks on the front racket
    # and the rear one sits a step back in the light
    depth = lambda card: depth_fn(card, cam, F, B, n)  # noqa: E731
    if wh:
        # white: a faint body and one crisp clearcoat streak, honeycombed to the coat's mirror path, glossy-only
        cpr = FL.mirror_point(cam, n, M) if W_BAND_HC > 0 else None
        band = FL.band_card_hc("Band", tuple(M + d * BAND_D), (BAND_W, 0.75), BAND_S * W_BAND, tuple(M), tuple(bright),
                               edge=BAND_EDGE, soft=0.006, decay=BAND_DECAY, line=W_BAND_LINE, line_w=W_BAND_LW,
                               color=kc, depth=depth, cprime=cpr, tol_deg=max(W_BAND_HC, 0.1),
                               glossy_only=W_BAND_HC > 0, body=W_BAND_BODY)
    elif feel == "pace":
        band = band_card_d("Band", tuple(M + d * BAND_D), (BAND_W, 0.75), P_BAND_S, tuple(M), tuple(bright), depth,
                           edge=BAND_EDGE, soft=0.006, decay=P_BAND_DECAY, line=P_BAND_LINE, color=kc)
    else:
        band = band_card_d("Band", tuple(M + d * BAND_D), (BAND_W, 0.75), BAND_S, tuple(M), tuple(bright), depth,
                           edge=BAND_EDGE, soft=0.006, decay=BAND_DECAY, line=BAND_LINE, color=kc)
    L.link_receivers(band, heads, "recv_band")

    # --- weave: a soft card above the mirror direction, seen only by the fibre lobes (twill / spread-tow sheen)
    hz_axis = Vector((-d.y, d.x, 0)).normalized()
    d_up = (Matrix.Rotation(math.radians(WEAVE_UP), 3, hz_axis) @ d).normalized()
    if d_up.z < d.z:
        d_up = (Matrix.Rotation(math.radians(-WEAVE_UP), 3, hz_axis) @ d).normalized()
    wv_s = WEAVE_S * (PACE_WEAVE if feel == "pace" else CMD_WEAVE) * wk(W_WEAVE)
    wv = None if wv_s <= 0 else gradient_card_d("Weave", tuple(M + d_up * 1.4), (WEAVE_W, 0.7), wv_s, tuple(M), depth, color=kc,
                         axis="u" if WEAVE_AXIS else "v", lo=WEAVE_LO, hi=WEAVE_HI,
                         floor=WEAVE_FLOOR if feel == "pace" else CMD_FLOOR)
    if wv is not None:
        L.link_receivers(wv, heads, "recv_weave")

    # --- top curves: a broad card overhead-behind, only the top edges can mirror it
    top = L.strip("Top", tuple(M + Vector((0.0, 0.9, 0.64))), (2.6, 1.4), TOP_S * wk(W_TOP), tuple(M + Vector((0, 0, 0.155))),
                  color=L.kelvin(6500), soft_ends=0.45, soft_w=0.25)
    L.link_receivers(top, bevels, "recv_top")

    # --- rims: right-hand (receding) edges get one hairline each from a card behind-right; the left (near) edges a
    # cooler line from the front-left. Linked to the rounded edges only. The ember card fades out toward its bottom:
    # down-facing edges (the throat shoulders, the head's lowest curve) mirror its lower part, so the ember line only
    # traces the head's curved right edge.
    rim_col = L.hex_lin("#ff3a1e") if (RIM_EMBER and not wh) else L.kelvin(6500)
    rim_s = RIM_S * (wk(W_RIM) if wh else (1.0 if RIM_EMBER else P_RIM))
    rim = gradient_card_d("RimR", tuple(M + t * 1.0 + n * -0.35 + Vector((0, 0, -0.04))), (2.4, 2.0), rim_s,
                          tuple(M + t * 0.12), None, color=rim_col, axis="v", lo=RIM_LO, hi=RIM_HI, floor=0.0,
                          soft_o=0.12)
    L.link_receivers(rim, bevels, "recv_rimR")
    rim_map(rim, C.objs(FP, "rim"), cam, "front")
    rim_map(rim, C.objs(RP, "rim"), cam, "rear")
    riml = studio.area_light("RimL", tuple(M - t * 1.1 + n * 0.25 + Vector((0, 0, -0.04))), 2.4, RIM_L,
                             color=L.kelvin(6500), size_y=2.0, target=tuple(M - t * 0.12))
    riml.visible_diffuse = False
    L.link_receivers(riml, bevels, "recv_rimL")

    # --- left side walls (both parallel): a tall card in the wall's mirror direction, bright high, fading down, so
    # the 38 mm band grades away and the twill folding onto it (and the SWISS MADE etch) reads against it
    wn = -t
    wp = F + wn * 0.13 + Vector((0, 0, -0.03))
    dw = L.mirror_dir(wn, wp, cam)
    wall = L.gradient_card("Wall", tuple(wp + dw * 1.2), (0.10, 1.2), WALL_S * wk(W_WALL), tuple(wp), color=L.kelvin(6500),
                           axis="v", lo=0.15, hi=0.95, floor=0.0)
    L.link_receivers(wall, heads + etches, "recv_wall")

    # --- bores: a soft lamp beside the camera, linked to the hole walls only -> every hole a lit crescent on its lip
    L.area_at("Bore", cam + Vector((0.35, 0.0, 0.45)), M, 0.6, 0.6, BORE_E * wk(W_BORE), color=L.kelvin(N_COL), recv=inner)

    # --- white Command: one soft spot pool per racket from the same direction (front face's upper left), and a weak
    # fill, on the head parts only. The rear racket's pool is weaker (W_POOL_REAR: the rear sits a step back in the
    # light) and its shadow blockers are the rear's own parts, so the front racket casts no hard diagonal shadow across
    # the rear face (it read as a dirty band at card size).
    if wh:
        for root_, k_ in ((front, 1.0), (rear, W_POOL_REAR)):
            Pr_ = C.parts(root_)
            recv_ = (C.objs(Pr_, "_Head", style="k789") + C.objs(Pr_, "HeadBevel", style="k789")
                     + C.objs(Pr_, "_HeadInner", style="k789") + C.objs(Pr_, "etchR", "etchL"))
            mw_ = root_.matrix_world
            aim = mw_ @ Vector((W_POOL_TX, W_POOL_TY, C.T2))
            pd = (t * W_POOL_T + up * W_POOL_U + n * W_POOL_N).normalized()
            if W_POOL * k_ > 0:
                pl = studio.spot_light("WPool_" + root_.name, tuple(aim + pd * W_POOL_D), W_POOL * k_, W_POOL_DEG,
                                       blend=W_POOL_BLEND, color=(1.0, 0.985, 0.97), target=tuple(aim), radius=W_POOL_R)
                L.link_receivers(pl, recv_, "recv_wpool_" + root_.name)
                bc = bpy.data.collections.new("block_wpool_" + root_.name)
                for ob_ in C.objs(Pr_, "all"):
                    bc.objects.link(ob_)
                pl.light_linking.blocker_collection = bc
                print(f"white pool {root_.name} at {tuple(round(c, 3) for c in aim + pd * W_POOL_D)} "
                      f"aim {tuple(round(c, 3) for c in aim)}", flush=True)
            if W_AKEY > 0 and root_ is front:
                ak_aim = mw_ @ Vector((W_AKEY_TX, W_AKEY_TY, C.T2))
                kd = (t * W_AKEY_T + up * W_AKEY_U + n * W_AKEY_N).normalized()
                ak = studio.area_light("WAKey", tuple(ak_aim + kd * W_AKEY_D), W_AKEY_SZ, W_AKEY, color=(1.0, 0.985, 0.97),
                                       target=tuple(ak_aim))
                ak.visible_camera = False
                L.link_receivers(ak, heads + bevels + inner + etches, "recv_wakey")
        if W_FILL > 0:
            fl = studio.area_light("WFill", tuple(M + t * 0.75 + n * 0.9 + up * 0.25), 1.0, W_FILL,
                                   color=(0.94, 0.96, 1.0), target=tuple(M))
            fl.visible_camera = False
            L.link_receivers(fl, heads + bevels + inner + etches, "recv_wfill")
        if W_WALLR > 0:
            # the rear racket's left wall (the shade side seen between the two heads): a weak soft light from the
            # front left, on the rear's wall and edges only, unshadowed by the front racket
            wr = rear.matrix_world @ Vector((-0.125, -0.06, 0.0))
            wd = (-t * 0.80 + n * 0.45 + up * 0.40).normalized()
            wl_ = studio.area_light("WWallR", tuple(wr + wd * W_WALLR_D), 0.35, W_WALLR, color=(0.97, 0.98, 1.0),
                                    target=tuple(wr))
            wl_.visible_camera = False
            L.link_receivers(wl_, C.objs(RP, "wall", "rim", "etchL"), "recv_wwallr")
            bc = bpy.data.collections.new("block_wwallr")
            for ob_ in C.objs(RP, "all"):
                bc.objects.link(ob_)
            wl_.light_linking.blocker_collection = bc

    # --- grips and caps, per racket
    for root, side, ge in ((front, -1, GRIP_E), (rear, 1, GRIP_E * GRIP_REAR)):
        P = C.parts(root)
        gc = centre(P["grip"])
        L.area_at(f"Grip_{root.name}", gc + t * (0.32 * side) + Vector((0, -0.22, 0.10)), gc, 0.025, 0.45, ge,
                  color=L.kelvin(N_COL), recv=[P["grip"]])
        if CAP_CARD:
            FL.cap_lights(f"Cap_{root.name}", root, cam, AZ_USED[0], k=1.0 if root is front else GRIP_REAR, box=CAP_BS,
                          box_size=CAP_BSZ, box_d=CAP_BD, rim=CAP_RS, rim_side=CAP_RSIDE, rim_size=(CAP_RW, CAP_RH),
                          rim_d=CAP_RD, card=CAP_CS, card_size=(CAP_CW, CAP_CH), card_d=CAP_CD, card_lo=CAP_LO,
                          card_hi=CAP_HI, card_floor=CAP_FLOOR, card_az=CAP_CAZ, color=L.kelvin(N_COL))
        else:
            cap_light(f"Cap_{root.name}", root, cam, CAP_S * (1.0 if root is front else GRIP_REAR))
        if RAKE_S * wk(W_RAKE) > 0:
            rake_light(f"Rake_{root.name}", root, mark_box,
                       RAKE_S * wk(W_RAKE) * (1.0 if root is front else RAKE_REAR) * (RAKE_CMD if feel == "command" else 1.0))

    L.visual_only("Backdrop")
    L.debug_off()
    studio.camera(tuple(cam), (cam.x, cam.y + 1.0, cam.z), lens=LENS)
    MASKS.update(masks(front, rear, cam, W, H, mark_box))
    return sc


MASKS = {}
AZ_USED = [0.0]


def _hull(u, v):
    pts = sorted(set(zip(np.round(u, 5).tolist(), np.round(v, 5).tolist())))
    if len(pts) < 3:
        return pts

    def cross(o_, a_, b_):
        return (a_[0] - o_[0]) * (b_[1] - o_[1]) - (a_[1] - o_[1]) * (b_[0] - o_[0])
    lo_, hi_ = [], []
    for p_ in pts:
        while len(lo_) >= 2 and cross(lo_[-2], lo_[-1], p_) <= 0:
            lo_.pop()
        lo_.append(p_)
    for p_ in reversed(pts):
        while len(hi_) >= 2 and cross(hi_[-2], hi_[-1], p_) <= 0:
            hi_.pop()
        hi_.append(p_)
    return lo_[:-1] + hi_[:-1]


def masks(front, rear, cam, W, H, mark_box):
    """Frame-fraction polygons for k11_measure.py: each racket's front face, whole head, holes, throat, throat mark,
    grip and cap (x from the left, y from the top)."""
    k = LENS / 36.0

    def proj(ob, co):
        mw = np.array(ob.matrix_world)
        wc = co @ mw[:3, :3].T + mw[:3, 3]
        dy = wc[:, 1] - cam.y
        return 0.5 + k * (wc[:, 0] - cam.x) / dy, 0.5 - k * (W / H) * (wc[:, 2] - cam.z) / dy

    def verts(ob):
        me = ob.data
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        return co.reshape(-1, 3)

    T2 = C.T2
    res = {}
    for nm, r in (("front", front), ("rear", rear)):
        P = C.parts(r)
        face = P["face"]
        co = verts(face)
        res[nm + "_face"] = _hull(*proj(face, co[co[:, 2] > T2 - 1e-4]))
        allc = np.concatenate([verts(P[k_]) for k_ in ("face", "rim", "wall")])
        res[nm + "_head"] = _hull(*proj(face, allc[::5]))
        hl = []
        for (hx, hy, hr) in C.holes_canon():
            ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
            rr = hr * C.U * 1.25
            c = np.stack([hx * C.U + rr * np.cos(ang), hy * C.U + rr * np.sin(ang), np.full(24, T2)], 1)
            u, v = proj(face, c)
            hl.append(list(zip(u.tolist(), v.tolist())))
        res[nm + "_holes"] = hl
        th = np.array([(x, y, T2) for (x, y) in T.throat_loop()])
        res[nm + "_throat"] = [_hull(*proj(face, th))]
        x0_, x1_, y0_, y1_ = mark_box
        res[nm + "_serial"] = _hull(*proj(face, np.array([(x0_, y0_, T2), (x1_, y0_, T2), (x1_, y1_, T2), (x0_, y1_, T2)])))
        for part_, key_ in (("_grip", "grip"), ("_cap", "cap")):
            ob = P[key_]
            res[nm + part_] = _hull(*proj(ob, verts(ob)[::3]))
    return res


def post(o, png):
    import json
    with open(png.replace(".png", "_masks.json"), "w") as fh_:
        json.dump(MASKS, fh_)
    """8-bit dithered view copies of the 16-bit master (full frame and the 4:5 band), like the site's export
    (stills.mjs: triangular dither of about one 8-bit step), and the fill check on both."""
    from PIL import Image
    img = bpy.data.images.load(png)
    img.colorspace_settings.name = "Non-Color"
    w, h = img.size
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    a = px.reshape(h, w, 4)[::-1, :, :3] * 255.0
    rng = np.random.default_rng(7)
    a = a + rng.random(a.shape, np.float32) - rng.random(a.shape, np.float32)
    im = Image.fromarray(np.clip(np.round(a), 0, 255).astype(np.uint8), "RGB")
    view = png.replace(".png", "_view.png")
    card = png.replace(".png", "_card.png")
    im.save(view)
    im.crop((round(w * 0.275), 0, round(w * 0.725), h)).save(card)
    fc = os.path.join(ROOT, "fillcheck.py")
    subprocess.run([sys.executable, fc, view, card], check=False)


if __name__ == "__main__":
    o = parse(sys.argv[1:])
    os.makedirs(os.path.join(studio.OUT, os.path.dirname(o["out"])), exist_ok=True)
    if "--dry" in sys.argv:
        build(o)
        import json
        with open(os.path.join(studio.OUT, o["out"] + "_masks.json"), "w") as fh_:
            json.dump(MASKS, fh_)
        sys.exit(0)
    path = L.render_main(build, o)
    if not o["crop"]:
        post(o, path)

