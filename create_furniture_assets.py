"""
Furniture Asset Generator
Creates realistic 3D furniture models and exports them as GLB files
"""

import trimesh
import numpy as np
from pathlib import Path

# Output directory
FURNITURE_DIR = Path("assets/furniture")
FURNITURE_DIR.mkdir(parents=True, exist_ok=True)

print("🛋️ Creating 3D Furniture Assets...")
print(f"Output directory: {FURNITURE_DIR}")
print("=" * 60)

# ============================================================================
# BEDROOM FURNITURE
# ============================================================================

def create_bed():
    """Create a king-size bed with base, mattress, and headboard"""
    print("Creating bed...")
    
    # Base (bed frame)
    base = trimesh.creation.box(extents=[200, 40, 180])
    base.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown wood
    base.apply_translation([0, 20, 0])
    
    # Mattress
    mattress = trimesh.creation.box(extents=[190, 30, 170])
    mattress.visual.vertex_colors = [240, 240, 240, 255]  # White
    mattress.apply_translation([0, 55, 0])
    
    # Headboard
    headboard = trimesh.creation.box(extents=[200, 100, 10])
    headboard.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown wood
    headboard.apply_translation([0, 90, -90])
    
    # Pillows (2)
    pillow1 = trimesh.creation.box(extents=[40, 15, 30])
    pillow1.visual.vertex_colors = [255, 255, 255, 255]  # White
    pillow1.apply_translation([-50, 77, -60])
    
    pillow2 = trimesh.creation.box(extents=[40, 15, 30])
    pillow2.visual.vertex_colors = [255, 255, 255, 255]  # White
    pillow2.apply_translation([50, 77, -60])
    
    return trimesh.util.concatenate([base, mattress, headboard, pillow1, pillow2])


def create_nightstand():
    """Create a bedside nightstand"""
    print("Creating nightstand...")
    
    # Main body
    body = trimesh.creation.box(extents=[50, 60, 40])
    body.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    body.apply_translation([0, 30, 0])
    
    # Drawer (visual detail)
    drawer = trimesh.creation.box(extents=[45, 15, 5])
    drawer.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
    drawer.apply_translation([0, 35, 22])
    
    # Knob
    knob = trimesh.creation.cylinder(radius=2, height=3)
    knob.visual.vertex_colors = [192, 192, 192, 255]  # Silver
    knob.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    knob.apply_translation([0, 35, 25])
    
    return trimesh.util.concatenate([body, drawer, knob])


def create_wardrobe():
    """Create a wardrobe/closet"""
    print("Creating wardrobe...")
    
    # Main body
    body = trimesh.creation.box(extents=[150, 200, 60])
    body.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
    body.apply_translation([0, 100, 0])
    
    # Doors (2)
    door1 = trimesh.creation.box(extents=[73, 195, 5])
    door1.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    door1.apply_translation([-37, 100, 32])
    
    door2 = trimesh.creation.box(extents=[73, 195, 5])
    door2.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    door2.apply_translation([37, 100, 32])
    
    # Handles
    handle1 = trimesh.creation.cylinder(radius=2, height=20)
    handle1.visual.vertex_colors = [192, 192, 192, 255]  # Silver
    handle1.apply_translation([-20, 100, 35])
    
    handle2 = trimesh.creation.cylinder(radius=2, height=20)
    handle2.visual.vertex_colors = [192, 192, 192, 255]  # Silver
    handle2.apply_translation([20, 100, 35])
    
    return trimesh.util.concatenate([body, door1, door2, handle1, handle2])


# ============================================================================
# LIVING ROOM FURNITURE
# ============================================================================

