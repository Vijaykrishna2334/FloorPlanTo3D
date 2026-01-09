"""
Enhanced 3D Floor Plan Generator with Realistic GLB Models
Exactly matching the Bringing_Floor_Plans_to_Life_with_AI notebook implementation
Generates a complete 3D building model from floor plan detection data
"""

import json
import numpy as np
import trimesh
import os
from pathlib import Path

# Configuration - matching notebook
FLOOR_THICKNESS = 5  # Increased for better visibility
WALL_HEIGHT = 300
WALL_THICKNESS = 15
SNAP_THRESHOLD = 20.0
GRID_SNAP_THRESHOLD = 15.0

# Asset paths
ASSETS_DIR = Path("assets")
DOOR_PATH = ASSETS_DIR / "door.glb"
WINDOW_PATH = ASSETS_DIR / "window.glb"
WALL_PATH = ASSETS_DIR / "wall.glb"
CARPET_PATH = ASSETS_DIR / "carpet.glb"
RAIL_PATH = ASSETS_DIR / "rail.glb"

# Furniture asset paths
FURNITURE_DIR = ASSETS_DIR / "furniture"
FURNITURE_ASSETS = {
    'bed': FURNITURE_DIR / "bed.glb",
    'nightstand': FURNITURE_DIR / "nightstand.glb",
    'wardrobe': FURNITURE_DIR / "wardrobe.glb",
    'sofa': FURNITURE_DIR / "sofa.glb",
    'armchair': FURNITURE_DIR / "armchair.glb",
    'coffee_table': FURNITURE_DIR / "coffee_table.glb",
    'tv_stand': FURNITURE_DIR / "tv_stand.glb",
    'dining_table': FURNITURE_DIR / "dining_table.glb",
    'dining_chair': FURNITURE_DIR / "dining_chair.glb",
    'chair': FURNITURE_DIR / "dining_chair.glb",  # Alias
    'table': FURNITURE_DIR / "dining_table.glb",  # Alias
    'kitchen_counter': FURNITURE_DIR / "kitchen_counter.glb",
    'refrigerator': FURNITURE_DIR / "refrigerator.glb",
    'fridge': FURNITURE_DIR / "refrigerator.glb",  # Alias
    'stove': FURNITURE_DIR / "stove.glb",
    'oven': FURNITURE_DIR / "stove.glb",  # Alias
    'toilet': FURNITURE_DIR / "toilet.glb",
    'sink': FURNITURE_DIR / "sink.glb",
    'bathtub': FURNITURE_DIR / "bathtub.glb",
    'shower': FURNITURE_DIR / "shower.glb",
    'desk': FURNITURE_DIR / "desk.glb",
    'office_chair': FURNITURE_DIR / "office_chair.glb",
    'bookshelf': FURNITURE_DIR / "bookshelf.glb",
}

# Furniture colors (placeholders)
FURNITURE_COLORS = {
    'bed': [65, 105, 225, 255],      # Royal Blue
    'sofa': [139, 69, 19, 255],      # Saddle Brown
    'table': [222, 184, 135, 255],   # Burlywood
    'chair': [160, 82, 45, 255],     # Sienna
    'toilet': [255, 255, 255, 255],  # White
    'sink': [240, 248, 255, 255],    # Alice Blue
    'default': [128, 128, 128, 255]  # Gray
}



def axis_snap_all_endpoints(data, threshold=5.0):
    """Grid-align all endpoints within threshold"""
    # Initialize lists to store x and y coordinates
    x_vals, y_vals = [], []
    for p in data['points']:
        x_vals += [p['x1'], p['x2']]
        y_vals += [p['y1'], p['y2']]

    # Function to group and snap coordinates within a threshold
    def snap_group(coords):
        coords = sorted(set(coords))
        groups, group = [], [coords[0]]
        for c in coords[1:]:
            if abs(c - group[-1]) <= threshold:
                group.append(c)
            else:
                groups.append(group)
                group = [c]
        groups.append(group)
        # Return the average of each group as the snapped value
        return {val: sum(g) / len(g) for g in groups for val in g}

    snap_x = snap_group(x_vals)
    snap_y = snap_group(y_vals)

    # Update each point with the snapped coordinates
    for p in data['points']:
        p['x1'] = snap_x.get(p['x1'], p['x1'])
        p['x2'] = snap_x.get(p['x2'], p['x2'])
        p['y1'] = snap_y.get(p['y1'], p['y1'])
        p['y2'] = snap_y.get(p['y2'], p['y2'])


