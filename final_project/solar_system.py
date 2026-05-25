"""
Procedural Solar System — Blender + Python (bpy)
=================================================
Final Project for the 3D Graphics course at WSB Merito Wrocław.

The whole scene (Sun, planets, lighting, camera, animation) is generated
by this single script. Nothing is built in the Blender UI by hand —
running this file is enough to produce the finished scene and a render.

How to run
----------
1. Open Blender (4.x recommended, 3.x also works).
2. Switch to the "Scripting" workspace.
3. File -> Open... and pick this file (solar_system.py).
4. Click "Run Script" (or press Alt+P with the cursor in the editor).

A still frame is rendered next to the script as `render.png`.
After the render finishes, press SPACE in the viewport to play the
animated orbits.

Configuration
-------------
All scene parameters (planet list, sizes, distances, colors, periods,
camera position, render resolution) live as constants at the top of
this file. Edit them and re-run to get a different solar system.
"""

import math
import os
import random

import bpy


# ============================================================
#  Configuration
# ============================================================

# (name, sphere_radius, orbit_radius, base_color RGB 0-1, orbit_period_frames,
#  material_type, style_overrides_dict)
# material_type chooses the procedural shader:
#   "rocky"     -> cratered Voronoi surface  (Mercury, Mars)
#   "earth"     -> ocean + procedural continents + polar ice
#   "venus"     -> smooth cream-yellow with cloud noise swirls
#   "gas_giant" -> horizontal bands via Wave texture  (Jupiter, Saturn)
# style overrides are forwarded as kwargs to the material function so each
# planet of the same type can still look distinctive.
PLANETS = [
    ("Mercury", 0.40,  4.0, (0.50, 0.45, 0.40),  60, "rocky",
        {"voronoi_scale": 11.0, "bump_strength": 0.55, "roughness": 0.90}),
    ("Venus",   0.62,  6.2, (0.95, 0.78, 0.35),  90, "venus", {}),
    ("Earth",   0.70,  8.7, (0.10, 0.30, 0.60), 120, "earth", {}),
    ("Mars",    0.55, 11.2, (0.78, 0.32, 0.18), 165, "rocky",
        {"voronoi_scale": 7.0,  "bump_strength": 0.35, "roughness": 0.82}),
    # Jupiter: many narrow bands, very wavy, high contrast
    ("Jupiter", 1.45, 15.5, (0.80, 0.62, 0.45), 230, "gas_giant",
        {"band_scale": 6.0, "distortion": 9.0, "detail": 4.0, "contrast": 1.3}),
    # Saturn: fewer/wider bands, calm, soft contrast
    ("Saturn",  1.20, 19.5, (0.92, 0.80, 0.55), 290, "gas_giant",
        {"band_scale": 3.0, "distortion": 2.5, "detail": 2.0, "contrast": 0.7}),
]

SUN_RADIUS              = 2.6
SUN_COLOR               = (1.0, 0.50, 0.00)   # pure yellow-orange, NO blue at all
SUN_EMISSION_STRENGTH   = 3.5    # moderate so AgX tone-mapping does not desaturate to white
SUN_LIGHT_ENERGY        = 17000.0  # the actual scene-lighting source (boosted to compensate for lower emission)
SUN_LIGHT_COLOR         = (1.0, 0.92, 0.75)

SATURN_RING_INNER       = 1.5   # multiplied by Saturn radius
SATURN_RING_OUTER       = 2.4
SATURN_RING_TILT_DEG    = 18.0

CAMERA_LOCATION         = (0.0, -40.0, 24.0)
CAMERA_TARGET           = (0.0,   0.0,  0.0)

ANIMATION_FRAMES        = 240
ANIMATION_FPS           = 24          # 240 frames / 24 fps = 10-second clip
RENDER_FRAME            = 60          # which frame to render as the still
RENDER_OUTPUT_NAME      = "render.png"
ANIMATION_OUTPUT_NAME   = "animation"  # extension is added by Blender (.mp4)
RENDER_RESOLUTION_X     = 1600
RENDER_RESOLUTION_Y     = 900
WORLD_BACKGROUND_COLOR  = (0.005, 0.005, 0.020, 1.0)

# --- Star field (procedural world shader) ---
STARFIELD_ENABLE        = True
STARFIELD_DENSITY       = 480.0    # bigger = more stars
STARFIELD_BRIGHTNESS    = 4.0      # how bright the star pixels are
STARFIELD_SIZE          = 0.045    # threshold of voronoi cell that becomes a star (bigger = chunkier stars)

# --- Orbit guide paths (thin glowing circles around the Sun) ---
ORBIT_PATHS_ENABLE      = True
ORBIT_PATH_THICKNESS    = 0.012
ORBIT_PATH_COLOR        = (0.55, 0.70, 0.95)
ORBIT_PATH_STRENGTH     = 0.4