def create_sofa():
    """Create a 3-seater sofa"""
    print("Creating sofa...")
    
    # Seat
    seat = trimesh.creation.box(extents=[180, 50, 80])
    seat.visual.vertex_colors = [70, 70, 90, 255]  # Dark blue-gray
    seat.apply_translation([0, 25, 0])
    
    # Backrest
    backrest = trimesh.creation.box(extents=[180, 80, 20])
    backrest.visual.vertex_colors = [70, 70, 90, 255]  # Dark blue-gray
    backrest.apply_translation([0, 65, -40])
    
    # Left armrest
    armrest_l = trimesh.creation.box(extents=[20, 60, 80])
    armrest_l.visual.vertex_colors = [70, 70, 90, 255]  # Dark blue-gray
    armrest_l.apply_translation([-90, 30, 0])
    
    # Right armrest
    armrest_r = trimesh.creation.box(extents=[20, 60, 80])
    armrest_r.visual.vertex_colors = [70, 70, 90, 255]  # Dark blue-gray
    armrest_r.apply_translation([90, 30, 0])
    
    # Cushions (3)
    cushions = []
    for i in range(3):
        cushion = trimesh.creation.box(extents=[55, 15, 60])
        cushion.visual.vertex_colors = [90, 90, 110, 255]  # Lighter blue-gray
        cushion.apply_translation([-60 + i*60, 57, 0])
        cushions.append(cushion)
    
    return trimesh.util.concatenate([seat, backrest, armrest_l, armrest_r] + cushions)


def create_armchair():
    """Create a single armchair"""
    print("Creating armchair...")
    
    # Seat
    seat = trimesh.creation.box(extents=[80, 50, 80])
    seat.visual.vertex_colors = [139, 69, 19, 255]  # Saddle brown
    seat.apply_translation([0, 25, 0])
    
    # Backrest
    backrest = trimesh.creation.box(extents=[80, 80, 20])
    backrest.visual.vertex_colors = [139, 69, 19, 255]  # Saddle brown
    backrest.apply_translation([0, 65, -40])
    
    # Left armrest
    armrest_l = trimesh.creation.box(extents=[20, 60, 80])
    armrest_l.visual.vertex_colors = [139, 69, 19, 255]  # Saddle brown
    armrest_l.apply_translation([-40, 30, 0])
    
    # Right armrest
    armrest_r = trimesh.creation.box(extents=[20, 60, 80])
    armrest_r.visual.vertex_colors = [139, 69, 19, 255]  # Saddle brown
    armrest_r.apply_translation([40, 30, 0])
    
    return trimesh.util.concatenate([seat, backrest, armrest_l, armrest_r])


def create_coffee_table():
    """Create a coffee table"""
    print("Creating coffee table...")
    
    # Tabletop
    top = trimesh.creation.box(extents=[120, 10, 60])
    top.visual.vertex_colors = [160, 82, 45, 255]  # Sienna
    top.apply_translation([0, 45, 0])
    
    # Legs (4)
    legs = []
    positions = [[-55, 22, -25], [55, 22, -25], [-55, 22, 25], [55, 22, 25]]
    for pos in positions:
        leg = trimesh.creation.cylinder(radius=3, height=40)
        leg.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
        leg.apply_translation(pos)
        legs.append(leg)
    
    return trimesh.util.concatenate([top] + legs)


def create_tv_stand():
    """Create a TV stand"""
    print("Creating TV stand...")
    
    # Main body
    body = trimesh.creation.box(extents=[150, 50, 40])
    body.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
    body.apply_translation([0, 25, 0])
    
    # Shelves (visual)
    shelf1 = trimesh.creation.box(extents=[145, 3, 38])
    shelf1.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    shelf1.apply_translation([0, 15, 0])
    
    shelf2 = trimesh.creation.box(extents=[145, 3, 38])
    shelf2.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    shelf2.apply_translation([0, 35, 0])
    
    return trimesh.util.concatenate([body, shelf1, shelf2])


# ============================================================================
# DINING ROOM FURNITURE
# ============================================================================

def create_dining_table():
    """Create a dining table"""
    print("Creating dining table...")
    
    # Tabletop
    top = trimesh.creation.box(extents=[180, 10, 100])
    top.visual.vertex_colors = [160, 82, 45, 255]  # Sienna
    top.apply_translation([0, 75, 0])
    
    # Legs (4)
    legs = []
    positions = [[-85, 37, -45], [85, 37, -45], [-85, 37, 45], [85, 37, 45]]
    for pos in positions:
        leg = trimesh.creation.cylinder(radius=5, height=70)
        leg.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
        leg.apply_translation(pos)
        legs.append(leg)
    
    return trimesh.util.concatenate([top] + legs)