def snap_doors_windows_to_walls(data, threshold=20.0):
    """Snap door/window endpoints to nearest wall endpoints"""
    snap_e, ref_e = [], []

    # Separate snap candidates (doors/windows) from references (walls, etc.)
    for idx, (cls, pt) in enumerate(zip(data['classes'], data['points'])):
        name = cls['name'].lower()
        entries = [('x1', 'y1', pt['x1'], pt['y1']), ('x2', 'y2', pt['x2'], pt['y2'])]
        if name in ['door', 'window']:
            for e in entries:
                snap_e.append((idx, *e))
        else:
            for e in entries:
                ref_e.append((idx, *e))

    # Snap close door/window points to nearest wall point
    for s_idx, sxk, syk, sx, sy in snap_e:
        for r_idx, rxk, ryk, rx, ry in ref_e:
            if np.hypot(sx - rx, sy - ry) < threshold:
                data['points'][s_idx][sxk] = rx
                data['points'][s_idx][syk] = ry
                break


def create_floor_mesh(data, floor_thickness, carpet_path):
    """Create floor mesh with optional carpet texture"""
    # Always use simple floor (carpet GLB has memory issues)
    all_x, all_z = [], []
    for p in data['points']:
        all_x += [p['x1'], p['x2']]
        all_z += [p['y1'], p['y2']]
    min_x, max_x = min(all_x), max(all_x)
    min_z, max_z = min(all_z), max(all_z)

    margin = 10.0
    width = (max_x - min_x) + 2 * margin
    depth = (max_z - min_z) + 2 * margin

    # Create floor box with increased thickness for visibility
    floor = trimesh.creation.box(extents=[width, floor_thickness, depth])
    floor.visual.vertex_colors = [220, 220, 220, 255]  # Light gray floor
    
    # Position floor at y=0 (ground level)
    floor.apply_translation([
        (min_x + max_x) / 2,
        0,  # Floor at ground level
        (min_z + max_z) / 2
    ])
    return floor