# --- Asteroid belt (between Mars and Jupiter) ---
ASTEROID_BELT_ENABLE    = True
ASTEROID_COUNT          = 280
ASTEROID_SUBDIVISIONS   = 2        # 1 = very low-poly, 2 = chunky, 3 = smooth
ASTEROID_BELT_INNER     = 12.6
ASTEROID_BELT_OUTER     = 14.2
ASTEROID_BELT_HEIGHT    = 0.20     # vertical jitter (+/-) — thin flat ring
ASTEROID_SIZE_MIN       = 0.035
ASTEROID_SIZE_MAX       = 0.085
ASTEROID_BOULDER_CHANCE = 0.04     # 4 % become slightly larger
ASTEROID_BOULDER_MIN    = 0.10
ASTEROID_BOULDER_MAX    = 0.16
ASTEROID_BELT_PERIOD    = 360      # frames for one orbit (slower than Jupiter)
ASTEROID_SEED           = 42       # change for a different random arrangement

# Output mode:
#   'still'      -> render a single PNG at RENDER_FRAME  (fast, default)
#   'animation'  -> render every frame as a PNG sequence (slow, minutes)
#   'none'       -> build the scene but skip rendering   (press F12 manually)
RENDER_MODE             = 'still'

# If automatic path detection fails (e.g. the script wrote to C:\ instead of
# the project folder), hard-code the output folder here.  Leave empty ("")
# to use auto-detection.  Use a raw string on Windows: r"C:\path\to\folder"
OUTPUT_DIR_OVERRIDE     = r"C:\Users\zapkinus\Desktop\3dgraphics\final_project"


# ============================================================
#  Small helpers
# ============================================================

def log(msg):
    print(f"[solar_system] {msg}")


def safe_set_input(node, candidate_names, value):
    """Set the first matching input that exists on a node.
    Blender 4.x renamed several Principled BSDF sockets, so we try
    multiple names and silently skip the ones that don't exist.
    """
    for name in candidate_names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return True
    return False


def script_directory():
    """Find the directory containing solar_system.py.

    The detection order is:
      1. OUTPUT_DIR_OVERRIDE if the user set it manually at the top of the file.
      2. __file__ — works when launched with `blender --python solar_system.py`.
      3. The active text editor's loaded file path.
      4. Search every Blender text data-block for one ending in solar_system.py.
      5. The directory of the open .blend file (only useful if it was saved).
      6. Current working directory (last resort — on Windows this is often
         C:\\, which is read-only, so we warn the user).
    """
    if OUTPUT_DIR_OVERRIDE:
        return OUTPUT_DIR_OVERRIDE

    # __file__ — works when run via `blender --python solar_system.py`
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass

    # Active text editor space
    space = getattr(bpy.context, "space_data", None)
    if space is not None:
        text = getattr(space, "text", None)
        if text is not None and text.filepath:
            return os.path.dirname(bpy.path.abspath(text.filepath))

    # Any loaded text data-block matching our filename
    for text in bpy.data.texts:
        if text.filepath and text.filepath.lower().endswith("solar_system.py"):
            return os.path.dirname(bpy.path.abspath(text.filepath))

    # The open .blend file's directory (only if saved)
    if bpy.data.filepath:
        return os.path.dirname(bpy.path.abspath(bpy.data.filepath))

    # Last resort
    fallback = os.getcwd()
    log(f"WARNING: could not detect script directory, falling back to {fallback}")
    log("If this fails to write, set OUTPUT_DIR_OVERRIDE at the top of the file.")
    return fallback


# ============================================================
#  Scene reset
# ============================================================

def clear_scene():
    """Remove every object plus orphan data blocks so the script is idempotent."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in (bpy.data.meshes,
                       bpy.data.materials,
                       bpy.data.lights,
                       bpy.data.cameras,
                       bpy.data.objects):
        for item in list(collection):
            try:
                collection.remove(item)
            except RuntimeError:
                pass


# ============================================================
#  Materials
# ============================================================

def _new_material(name):
    """Create a fresh node-based material with an empty node tree."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    for node in list(mat.node_tree.nodes):
        mat.node_tree.nodes.remove(node)
    return mat, mat.node_tree.nodes, mat.node_tree.links


def _principled(nodes, x=200, roughness=0.7, specular=0.3):
    """Helper: spawn a Principled BSDF with sensible defaults."""
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (x, 0)
    safe_set_input(bsdf, ['Roughness'], roughness)
    safe_set_input(bsdf, ['Specular IOR Level', 'Specular'], specular)
    return bsdf


def _output(nodes, x=500):
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (x, 0)
    return out


def make_material(name, color, emission_strength=0.0, roughness=0.55):
    """Plain flat-color material — kept as a fallback for tasks that do not
    use the procedural planet materials below."""
    mat, nodes, links = _new_material(name)
    out = _output(nodes, x=300)
    if emission_strength > 0:
        shader = nodes.new('ShaderNodeEmission')
        shader.inputs['Color'].default_value = (*color, 1.0)
        shader.inputs['Strength'].default_value = emission_strength
        shader.location = (0, 0)
        links.new(shader.outputs['Emission'], out.inputs['Surface'])
    else:
        shader = _principled(nodes, x=0, roughness=roughness)
        safe_set_input(shader, ['Base Color'], (*color, 1.0))
        links.new(shader.outputs['BSDF'], out.inputs['Surface'])
    return mat


# ------------------------------------------------------------
#  Procedural planet materials
# ------------------------------------------------------------