def create_dining_chair():
    """Create a dining chair"""
    print("Creating dining chair...")
    
    # Seat
    seat = trimesh.creation.box(extents=[45, 8, 45])
    seat.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    seat.apply_translation([0, 45, 0])
    
    # Backrest
    backrest = trimesh.creation.box(extents=[45, 50, 8])
    backrest.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    backrest.apply_translation([0, 70, -20])
    
    # Legs (4)
    legs = []
    positions = [[-18, 22, -18], [18, 22, -18], [-18, 22, 18], [18, 22, 18]]
    for pos in positions:
        leg = trimesh.creation.cylinder(radius=2, height=40)
        leg.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
        leg.apply_translation(pos)
        legs.append(leg)
    
    return trimesh.util.concatenate([seat, backrest] + legs)


# ============================================================================
# KITCHEN FURNITURE
# ============================================================================

def create_kitchen_counter():
    """Create a kitchen counter"""
    print("Creating kitchen counter...")
    
    # Counter base
    base = trimesh.creation.box(extents=[200, 90, 60])
    base.visual.vertex_colors = [245, 245, 220, 255]  # Beige
    base.apply_translation([0, 45, 0])
    
    # Countertop
    top = trimesh.creation.box(extents=[205, 5, 65])
    top.visual.vertex_colors = [105, 105, 105, 255]  # Dim gray (granite)
    top.apply_translation([0, 92, 0])
    
    return trimesh.util.concatenate([base, top])


def create_refrigerator():
    """Create a refrigerator"""
    print("Creating refrigerator...")
    
    # Main body
    body = trimesh.creation.box(extents=[80, 180, 70])
    body.visual.vertex_colors = [220, 220, 220, 255]  # Light gray
    body.apply_translation([0, 90, 0])
    
    # Freezer door (top)
    freezer = trimesh.creation.box(extents=[78, 60, 5])
    freezer.visual.vertex_colors = [200, 200, 200, 255]  # Slightly darker
    freezer.apply_translation([0, 145, 37])
    
    # Fridge door (bottom)
    fridge = trimesh.creation.box(extents=[78, 115, 5])
    fridge.visual.vertex_colors = [200, 200, 200, 255]  # Slightly darker
    fridge.apply_translation([0, 60, 37])
    
    # Handles
    handle1 = trimesh.creation.cylinder(radius=1.5, height=30)
    handle1.visual.vertex_colors = [128, 128, 128, 255]  # Gray
    handle1.apply_translation([35, 145, 40])
    
    handle2 = trimesh.creation.cylinder(radius=1.5, height=50)
    handle2.visual.vertex_colors = [128, 128, 128, 255]  # Gray
    handle2.apply_translation([35, 60, 40])
    
    return trimesh.util.concatenate([body, freezer, fridge, handle1, handle2])


def create_stove():
    """Create a stove/oven"""
    print("Creating stove...")
    
    # Main body
    body = trimesh.creation.box(extents=[80, 90, 60])
    body.visual.vertex_colors = [50, 50, 50, 255]  # Dark gray
    body.apply_translation([0, 45, 0])
    
    # Cooktop
    top = trimesh.creation.box(extents=[80, 5, 60])
    top.visual.vertex_colors = [30, 30, 30, 255]  # Very dark gray
    top.apply_translation([0, 92, 0])
    
    # Burners (4)
    burners = []
    positions = [[-20, 95, -15], [20, 95, -15], [-20, 95, 15], [20, 95, 15]]
    for pos in positions:
        burner = trimesh.creation.cylinder(radius=8, height=2)
        burner.visual.vertex_colors = [0, 0, 0, 255]  # Black
        burner.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
        burner.apply_translation(pos)
        burners.append(burner)
    
    # Oven door
    door = trimesh.creation.box(extents=[75, 50, 5])
    door.visual.vertex_colors = [70, 70, 70, 255]  # Medium gray
    door.apply_translation([0, 30, 32])
    
    return trimesh.util.concatenate([body, top] + burners + [door])


# ============================================================================
# BATHROOM FURNITURE
# ============================================================================