def create_procedural_furniture(name, width, height, depth, color):
    """Create a procedural furniture mesh based on type"""
    name = name.lower()
    
    if 'bed' in name:
        # Bed: Base + Mattress + Pillow
        base_h = height * 0.3
        mattress_h = height * 0.5
        
        # Base
        base = trimesh.creation.box(extents=[width, base_h, depth])
        base.visual.vertex_colors = [139, 69, 19, 255] # Wood
        base.apply_translation([0, base_h/2, 0])
        
        # Mattress
        mattress = trimesh.creation.box(extents=[width * 0.95, mattress_h, depth * 0.95])
        mattress.visual.vertex_colors = [240, 240, 240, 255] # White
        mattress.apply_translation([0, base_h + mattress_h/2, 0])
        
        # Pillow
        pillow = trimesh.creation.box(extents=[width * 0.8, height * 0.2, depth * 0.2])
        pillow.visual.vertex_colors = [255, 255, 255, 255]
        pillow.apply_translation([0, base_h + mattress_h + height*0.1, -depth*0.35])
        
        return trimesh.util.concatenate([base, mattress, pillow])
        
    elif 'table' in name:
        # Table: Top + 4 Legs
        top_h = height * 0.1
        leg_h = height - top_h
        leg_w = min(width, depth) * 0.1
        
        top = trimesh.creation.box(extents=[width, top_h, depth])
        top.visual.vertex_colors = color
        top.apply_translation([0, leg_h + top_h/2, 0])
        
        legs = []
        for x in [-1, 1]:
            for z in [-1, 1]:
                leg = trimesh.creation.box(extents=[leg_w, leg_h, leg_w])
                leg.visual.vertex_colors = color
                leg.apply_translation([x * (width/2 - leg_w), leg_h/2, z * (depth/2 - leg_w)])
                legs.append(leg)
                
        return trimesh.util.concatenate([top] + legs)
        
    elif 'sofa' in name:
        # Sofa: Base + Back + Arms
        seat_h = height * 0.4
        back_h = height
        back_d = depth * 0.2
        arm_w = width * 0.15
        
        # Seat
        seat = trimesh.creation.box(extents=[width, seat_h, depth])
        seat.visual.vertex_colors = color
        seat.apply_translation([0, seat_h/2, 0])
        
        # Back
        back = trimesh.creation.box(extents=[width, back_h - seat_h, back_d])
        back.visual.vertex_colors = color
        back.apply_translation([0, seat_h + (back_h - seat_h)/2, -depth/2 + back_d/2])
        
        # Arms
        arms = []
        for x in [-1, 1]:
            arm = trimesh.creation.box(extents=[arm_w, height * 0.6, depth])
            arm.visual.vertex_colors = color
            arm.apply_translation([x * (width/2 - arm_w/2), height*0.3, 0])
            arms.append(arm)
            
        return trimesh.util.concatenate([seat, back] + arms)

    elif 'chair' in name:
        # Chair: Seat + Back + Legs
        seat_h = height * 0.5
        seat_d = depth * 0.9
        back_h = height
        back_d = depth * 0.1
        leg_w = width * 0.1
        
        # Seat
        seat = trimesh.creation.box(extents=[width, height*0.05, seat_d])
        seat.visual.vertex_colors = color
        seat.apply_translation([0, seat_h, 0])
        
        # Back
        back = trimesh.creation.box(extents=[width, back_h - seat_h, back_d])
        back.visual.vertex_colors = color
        back.apply_translation([0, seat_h + (back_h - seat_h)/2, -depth/2 + back_d/2])
        
        # Legs
        legs = []
        for x in [-1, 1]:
            for z in [-1, 1]:
                leg = trimesh.creation.box(extents=[leg_w, seat_h, leg_w])
                leg.visual.vertex_colors = color
                leg.apply_translation([x * (width/2 - leg_w), seat_h/2, z * (seat_d/2 - leg_w)])
                legs.append(leg)
                
        return trimesh.util.concatenate([seat, back] + legs)
        
    elif 'toilet' in name:
        # Toilet: Base + Tank
        base_h = height * 0.5
        tank_h = height
        tank_d = depth * 0.3
        
        base = trimesh.creation.box(extents=[width * 0.7, base_h, depth * 0.7])
        base.visual.vertex_colors = [255, 255, 255, 255]
        base.apply_translation([0, base_h/2, depth * 0.15])
        
        tank = trimesh.creation.box(extents=[width, tank_h - base_h, tank_d])
        tank.visual.vertex_colors = [255, 255, 255, 255]
        tank.apply_translation([0, base_h + (tank_h - base_h)/2, -depth/2 + tank_d/2])
        
        return trimesh.util.concatenate([base, tank])

    # Default box
    mesh = trimesh.creation.box(extents=[width, height, depth])
    mesh.visual.vertex_colors = color
    mesh.apply_translation([0, height/2, 0])
    return mesh