def make_sun_material(name, color, emission_strength):
    """Emissive sun with noise-driven surface variation (sun-spot feel)."""
    mat, nodes, links = _new_material(name)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-700, 0)

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = 4.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Distortion'].default_value = 1.2
    links.new(coords.outputs['Generated'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-250, 0)
    # Noise just adds subtle sun-spot variation around the base colour.
    # Blue is kept at 0 in both stops so AgX cannot tint the highlights to
    # cream/peach when the channel values clip.
    ramp.color_ramp.elements[0].color = (color[0] * 0.75, color[1] * 0.40, 0.0, 1.0)
    ramp.color_ramp.elements[1].color = (1.0, min(color[1] * 1.45, 1.0), 0.05, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Strength'].default_value = emission_strength
    links.new(ramp.outputs['Color'], emission.inputs['Color'])

    out = _output(nodes, x=300)
    links.new(emission.outputs['Emission'], out.inputs['Surface'])
    return mat


def make_rocky_material(name, base_color, voronoi_scale=9.0, bump_strength=0.45, roughness=0.88):
    """Rocky / cratered surface (Mercury, Mars).
    Voronoi gives crater pattern via bump, noise gives broad colour variation."""
    dark = tuple(c * 0.55 for c in base_color)
    mat, nodes, links = _new_material(name)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-1100, 0)

    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-850, 200)
    voronoi.inputs['Scale'].default_value = voronoi_scale
    links.new(coords.outputs['Generated'], voronoi.inputs['Vector'])

    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-850, -200)
    noise.inputs['Scale'].default_value = 3.5
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Distortion'].default_value = 0.6
    links.new(coords.outputs['Generated'], noise.inputs['Vector'])

    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-550, -200)
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[0].color = (*dark, 1.0)
    ramp.color_ramp.elements[1].color = (*base_color, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    bump = nodes.new('ShaderNodeBump')
    bump.location = (-250, 200)
    bump.inputs['Strength'].default_value = bump_strength
    links.new(voronoi.outputs['Distance'], bump.inputs['Height'])

    bsdf = _principled(nodes, x=0, roughness=roughness, specular=0.15)
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    out = _output(nodes, x=300)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_earth_material(name):
    """Procedural Earth: noise-based continent mask over an ocean base."""
    OCEAN     = (0.04, 0.18, 0.45)
    LAND_DARK = (0.25, 0.18, 0.10)   # bare rock / desert
    LAND_VEG  = (0.18, 0.36, 0.13)   # vegetation green
    POLAR_ICE = (0.92, 0.95, 0.97)

    mat, nodes, links = _new_material(name)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-1400, 0)

    # Continent mask
    cont_noise = nodes.new('ShaderNodeTexNoise')
    cont_noise.location = (-1200, 250)
    cont_noise.inputs['Scale'].default_value = 2.4
    cont_noise.inputs['Detail'].default_value = 8.0
    cont_noise.inputs['Distortion'].default_value = 1.8
    links.new(coords.outputs['Generated'], cont_noise.inputs['Vector'])

    land_mask = nodes.new('ShaderNodeValToRGB')
    land_mask.location = (-900, 250)
    land_mask.color_ramp.elements[0].position = 0.45
    land_mask.color_ramp.elements[1].position = 0.55
    links.new(cont_noise.outputs['Fac'], land_mask.inputs['Fac'])

    # Land surface variation (rock vs vegetation)
    land_noise = nodes.new('ShaderNodeTexNoise')
    land_noise.location = (-1200, -50)
    land_noise.inputs['Scale'].default_value = 7.0
    land_noise.inputs['Detail'].default_value = 8.0
    links.new(coords.outputs['Generated'], land_noise.inputs['Vector'])

    land_ramp = nodes.new('ShaderNodeValToRGB')
    land_ramp.location = (-900, -50)
    land_ramp.color_ramp.elements[0].color = (*LAND_DARK, 1.0)
    land_ramp.color_ramp.elements[1].color = (*LAND_VEG, 1.0)
    links.new(land_noise.outputs['Fac'], land_ramp.inputs['Fac'])

    ocean_rgb = nodes.new('ShaderNodeRGB')
    ocean_rgb.location = (-900, 450)
    ocean_rgb.outputs[0].default_value = (*OCEAN, 1.0)

    mix_land_ocean = nodes.new('ShaderNodeMixRGB')
    mix_land_ocean.location = (-600, 200)
    links.new(land_mask.outputs['Color'], mix_land_ocean.inputs['Fac'])
    links.new(ocean_rgb.outputs[0], mix_land_ocean.inputs['Color1'])
    links.new(land_ramp.outputs['Color'], mix_land_ocean.inputs['Color2'])

    # Polar ice caps from Z coordinate
    separate = nodes.new('ShaderNodeSeparateXYZ')
    separate.location = (-1200, -350)
    links.new(coords.outputs['Generated'], separate.inputs['Vector'])

    abs_z = nodes.new('ShaderNodeMath')
    abs_z.operation = 'ABSOLUTE'
    abs_z.location = (-1000, -350)
    links.new(separate.outputs['Z'], abs_z.inputs[0])

    ice_ramp = nodes.new('ShaderNodeValToRGB')
    ice_ramp.location = (-800, -350)
    # Only the very top and bottom 12-18 % of the sphere become polar ice.
    ice_ramp.color_ramp.elements[0].position = 0.82
    ice_ramp.color_ramp.elements[1].position = 0.92
    ice_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ice_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    links.new(abs_z.outputs[0], ice_ramp.inputs['Fac'])

    ice_rgb = nodes.new('ShaderNodeRGB')
    ice_rgb.location = (-800, -550)
    ice_rgb.outputs[0].default_value = (*POLAR_ICE, 1.0)

    mix_with_ice = nodes.new('ShaderNodeMixRGB')
    mix_with_ice.location = (-300, 0)
    links.new(ice_ramp.outputs['Color'], mix_with_ice.inputs['Fac'])
    links.new(mix_land_ocean.outputs['Color'], mix_with_ice.inputs['Color1'])
    links.new(ice_rgb.outputs[0], mix_with_ice.inputs['Color2'])

    # Light bump from land mask
    bump = nodes.new('ShaderNodeBump')
    bump.location = (-300, -250)
    bump.inputs['Strength'].default_value = 0.12
    links.new(land_mask.outputs['Color'], bump.inputs['Height'])

    bsdf = _principled(nodes, x=0, roughness=0.65, specular=0.35)
    links.new(mix_with_ice.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    out = _output(nodes, x=300)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_venus_material(name, base_color):
    """Venus: thick swirling cream cloud cover, very smooth."""
    light = tuple(min(c * 1.10, 1.0) for c in base_color)
    dark  = tuple(c * 0.65 for c in base_color)

    mat, nodes, links = _new_material(name)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-900, 0)

    swirl = nodes.new('ShaderNodeTexNoise')
    swirl.location = (-700, 100)
    swirl.inputs['Scale'].default_value = 1.8
    swirl.inputs['Detail'].default_value = 6.0
    swirl.inputs['Distortion'].default_value = 3.5
    links.new(coords.outputs['Generated'], swirl.inputs['Vector'])

    wisps = nodes.new('ShaderNodeTexNoise')
    wisps.location = (-700, -200)
    wisps.inputs['Scale'].default_value = 8.0
    wisps.inputs['Detail'].default_value = 6.0
    wisps.inputs['Distortion'].default_value = 1.5
    links.new(coords.outputs['Generated'], wisps.inputs['Vector'])

    swirl_color = nodes.new('ShaderNodeValToRGB')
    swirl_color.location = (-400, 100)
    swirl_color.color_ramp.elements[0].color = (*dark, 1.0)
    swirl_color.color_ramp.elements[1].color = (*light, 1.0)
    links.new(swirl.outputs['Fac'], swirl_color.inputs['Fac'])

    mix = nodes.new('ShaderNodeMixRGB')
    mix.location = (-100, 0)
    mix.blend_type = 'OVERLAY'
    mix.inputs['Fac'].default_value = 0.35
    links.new(swirl_color.outputs['Color'], mix.inputs['Color1'])
    # Use the wisps fac as a grayscale color
    wisp_color = nodes.new('ShaderNodeValToRGB')
    wisp_color.location = (-400, -200)
    wisp_color.color_ramp.elements[0].color = (0.6, 0.6, 0.6, 1)
    wisp_color.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1)
    links.new(wisps.outputs['Fac'], wisp_color.inputs['Fac'])
    links.new(wisp_color.outputs['Color'], mix.inputs['Color2'])

    bsdf = _principled(nodes, x=150, roughness=0.55, specular=0.30)
    links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    out = _output(nodes, x=450)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_gas_giant_material(name, base_color,
                            band_scale=4.5, distortion=6.0, detail=3.0,
                            contrast=1.0):
    """Gas giant (Jupiter, Saturn): horizontal banded stripes with noise.

    Parameters can be tuned per planet:
      band_scale : how many bands appear   (Jupiter ~5, Saturn ~3)
      distortion : how wavy the bands are  (Jupiter very wavy ~9, Saturn calm ~2)
      contrast   : multiplier on light/dark colours (Jupiter ~1.3, Saturn ~0.8)
    """
    accent = tuple(min(c * (1.0 + 0.25 * contrast), 1.0) for c in base_color)
    dark   = tuple(c * (1.0 - 0.30 * contrast) for c in base_color)

    mat, nodes, links = _new_material(name)
    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-900, 0)

    # Wave texture with bands along the Z axis = perfect for planet stripes
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-650, 0)
    wave.wave_type = 'BANDS'
    if hasattr(wave, 'bands_direction'):
        wave.bands_direction = 'Z'
    wave.wave_profile = 'SIN'
    wave.inputs['Scale'].default_value = band_scale
    wave.inputs['Distortion'].default_value = distortion
    wave.inputs['Detail'].default_value = detail
    wave.inputs['Detail Scale'].default_value = 1.5
    links.new(coords.outputs['Generated'], wave.inputs['Vector'])

    # Three-color ramp for richer banding
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-350, 0)
    e = ramp.color_ramp.elements
    e[0].color = (*dark, 1.0)
    e[0].position = 0.0
    e[1].color = (*base_color, 1.0)
    e[1].position = 0.5
    e.new(0.85).color = (*accent, 1.0)
    links.new(wave.outputs['Fac'], ramp.inputs['Fac'])

    bsdf = _principled(nodes, x=0, roughness=0.50, specular=0.25)
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    out = _output(nodes, x=300)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_planet_material(name, base_color, material_type, style=None):
    """Dispatch helper — picks a procedural material by type.
    `style` is an optional dict of keyword overrides for the chosen material."""
    style = style or {}
    if material_type == "rocky":
        return make_rocky_material(name, base_color, **style)
    if material_type == "earth":
        return make_earth_material(name)
    if material_type == "venus":
        return make_venus_material(name, base_color)
    if material_type == "gas_giant":
        return make_gas_giant_material(name, base_color, **style)
    # Fallback to flat colour
    return make_material(name, base_color)