def create_toilet():
    """Create a toilet"""
    print("Creating toilet...")
    
    # Bowl base
    base = trimesh.creation.cylinder(radius=20, height=40)
    base.visual.vertex_colors = [255, 255, 255, 255]  # White
    base.apply_translation([0, 20, 10])
    
    # Bowl seat
    seat = trimesh.creation.cylinder(radius=18, height=5)
    seat.visual.vertex_colors = [255, 255, 255, 255]  # White
    seat.apply_translation([0, 42, 10])
    
    # Tank
    tank = trimesh.creation.box(extents=[35, 50, 20])
    tank.visual.vertex_colors = [255, 255, 255, 255]  # White
    tank.apply_translation([0, 45, -15])
    
    return trimesh.util.concatenate([base, seat, tank])


def create_sink():
    """Create a bathroom sink"""
    print("Creating sink...")
    
    # Basin
    basin = trimesh.creation.cylinder(radius=25, height=15)
    basin.visual.vertex_colors = [255, 255, 255, 255]  # White
    basin.apply_translation([0, 85, 0])
    
    # Pedestal
    pedestal = trimesh.creation.cylinder(radius=15, height=80, sections=8)
    pedestal.visual.vertex_colors = [255, 255, 255, 255]  # White
    pedestal.apply_translation([0, 40, 0])
    
    # Faucet
    faucet = trimesh.creation.cylinder(radius=2, height=20)
    faucet.visual.vertex_colors = [192, 192, 192, 255]  # Silver
    faucet.apply_translation([0, 100, -15])
    
    return trimesh.util.concatenate([basin, pedestal, faucet])


def create_bathtub():
    """Create a bathtub"""
    print("Creating bathtub...")
    
    # Main tub
    tub = trimesh.creation.box(extents=[150, 60, 70])
    tub.visual.vertex_colors = [255, 255, 255, 255]  # White
    tub.apply_translation([0, 30, 0])
    
    # Rim
    rim = trimesh.creation.box(extents=[155, 5, 75])
    rim.visual.vertex_colors = [245, 245, 245, 255]  # Off-white
    rim.apply_translation([0, 62, 0])
    
    return trimesh.util.concatenate([tub, rim])


def create_shower():
    """Create a shower stall"""
    print("Creating shower...")
    
    # Base
    base = trimesh.creation.box(extents=[90, 10, 90])
    base.visual.vertex_colors = [255, 255, 255, 255]  # White
    base.apply_translation([0, 5, 0])
    
    # Walls (3 sides)
    wall1 = trimesh.creation.box(extents=[90, 200, 5])
    wall1.visual.vertex_colors = [200, 200, 200, 100]  # Translucent glass
    wall1.apply_translation([0, 100, -45])
    
    wall2 = trimesh.creation.box(extents=[5, 200, 90])
    wall2.visual.vertex_colors = [200, 200, 200, 100]  # Translucent glass
    wall2.apply_translation([-45, 100, 0])
    
    wall3 = trimesh.creation.box(extents=[5, 200, 90])
    wall3.visual.vertex_colors = [200, 200, 200, 100]  # Translucent glass
    wall3.apply_translation([45, 100, 0])
    
    # Showerhead
    head = trimesh.creation.cylinder(radius=8, height=3)
    head.visual.vertex_colors = [192, 192, 192, 255]  # Silver
    head.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    head.apply_translation([0, 180, -35])
    
    return trimesh.util.concatenate([base, wall1, wall2, wall3, head])


# ============================================================================
# OFFICE FURNITURE
# ============================================================================

def create_desk():
    """Create an office desk"""
    print("Creating desk...")
    
    # Desktop
    top = trimesh.creation.box(extents=[140, 5, 70])
    top.visual.vertex_colors = [160, 82, 45, 255]  # Sienna
    top.apply_translation([0, 75, 0])
    
    # Legs (4)
    legs = []
    positions = [[-65, 37, -30], [65, 37, -30], [-65, 37, 30], [65, 37, 30]]
    for pos in positions:
        leg = trimesh.creation.cylinder(radius=3, height=70)
        leg.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
        leg.apply_translation(pos)
        legs.append(leg)
    
    # Drawer unit (right side)
    drawer_unit = trimesh.creation.box(extents=[40, 50, 50])
    drawer_unit.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
    drawer_unit.apply_translation([50, 50, 0])
    
    return trimesh.util.concatenate([top] + legs + [drawer_unit])