def place_furniture(scene, furniture_data, floor_bounds):
    """Place furniture models or placeholders based on AI suggestions"""
    if not furniture_data:
        return

    min_x, max_x, min_z, max_z = floor_bounds
    floor_width = max_x - min_x
    floor_depth = max_z - min_z

    print(f"Placing {len(furniture_data)} furniture items...")

    for i, item in enumerate(furniture_data):
        name = item.get('name', 'unknown').lower()
        
        # Calculate position based on relative coordinates
        rel_x = item.get('x', 0.5)
        rel_y = item.get('y', 0.5)
        
        # Map relative (0-1) to absolute coordinates
        abs_x = min_x + (rel_x * floor_width)
        abs_z = min_z + (rel_y * floor_depth)
        
        # Dimensions
        width = item.get('width', 100)
        depth = item.get('depth', 100)
        height = 60 # Default height
        
        # Adjust dimensions based on type
        if 'bed' in name: height = 60
        elif 'sofa' in name: height = 80
        elif 'table' in name: height = 75
        elif 'chair' in name: height = 90
        elif 'toilet' in name: height = 80
        elif 'sink' in name: height = 85
        
        # Color
        color = FURNITURE_COLORS.get(name, FURNITURE_COLORS['default'])
        if name not in FURNITURE_COLORS:
            for key in FURNITURE_COLORS:
                if key in name:
                    color = FURNITURE_COLORS[key]
                    break
        
        # Check for furniture GLB asset first
        mesh = None
        
        # Try to load from FURNITURE_ASSETS dictionary
        if name in FURNITURE_ASSETS and FURNITURE_ASSETS[name].exists():
            try:
                asset_path = FURNITURE_ASSETS[name]
                print(f"  Loading furniture asset: {asset_path.name}")
                loaded = trimesh.load(str(asset_path))
                mesh = loaded.to_geometry() if isinstance(loaded, trimesh.Scene) else loaded
                
                # Scale to fit dimensions
                bounds = mesh.bounds
                size = bounds[1] - bounds[0]
                size[size == 0] = 1e-3
                scale = [width / size[0], height / size[1], depth / size[2]]
                mesh.apply_scale(scale)
                
                # Center and move to floor
                mesh.apply_translation(-mesh.bounds.mean(axis=0)) # Center at origin
                mesh.apply_translation([0, height/2, 0]) # Move up
                
            except Exception as e:
                print(f"  Failed to load {asset_path.name}: {e}")
        
        # Fallback to procedural generation
        if mesh is None:
            mesh = create_procedural_furniture(name, width, height, depth, color)
        
        # Rotation
        rotation = item.get('rotation', 0)
        if rotation:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(rotation), [0, 1, 0]
            ))
            
        # Position (center of object)
        mesh.apply_translation([abs_x, 0, abs_z])
        
        mesh.metadata['name'] = f"furniture_{name}"
        
        node_name = f"furniture_{name}_{i}"
        scene.add_geometry(mesh, node_name=node_name, geom_name=node_name)