# ============================================================
#  Object builders
# ============================================================

def make_sun():
    bpy.ops.mesh.primitive_uv_sphere_add(radius=SUN_RADIUS, location=(0, 0, 0), segments=48, ring_count=24)
    sun = bpy.context.active_object
    sun.name = "Sun"
    bpy.ops.object.shade_smooth()
    sun.data.materials.append(make_sun_material("SunMaterial", SUN_COLOR, SUN_EMISSION_STRENGTH))
    # The point light lives at (0,0,0) inside the Sun mesh.  If the Sun
    # casts shadows it blocks that light from ever reaching the planets,
    # which is exactly the "all planets are black" symptom we hit.  Turn
    # off shadow casting on the Sun itself.
    try:
        sun.visible_shadow = False
    except AttributeError:
        pass
    # Cycles-specific shadow visibility (no-op under Eevee)
    if hasattr(sun, "cycles_visibility"):
        try:
            sun.cycles_visibility.shadow = False
        except AttributeError:
            pass
    return sun


def make_orbit_pivot(name):
    """Empty at the origin — children rotate around its Z axis."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    pivot = bpy.context.active_object
    pivot.name = name
    return pivot


def make_planet(name, radius, distance, color, material_type="rocky", style=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(distance, 0, 0), segments=48, ring_count=24)
    planet = bpy.context.active_object
    planet.name = name
    bpy.ops.object.shade_smooth()
    planet.data.materials.append(
        make_planet_material(f"{name}Material", color, material_type, style)
    )
    return planet


def make_saturn_ring(saturn):
    """Multi-band ring system around Saturn — inner B-ring, outer A-ring,
    and a faint outer dust band, separated by a Cassini-Division-style gap.
    Each band has a small emission component so it stays visible even when
    Saturn is partially in shadow."""
    saturn_radius = saturn.dimensions.x / 2.0   # ~1.2

    # (label, inner_mult, outer_mult, color, emission_strength)
    bands = [
        ("B",  1.35, 1.80, (0.80, 0.62, 0.40), 0.30),  # inner B-ring (darker)
        ("A",  1.95, 2.65, (0.95, 0.82, 0.58), 0.55),  # bright A-ring
        ("F",  2.78, 3.05, (0.88, 0.75, 0.55), 0.20),  # faint F-ring / dust
    ]

    for label, in_mul, out_mul, color, emi in bands:
        inner = saturn_radius * in_mul
        outer = saturn_radius * out_mul
        major = (inner + outer) / 2.0
        minor = (outer - inner) / 2.0

        # Important: create the torus at the WORLD ORIGIN, not at
        # saturn.location.  Then `band.parent = saturn` keeps the band
        # at Saturn's centre instead of doubling the offset.
        bpy.ops.mesh.primitive_torus_add(
            location=(0, 0, 0),
            major_radius=major,
            minor_radius=minor,
            major_segments=96,
            minor_segments=2,
        )
        band = bpy.context.active_object
        band.name = f"SaturnRing_{label}"
        bpy.ops.object.shade_smooth()

        # Parent first, THEN apply the band's local transform.  Because
        # the basis location is still (0,0,0), the band sits exactly at
        # Saturn's position with the chosen tilt and thickness.
        band.parent = saturn
        band.location = (0, 0, 0)
        band.rotation_euler = (math.radians(SATURN_RING_TILT_DEG + 6), 0, 0)
        band.scale.z = 0.025

        # Material — diffuse + slight emission so the ring stays visible.
        mat, nodes, links = _new_material(f"SaturnRing_{label}_Mat")
        bsdf = _principled(nodes, x=0, roughness=0.55, specular=0.25)
        safe_set_input(bsdf, ['Base Color'], (*color, 1.0))
        safe_set_input(bsdf, ['Emission Color', 'Emission'], (*color, 1.0))
        safe_set_input(bsdf, ['Emission Strength'], emi)
        out = _output(nodes, x=300)
        links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        band.data.materials.append(mat)

        try:
            band.visible_shadow = False
        except AttributeError:
            pass

    return saturn


# ============================================================
#  Orbit guide paths (thin emissive rings showing each planet's orbit)
# ============================================================

def make_orbit_path(distance):
    """Subtle glowing circle at the given orbital radius."""
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, 0),
        major_radius=distance,
        minor_radius=ORBIT_PATH_THICKNESS,
        major_segments=128,
        minor_segments=6,
    )
    orbit = bpy.context.active_object
    orbit.name = f"OrbitPath_{distance:.1f}"
    bpy.ops.object.shade_smooth()

    mat, nodes, links = _new_material(f"OrbitMat_{distance:.1f}")
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (0, 0)
    emission.inputs['Color'].default_value = (*ORBIT_PATH_COLOR, 1.0)
    emission.inputs['Strength'].default_value = ORBIT_PATH_STRENGTH
    out = _output(nodes, x=300)
    links.new(emission.outputs['Emission'], out.inputs['Surface'])
    orbit.data.materials.append(mat)

    # Orbit guides should never block light or cast shadows
    try:
        orbit.visible_shadow = False
    except AttributeError:
        pass

    return orbit


# ============================================================
#  Asteroid belt (between Mars and Jupiter)
# ============================================================

def make_asteroid_belt():
    """Spawn ASTEROID_COUNT small asteroids in a ring between the inner
    and outer belt radii. All asteroids share a single mesh + material for
    efficiency; they differ in position, scale and random rotation."""
    random.seed(ASTEROID_SEED)

    # Parent empty (lets us rotate the whole belt as a single orbit)
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    belt = bpy.context.active_object
    belt.name = "AsteroidBelt"

    # Build ONE template mesh, then instance it many times
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=1.0, subdivisions=ASTEROID_SUBDIVISIONS, location=(0, 0, 200),
    )
    template = bpy.context.active_object
    template_mesh = template.data
    template_mesh.name = "AsteroidMesh"
    template_mesh.use_fake_user = True  # keep the mesh alive after we delete the template object
    bpy.ops.object.shade_smooth()

    asteroid_mat = make_rocky_material(
        "AsteroidMaterial",
        (0.45, 0.40, 0.35),
        voronoi_scale=14.0, bump_strength=0.65, roughness=0.92,
    )
    template_mesh.materials.append(asteroid_mat)

    # Discard the template object — the mesh data lives on (fake_user)
    bpy.data.objects.remove(template, do_unlink=True)

    boulders = 0
    # Instance the mesh many times around the ring
    for i in range(ASTEROID_COUNT):
        angle  = random.uniform(0.0, 2.0 * math.pi)
        radius = random.uniform(ASTEROID_BELT_INNER, ASTEROID_BELT_OUTER)
        z      = random.uniform(-ASTEROID_BELT_HEIGHT, ASTEROID_BELT_HEIGHT)

        # Most are pebble-sized; a few are large "boulders" so the belt
        # is not a uniform-looking sand ring.
        if random.random() < ASTEROID_BOULDER_CHANCE:
            size = random.uniform(ASTEROID_BOULDER_MIN, ASTEROID_BOULDER_MAX)
            boulders += 1
        else:
            size = random.uniform(ASTEROID_SIZE_MIN, ASTEROID_SIZE_MAX)

        # Slight non-uniform scale on each axis -> shapes look like rocks,
        # not perfect spheres
        sx = size * random.uniform(0.85, 1.15)
        sy = size * random.uniform(0.85, 1.15)
        sz = size * random.uniform(0.85, 1.15)

        obj = bpy.data.objects.new(f"Asteroid_{i:03d}", template_mesh)
        bpy.context.collection.objects.link(obj)
        obj.location = (radius * math.cos(angle), radius * math.sin(angle), z)
        obj.scale = (sx, sy, sz)
        obj.rotation_euler = (
            random.uniform(0.0, 2.0 * math.pi),
            random.uniform(0.0, 2.0 * math.pi),
            random.uniform(0.0, 2.0 * math.pi),
        )
        obj.parent = belt

    log(f"  asteroid belt: {ASTEROID_COUNT} rocks ({boulders} boulders)")
    return belt


# ============================================================
#  Animation
# ============================================================

def _iter_fcurves(action):
    """Return all fcurves on an Action, supporting both the legacy API
    (Blender <= 4.3, `action.fcurves`) and the Slotted Actions API
    introduced in Blender 4.4 (`action.layers[].strips[].channelbags[].fcurves`)."""
    if action is None:
        return
    # Legacy API
    legacy = getattr(action, "fcurves", None)
    if legacy:
        for fc in legacy:
            yield fc
        return
    # Slotted Actions API
    for layer in getattr(action, "layers", []) or []:
        for strip in getattr(layer, "strips", []) or []:
            for channelbag in getattr(strip, "channelbags", []) or []:
                for fc in getattr(channelbag, "fcurves", []) or []:
                    yield fc


def animate_orbit(pivot, period_frames):
    """Rotate the pivot continuously over the whole animation range,
    completing one full turn every `period_frames` frames."""
    total_frames = ANIMATION_FRAMES
    final_angle = (total_frames / period_frames) * 2.0 * math.pi

    scene = bpy.context.scene

    scene.frame_set(1)
    pivot.rotation_euler = (0.0, 0.0, 0.0)
    pivot.keyframe_insert(data_path="rotation_euler", index=2, frame=1)

    scene.frame_set(total_frames)
    pivot.rotation_euler = (0.0, 0.0, final_angle)
    pivot.keyframe_insert(data_path="rotation_euler", index=2, frame=total_frames)

    # Constant angular velocity: linear interpolation between the two keyframes.
    if pivot.animation_data is None:
        return
    for fcurve in _iter_fcurves(pivot.animation_data.action):
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'


# ============================================================
#  Lighting + Camera
# ============================================================

def add_sun_light():
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    light = bpy.context.active_object
    light.name = "SunLight"
    light.data.energy = SUN_LIGHT_ENERGY
    light.data.color = SUN_LIGHT_COLOR
    light.data.shadow_soft_size = 1.5
    return light


def add_camera():
    bpy.ops.object.camera_add(location=CAMERA_LOCATION)
    cam = bpy.context.active_object
    cam.name = "MainCamera"

    # "Track To" constraint keeps the camera pointing at the origin
    target = bpy.data.objects.new("CameraTarget", None)
    target.location = CAMERA_TARGET
    bpy.context.collection.objects.link(target)

    track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    bpy.context.scene.camera = cam
    return cam


# ============================================================
#  World + Render setup
# ============================================================

def setup_starfield_world(scene):
    """Procedural star field rendered into the world background.

    The approach: a Voronoi F1 distance texture gives perfectly distributed
    point features.  A ColorRamp keeps only the tiny disc around each
    feature point — those become stars.  Their brightness is added on top
    of the deep-space background colour."""
    if scene.world is None:
        scene.world = bpy.data.worlds.new("SolarWorld")
    world = scene.world
    world.use_nodes = True

    nodes = world.node_tree.nodes
    links = world.node_tree.links
    for node in list(nodes):
        nodes.remove(node)

    coords = nodes.new('ShaderNodeTexCoord')
    coords.location = (-1000, 0)

    # Voronoi F1 — distance to the nearest feature point
    voronoi = nodes.new('ShaderNodeTexVoronoi')
    voronoi.location = (-800, 0)
    voronoi.feature = 'F1'
    voronoi.inputs['Scale'].default_value = STARFIELD_DENSITY
    links.new(coords.outputs['Generated'], voronoi.inputs['Vector'])

    # Threshold: only the centre of each cell becomes a star.  Larger
    # STARFIELD_SIZE makes the visible star discs bigger.
    star_ramp = nodes.new('ShaderNodeValToRGB')
    star_ramp.location = (-550, 0)
    star_ramp.color_ramp.elements[0].position = 0.00
    star_ramp.color_ramp.elements[1].position = STARFIELD_SIZE
    star_ramp.color_ramp.elements[0].color = (STARFIELD_BRIGHTNESS,
                                              STARFIELD_BRIGHTNESS,
                                              STARFIELD_BRIGHTNESS, 1.0)
    star_ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    links.new(voronoi.outputs['Distance'], star_ramp.inputs['Fac'])

    # Deep-space background colour
    bg_color = nodes.new('ShaderNodeRGB')
    bg_color.location = (-550, 250)
    bg_color.outputs[0].default_value = WORLD_BACKGROUND_COLOR

    # Add stars on top of the background
    add = nodes.new('ShaderNodeMixRGB')
    add.location = (-250, 100)
    add.blend_type = 'ADD'
    add.inputs['Fac'].default_value = 1.0
    links.new(bg_color.outputs[0], add.inputs['Color1'])
    links.new(star_ramp.outputs['Color'], add.inputs['Color2'])

    bg = nodes.new('ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = 1.0
    links.new(add.outputs['Color'], bg.inputs['Color'])

    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (250, 0)
    links.new(bg.outputs['Background'], out.inputs['Surface'])


def setup_world_and_render():
    scene = bpy.context.scene

    # Render engine — prefer Eevee Next (Blender 4.2+), fall back gracefully
    for engine in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE', 'CYCLES'):
        try:
            scene.render.engine = engine
            log(f"render engine = {engine}")
            break
        except TypeError:
            continue

    scene.render.resolution_x = RENDER_RESOLUTION_X
    scene.render.resolution_y = RENDER_RESOLUTION_Y
    scene.render.resolution_percentage = 100

    # Background — either procedural starfield, or plain dark colour
    if STARFIELD_ENABLE:
        setup_starfield_world(scene)
    else:
        if scene.world is None:
            scene.world = bpy.data.worlds.new("SolarWorld")
        world = scene.world
        world.use_nodes = True
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[0].default_value = WORLD_BACKGROUND_COLOR
            bg.inputs[1].default_value = 1.0

    # Animation range
    scene.frame_start = 1
    scene.frame_end = ANIMATION_FRAMES
    scene.frame_set(RENDER_FRAME)


def render_still():
    output = os.path.join(script_directory(), RENDER_OUTPUT_NAME)
    bpy.context.scene.render.filepath = output
    log(f"rendering frame {bpy.context.scene.frame_current} -> {output}")
    bpy.ops.render.render(write_still=True)
    return output


def _find_ffmpeg():
    """Locate the ffmpeg executable.  Checks (in order):
      1. system PATH,
      2. system Python's `imageio-ffmpeg` bundled binary,
      3. a hand-curated list of common Windows install locations.
    Returns the full path or None."""
    import shutil
    p = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if p:
        return p

    # Ask the SYSTEM python where imageio-ffmpeg keeps its bundled binary.
    # Blender ships its own Python; we want the user's main interpreter.
    import subprocess
    for py in ("python", "python.exe", "python3"):
        try:
            r = subprocess.run(
                [py, "-c",
                 "import imageio_ffmpeg, sys; sys.stdout.write(imageio_ffmpeg.get_ffmpeg_exe())"],
                capture_output=True, text=True, timeout=8,
            )
            cand = r.stdout.strip()
            if r.returncode == 0 and cand and os.path.isfile(cand):
                return cand
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None


def render_animation():
    """Render the orbit animation as an H.264 .mp4 video.

    Blender 5.x removed FFMPEG from `image_settings.file_format`, so we
    always render a PNG sequence first and then combine the frames into
    a video with an external ffmpeg binary (system PATH or the one
    bundled with the `imageio-ffmpeg` Python package).

    Slow — expect several minutes in Eevee Next, much longer in Cycles."""
    scene = bpy.context.scene
    scene.render.fps = ANIMATION_FPS

    out_dir = script_directory()
    frames_dir = os.path.join(out_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Use PNG sequence (works in EVERY Blender version, incl. 5.x).
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    # The "####" suffix forces Blender to zero-pad the frame index to 4
    # digits, so files become frame_0001.png … frame_0240.png — that
    # matches the ffmpeg "%04d" input pattern used below.
    scene.render.filepath = os.path.join(frames_dir, "frame_####")

    total = scene.frame_end - scene.frame_start + 1
    log(f"rendering {total} frames @ {ANIMATION_FPS} fps "
        f"({total / ANIMATION_FPS:.1f} s) as a PNG sequence")
    log(f"  frames dir : {frames_dir}")
    log("  (this is slow — expect several minutes)")
    bpy.ops.render.render(animation=True)
    log(f"PNG render complete: {total} frames")

    # Encode the PNGs into a single H.264 MP4 with ffmpeg.
    mp4_path = os.path.join(out_dir, ANIMATION_OUTPUT_NAME + ".mp4")
    ffmpeg = _find_ffmpeg()
    if not ffmpeg:
        log("")
        log("WARNING: ffmpeg not found — animation.mp4 was NOT created.")
        log(f"PNG frames are ready in: {frames_dir}")
        log("Install ffmpeg, then run:")
        log(f'  ffmpeg -framerate {ANIMATION_FPS} '
            f'-i "{frames_dir}\\frame_%04d.png" '
            f'-c:v libx264 -pix_fmt yuv420p "{mp4_path}"')
        log("Easy install:  pip install imageio-ffmpeg")
        log("       or:     winget install --id=Gyan.FFmpeg")
        return frames_dir

    log(f"encoding video with: {ffmpeg}")
    import subprocess
    cmd = [
        ffmpeg, "-y",
        "-framerate", str(ANIMATION_FPS),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        mp4_path,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode == 0:
            log(f"animation.mp4 written: {mp4_path}")
            return mp4_path
        log(f"ffmpeg failed (exit code {r.returncode}):")
        log(r.stderr[-500:] if r.stderr else "(no stderr)")
    except Exception as exc:
        log(f"ffmpeg call raised: {exc}")

    log(f"PNG frames are still available at: {frames_dir}")
    return frames_dir


# ============================================================
#  Main
# ============================================================

def main():
    log("=" * 50)
    log("Procedural Solar System")
    log("=" * 50)

    clear_scene()
    log("scene cleared")

    make_sun()
    log(f"Sun (r={SUN_RADIUS}) created with emission shader")

    for name, radius, distance, color, period, mat_type, style in PLANETS:
        pivot = make_orbit_pivot(f"{name}_OrbitPivot")
        planet = make_planet(name, radius, distance, color, mat_type, style)
        planet.parent = pivot
        animate_orbit(pivot, period)
        if name == "Saturn":
            make_saturn_ring(planet)
        if ORBIT_PATHS_ENABLE:
            make_orbit_path(distance)
        log(f"  {name:8s}  r={radius}  d={distance:4.1f}  period={period:3d} frames  mat={mat_type}")

    if ASTEROID_BELT_ENABLE:
        belt = make_asteroid_belt()
        animate_orbit(belt, ASTEROID_BELT_PERIOD)
        log(f"  AsteroidBelt  {ASTEROID_COUNT} rocks, r=[{ASTEROID_BELT_INNER}, {ASTEROID_BELT_OUTER}], period={ASTEROID_BELT_PERIOD}")

    add_sun_light()
    add_camera()
    setup_world_and_render()
    if STARFIELD_ENABLE:
        log(f"  Starfield enabled (density={STARFIELD_DENSITY})")

    if RENDER_MODE == 'still':
        try:
            render_still()
            log("render finished — check render.png next to this script")
        except Exception as exc:
            log(f"render skipped: {exc}")
            log("scene was built successfully — you can render manually with F12")
    elif RENDER_MODE == 'animation':
        try:
            out = render_animation()
            log(f"animation finished — {out}")
        except Exception as exc:
            log(f"animation render skipped: {exc}")
    else:
        log("render skipped (RENDER_MODE = 'none') — press F12 to render manually")

    log("done — press SPACE in the viewport to play the orbits")
    log("=" * 50)


if __name__ == "__main__":
    main()