def create_office_chair():
    """Create an office chair"""
    print("Creating office chair...")
    
    # Seat
    seat = trimesh.creation.cylinder(radius=25, height=10)
    seat.visual.vertex_colors = [50, 50, 50, 255]  # Dark gray
    seat.apply_translation([0, 50, 0])
    
    # Backrest
    backrest = trimesh.creation.box(extents=[45, 60, 10])
    backrest.visual.vertex_colors = [50, 50, 50, 255]  # Dark gray
    backrest.apply_translation([0, 75, -20])
    
    # Base (5-star)
    base_center = trimesh.creation.cylinder(radius=5, height=10)
    base_center.visual.vertex_colors = [128, 128, 128, 255]  # Gray
    base_center.apply_translation([0, 35, 0])
    
    # Pneumatic cylinder
    cylinder = trimesh.creation.cylinder(radius=3, height=30)
    cylinder.visual.vertex_colors = [128, 128, 128, 255]  # Gray
    cylinder.apply_translation([0, 20, 0])
    
    # Wheels (5)
    wheels = []
    for i in range(5):
        angle = i * (2 * np.pi / 5)
        x = 20 * np.cos(angle)
        z = 20 * np.sin(angle)
        wheel = trimesh.creation.cylinder(radius=3, height=5)
        wheel.visual.vertex_colors = [64, 64, 64, 255]  # Dark gray
        wheel.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
        wheel.apply_translation([x, 5, z])
        wheels.append(wheel)
    
    return trimesh.util.concatenate([seat, backrest, base_center, cylinder] + wheels)


def create_bookshelf():
    """Create a bookshelf"""
    print("Creating bookshelf...")
    
    # Main frame
    frame = trimesh.creation.box(extents=[100, 180, 30])
    frame.visual.vertex_colors = [101, 67, 33, 255]  # Dark brown
    frame.apply_translation([0, 90, 0])
    
    # Shelves (4)
    shelves = []
    for i in range(5):
        shelf = trimesh.creation.box(extents=[95, 3, 28])
        shelf.visual.vertex_colors = [139, 90, 43, 255]  # Medium brown
        shelf.apply_translation([0, i * 45, 0])
        shelves.append(shelf)
    
    return trimesh.util.concatenate([frame] + shelves)


# ============================================================================
# EXPORT ALL FURNITURE
# ============================================================================

furniture_creators = {
    'bed': create_bed,
    'nightstand': create_nightstand,
    'wardrobe': create_wardrobe,
    'sofa': create_sofa,
    'armchair': create_armchair,
    'coffee_table': create_coffee_table,
    'tv_stand': create_tv_stand,
    'dining_table': create_dining_table,
    'dining_chair': create_dining_chair,
    'kitchen_counter': create_kitchen_counter,
    'refrigerator': create_refrigerator,
    'stove': create_stove,
    'toilet': create_toilet,
    'sink': create_sink,
    'bathtub': create_bathtub,
    'shower': create_shower,
    'desk': create_desk,
    'office_chair': create_office_chair,
    'bookshelf': create_bookshelf,
}

print("\n🎨 Generating furniture models...")
print("=" * 60)

for name, creator_func in furniture_creators.items():
    try:
        mesh = creator_func()
        output_path = FURNITURE_DIR / f"{name}.glb"
        mesh.export(str(output_path))
        file_size = output_path.stat().st_size / 1024  # KB
        print(f"  ✅ {name}.glb ({file_size:.1f} KB)")
    except Exception as e:
        print(f"  ❌ {name}.glb - Error: {e}")

print("\n" + "=" * 60)
print(f"✨ Furniture asset generation complete!")
print(f"📁 Assets saved to: {FURNITURE_DIR.absolute()}")
print(f"📊 Total files: {len(list(FURNITURE_DIR.glob('*.glb')))}")