def generate_glb_model(json_path, output_path='output.glb'):
    """Generate complete 3D GLB model from detection data - matching notebook implementation"""

    print(f"Loading detection data from: {json_path}")
    print(f"Loading detection data from: {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    # Check for furniture data
    furniture_data = data.get('furniture', [])


    print(f"Analyzing floor plan...")
    print(f"   - Walls: {sum(1 for c in data['classes'] if c['name'] == 'wall')}")
    print(f"   - Doors: {sum(1 for c in data['classes'] if c['name'] == 'door')}")
    print(f"   - Windows: {sum(1 for c in data['classes'] if c['name'] == 'window')}")

    # Snap doors/windows to walls
    print("Snapping doors/windows to walls...")
    snap_doors_windows_to_walls(data, SNAP_THRESHOLD)

    # Grid-align all endpoints
    print("Grid-aligning all endpoints...")
    axis_snap_all_endpoints(data, GRID_SNAP_THRESHOLD)

    # Configuration from data
    floor_thickness = data.get("floorThickness", FLOOR_THICKNESS)
    wall_height = data.get('wallHeight', WALL_HEIGHT)
    door_height = data.get('averageDoor', 80)
    window_height = data.get('windowHeight', 40)
    wall_thickness = data.get('wallThickness', WALL_THICKNESS)
    window_sill_height = data.get('windowSillHeight', (wall_height - window_height) / 2)

    print(f"Configuration:")
    print(f"   - Wall height: {wall_height}")
    print(f"   - Door height: {door_height}")
    print(f"   - Window height: {window_height}")
    print(f"   - Window sill height: {window_sill_height}")

    meshes = []

    # Load base models
    base_door = None
    base_window = None
    base_wall = None
    base_railing = None

    print("Loading 3D assets...")

    if DOOR_PATH.exists():
        print("  [OK] Loading door model...")
        scene = trimesh.load(str(DOOR_PATH))
        base_door = scene.to_geometry() if isinstance(scene, trimesh.Scene) else scene

    if WINDOW_PATH.exists():
        print("  [OK] Loading window model...")
        scene = trimesh.load(str(WINDOW_PATH))
        base_window = scene.to_geometry() if isinstance(scene, trimesh.Scene) else scene

    if WALL_PATH.exists():
        print("  [OK] Loading wall model...")
        scene = trimesh.load(str(WALL_PATH))
        base_wall = scene.to_geometry() if isinstance(scene, trimesh.Scene) else scene

    if RAIL_PATH.exists():
        print("  [OK] Loading railing model...")
        scene = trimesh.load(str(RAIL_PATH))
        base_railing = scene.to_geometry() if isinstance(scene, trimesh.Scene) else scene

    # Create floor
    print("Creating floor...")
    floor_mesh = create_floor_mesh(data, floor_thickness, CARPET_PATH)
    floor_mesh.metadata['name'] = 'floor'
    meshes.append(floor_mesh)

    # Track wall edges for railing
    wall_edges = set()

    # Process all elements
    print("Building 3D elements...")
    for cls, p in zip(data['classes'], data['points']):
        name = cls['name'].lower()
        x1, y1 = p['x1'], p['y1']
        x2, y2 = p['x2'], p['y2']
        dx, dz = abs(x2 - x1), abs(y2 - y1)
        cx, cz = (x1 + x2) / 2, (y1 + y2) / 2

        # WALLS
        if name not in ['door', 'window']:
            start = np.array([x1, 0.0, y1])
            end = np.array([x2, 0.0, y2])
            length = np.linalg.norm(end - start)
            if length < 1e-6:
                continue

            def make_wall_surface(flip=False):
                if base_wall is not None:
                    wall = base_wall.copy()
                    bnd = wall.bounds
                    size = bnd[1] - bnd[0]
                    size[size == 0] = 1e-3
                    scale = [length / size[0], wall_height / size[1], 1.0 / size[2]]
                    wall.apply_scale(scale)
                else:
                    # Fallback wall
                    wall = trimesh.creation.box(extents=[length, wall_height, wall_thickness])
                    wall.visual.vertex_colors = [192, 192, 192, 255]

                if flip:
                    wall.apply_transform(
                        trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0])
                    )

                orig_dir = np.array([1, 0, 0])
                target = (end - start) / length
                axis = np.cross(orig_dir, target)
                angle = np.arccos(np.clip(np.dot(orig_dir, target), -1.0, 1.0))
                if np.linalg.norm(axis) > 1e-6 and abs(angle) > 1e-3:
                    wall.apply_transform(
                        trimesh.transformations.rotation_matrix(angle, axis)
                    )

                wall.apply_translation(-wall.bounds.mean(axis=0))
                midpoint = (start + end) / 2
                wall.apply_translation(midpoint + [0, wall_height / 2, 0])
                return wall

            wall1 = make_wall_surface(flip=False)
            wall1.metadata['name'] = 'wall'
            meshes.append(wall1)
            wall2 = make_wall_surface(flip=True)
            wall2.metadata['name'] = 'wall'
            meshes.append(wall2)

            # Track wall edge
            edge = tuple(sorted(((x1, y1), (x2, y2))))
            wall_edges.add(edge)

        # DOORS
        elif name == 'door':
            if base_door is not None:
                door = base_door.copy()
                is_vertical = dx < dz
                target_w = dz if is_vertical else dx
                target_h = door_height + 50
                target_d = wall_thickness

                bounds = door.bounds
                size = bounds[1] - bounds[0]
                size[size == 0] = 1e-3

                scale_factors = np.array([
                    target_w / size[0],
                    target_h / size[1],
                    target_d / size[2]
                ])
                door.apply_scale(scale_factors)

                if is_vertical:
                    door.apply_transform(trimesh.transformations.rotation_matrix(
                        np.radians(90), [0, 1, 0]
                    ))

                bounds = door.bounds
                center_xz = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
                center_model_xz = (bounds[0][::2] + bounds[1][::2]) / 2

                door.apply_translation([
                    center_xz[0] - center_model_xz[0],
                    -bounds[0][1],
                    center_xz[1] - center_model_xz[1]
                ])

                door.metadata['name'] = 'door'
                meshes.append(door)
            else:
                # Fallback door
                is_vertical = dx < dz
                target_w = dz if is_vertical else dx
                door = trimesh.creation.box(
                    extents=[target_w if not is_vertical else wall_thickness,
                            door_height,
                            target_w if is_vertical else wall_thickness]
                )
                door.visual.vertex_colors = [139, 69, 19, 255]
                door.apply_translation([cx, door_height / 2, cz])
                door.metadata['name'] = 'door'
                meshes.append(door)

            # Slab above door
            slab_h = wall_height - (door_height + 50)
            if slab_h > 1e-3:
                start = np.array([x1, 0.0, y1])
                end = np.array([x2, 0.0, y2])
                length = np.linalg.norm(end - start)
                if length >= 1e-6:
                    def make_wall_surface(flip=False):
                        if base_wall is not None:
                            wall = base_wall.copy()
                            bnd = wall.bounds
                            size = bnd[1] - bnd[0]
                            size[size == 0] = 1e-3
                            scale = [length / size[0], slab_h / size[1], 1.0 / size[2]]
                            wall.apply_scale(scale)
                        else:
                            wall = trimesh.creation.box(extents=[length, slab_h, wall_thickness])
                            wall.visual.vertex_colors = [192, 192, 192, 255]

                        if flip:
                            wall.apply_transform(
                                trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0])
                            )

                        orig_dir = np.array([1, 0, 0])
                        target = (end - start) / length
                        axis = np.cross(orig_dir, target)
                        angle = np.arccos(np.clip(np.dot(orig_dir, target), -1.0, 1.0))
                        if np.linalg.norm(axis) > 1e-6 and abs(angle) > 1e-3:
                            wall.apply_transform(
                                trimesh.transformations.rotation_matrix(angle, axis)
                            )

                        wall.apply_translation(-wall.bounds.mean(axis=0))
                        midpoint = (start + end) / 2
                        wall.apply_translation(midpoint + [0, (door_height + 50) + slab_h / 2, 0])
                        return wall

                    wall1 = make_wall_surface(flip=False)
                    wall1.metadata['name'] = 'wall'
                    meshes.append(wall1)
                    wall2 = make_wall_surface(flip=True)
                    wall2.metadata['name'] = 'wall'
                    meshes.append(wall2)

            # Track as wall edge
            edge = tuple(sorted(((x1, y1), (x2, y2))))
            wall_edges.add(edge)

        # WINDOWS
        elif name == 'window':
            start = np.array([x1, 0.0, y1])
            end = np.array([x2, 0.0, y2])
            length = np.linalg.norm(end - start)
            if length < 1e-6:
                continue

            def make_wall_surface(height, bottom_y, flip=False):
                if base_wall is not None:
                    wall = base_wall.copy()
                    bnd = wall.bounds
                    size = bnd[1] - bnd[0]
                    size[size == 0] = 1e-3
                    scale = [length / size[0], height / size[1], 1.0 / size[2]]
                    wall.apply_scale(scale)
                else:
                    wall = trimesh.creation.box(extents=[length, height, wall_thickness])
                    wall.visual.vertex_colors = [192, 192, 192, 255]

                if flip:
                    wall.apply_transform(
                        trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0])
                    )

                orig_dir = np.array([1, 0, 0])
                target = (end - start) / length
                axis = np.cross(orig_dir, target)
                angle = np.arccos(np.clip(np.dot(orig_dir, target), -1.0, 1.0))
                if np.linalg.norm(axis) > 1e-6 and abs(angle) > 1e-3:
                    wall.apply_transform(
                        trimesh.transformations.rotation_matrix(angle, axis)
                    )

                wall.apply_translation(-wall.bounds.mean(axis=0))
                midpoint = (start + end) / 2
                wall.apply_translation(midpoint + [0, bottom_y + height / 2, 0])
                return wall

            # Header above window
            header_h = wall_height - (window_sill_height + window_height)
            if header_h > 1e-3:
                wall1 = make_wall_surface(header_h, window_sill_height + window_height, flip=False)
                wall1.metadata['name'] = 'wall'
                meshes.append(wall1)
                wall2 = make_wall_surface(header_h, window_sill_height + window_height, flip=True)
                wall2.metadata['name'] = 'wall'
                meshes.append(wall2)

            # Sill below window
            sill_h = window_sill_height
            if sill_h > 1e-3:
                wall3 = make_wall_surface(sill_h, 0.0, flip=False)
                wall3.metadata['name'] = 'wall'
                meshes.append(wall3)
                wall4 = make_wall_surface(sill_h, 0.0, flip=True)
                wall4.metadata['name'] = 'wall'
                meshes.append(wall4)

            # Realistic window model
            if base_window is not None:
                win = base_window.copy()
                orig = win.extents
                scale = [
                    (dx if dx >= dz else dz) / (orig[0] or 1e-3),
                    window_height / (orig[1] or 1e-3),
                    wall_thickness / (orig[2] or 1e-3)
                ]
                win.apply_scale(scale)
                if dx < dz:
                    win.apply_transform(trimesh.transformations.rotation_matrix(
                        np.radians(90), [0, 1, 0]))
                win.apply_translation([cx, window_sill_height + window_height / 2, cz])
                win.metadata['name'] = 'window'
                meshes.append(win)
            else:
                # Fallback window
                win_w = dz if dx < dz else dx
                win = trimesh.creation.box(
                    extents=[win_w if dx >= dz else wall_thickness * 0.5,
                            window_height,
                            win_w if dx < dz else wall_thickness * 0.5]
                )
                win.visual.vertex_colors = [173, 216, 230, 128]
                win.apply_translation([cx, window_sill_height + window_height / 2, cz])
                win.metadata['name'] = 'window'
                meshes.append(win)

            # Track as wall edge
            edge = tuple(sorted(((x1, y1), (x2, y2))))
            wall_edges.add(edge)

    # Add railings to open edges
    if base_railing is not None:
        print("Adding railings...")
        all_x, all_z = [], []
        for p in data['points']:
            all_x += [p['x1'], p['x2']]
            all_z += [p['y1'], p['y2']]
        min_x, max_x = min(all_x), max(all_x)
        min_z, max_z = min(all_z), max(all_z)

        border_edges = [
            ((min_x, min_z), (max_x, min_z)),
            ((max_x, min_z), (max_x, max_z)),
            ((max_x, max_z), (min_x, max_z)),
            ((min_x, max_z), (min_x, min_z)),
        ]

        for (x1, z1), (x2, z2) in border_edges:
            edge_key = tuple(sorted(((x1, z1), (x2, z2))))
            if edge_key in wall_edges:
                continue

            dx, dz = x2 - x1, z2 - z1
            length = np.hypot(dx, dz)
            if length < 1e-3:
                continue
            angle = np.arctan2(dz, dx)
            cx, cz = (x1 + x2) / 2, (z1 + z2) / 2

            railing = base_railing.copy()
            orig_bounds = railing.bounds
            orig_size = orig_bounds[1] - orig_bounds[0]
            orig_size[orig_size == 0] = 1e-3

            scale = [length / orig_size[0], 40.0, 1.0]
            railing.apply_scale(scale)

            bmin, bmax = railing.bounds
            center_xz = (bmin[[0, 2]] + bmax[[0, 2]]) / 2
            bottom_y = bmin[1]

            railing.apply_translation([-center_xz[0], -bottom_y, -center_xz[1]])
            railing.apply_transform(trimesh.transformations.rotation_matrix(angle, [0, 1, 0]))
            railing.apply_translation([cx, 0, cz])

            meshes.append(railing)

            meshes.append(railing)

    # Create scene and export
    print("Combining meshes...")
    scene = trimesh.Scene()
    for i, m in enumerate(meshes):
        # Use metadata name if available, otherwise use generic name
        mesh_name = m.metadata.get('name', 'unknown')
        node_name = f"{mesh_name}_{i:03d}"
        scene.add_geometry(m, node_name=node_name, geom_name=node_name)

    # Place furniture if available
    if furniture_data:
        # Calculate floor bounds for relative positioning
        all_x, all_z = [], []
        for p in data['points']:
            all_x += [p['x1'], p['x2']]
            all_z += [p['y1'], p['y2']]
        if all_x and all_z:
            floor_bounds = (min(all_x), max(all_x), min(all_z), max(all_z))
            place_furniture(scene, furniture_data, floor_bounds)


    print(f"Exporting to {output_path}...")
    scene.export(output_path)
    print(f"[SUCCESS] 3D model exported successfully: {output_path}")

    return scene


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate GLB 3D model from floor plan detection')
    parser.add_argument('--input', '-i', default='disney_1.json', help='Input JSON file')
    parser.add_argument('--output', '-o', default='output.glb', help='Output GLB file')

    args = parser.parse_args()

    generate_glb_model(args.input, args.output)
