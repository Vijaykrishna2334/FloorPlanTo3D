import os
import sys

# Set environment variable to use TensorFlow's Keras implementation
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import numpy as np
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import tensorflow as tf
import json

from mrcnn.config import Config
from mrcnn.model import MaskRCNN
from mrcnn.utils import extract_bboxes
from mrcnn.model import mold_image
from numpy import expand_dims

# ============================
# Configuration
# ============================
WEIGHTS_FOLDER = "./weights"
WEIGHTS_FILE_NAME = 'maskrcnn_15_epochs.h5'


class PredictionConfig(Config):
    NAME = "floorPlan_cfg"
    NUM_CLASSES = 1 + 3  # background + wall, window, door
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1


# ============================
# Flask App Setup
# ============================
application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})

global_model = None
config = None


@application.before_request
def load_model():
    if hasattr(application, '_is_model_loaded') and application._is_model_loaded:
        return
    application._is_model_loaded = True
    global global_model, config
    config = PredictionConfig()
    model_dir = os.path.abspath("./mrcnn")
    weights_path = os.path.join(WEIGHTS_FOLDER, WEIGHTS_FILE_NAME)
    print("Loading Mask R-CNN model from:", weights_path)
    global_model = MaskRCNN(mode='inference', model_dir=model_dir, config=config)
    global_model.load_weights(weights_path, by_name=True)
    print("Model loaded successfully.")


# ============================
# Helper Functions
# ============================

def myImageLoader(image_input):
    image = image_input.convert('RGB')
    image = np.asarray(image)
    h, w = image.shape[:2]
    return image, w, h


def getClassNames(class_ids):
    mapping = {1: 'wall', 2: 'window', 3: 'door'}
    return [{'name': mapping.get(cid, 'unknown')} for cid in class_ids]


def normalizePoints(bboxes, class_ids):
    result = []
    door_diff_sum = 0
    door_count = 0
    for idx, bb in enumerate(bboxes):
        cid = class_ids[idx]
        # Mask R-CNN returns bboxes as [y1, x1, y2, x2]
        y1, x1, y2, x2 = bb
        result.append([x1, y1, x2, y2])
        # accumulate door size for average
        if cid == 3:
            door_count += 1
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            door_diff_sum += max(width, height)
    avg_door = (door_diff_sum / door_count) if door_count else 0
    return result, avg_door


def turnSubArraysToJson(arrays):
    return [{'x1': a[0], 'y1': a[1], 'x2': a[2], 'y2': a[3]} for a in arrays]


# ============================
# Routes
# ============================
@application.route('/predict', methods=['POST', 'GET'])
def prediction():
    if request.method == 'GET':
        # simple upload form
        return (
            """
            <h1>Mask R-CNN Floorplan Predictor</h1>
            <p>Upload an image to get wall, window, and door detections.</p>
            <form method="post" enctype="multipart/form-data">
              <input type="file" name="image" accept="image/*" required>
              <button type="submit">Upload + Predict</button>
            </form>
            """, 200
        )

    # POST: perform prediction
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    img_stream = request.files['image'].stream
    pil_img = Image.open(img_stream).convert('RGB')
    image, w, h = myImageLoader(pil_img)
    molded = mold_image(image, config)
    sample = expand_dims(molded, 0)

    r = global_model.detect(sample, verbose=0)[0]

    bboxes = r['rois'].tolist()
    norm_boxes, avg_door = normalizePoints(bboxes, r['class_ids'])
    json_boxes = turnSubArraysToJson(norm_boxes)

    response = {
        'points': json_boxes,
        'classes': getClassNames(r['class_ids']),
        'Width': w,
        'Height': h,
        'averageDoor': avg_door
    }

    # Save to file
    with open('disney_1.json', 'w') as f:
        json.dump(response, f, indent=4)

    return jsonify(response)


@application.route('/', methods=['GET'])
def index():
    return send_file('index.html')

@application.route('/3d', methods=['GET'])
def viewer_3d():
    return send_file('viewer3d.html')

@application.route('/advanced', methods=['GET'])
def advanced_viewer():
    return send_file('advanced_viewer.html')

@application.route('/premium', methods=['GET'])
def premium_viewer():
    return send_file('premium_viewer.html')

@application.route('/glb_viewer', methods=['GET'])
def glb_viewer():
    return send_file('glb_viewer.html')

@application.route('/glb_viewer.html', methods=['GET'])
def glb_viewer_html():
    return send_file('glb_viewer.html')

@application.route('/disney_1_output.glb', methods=['GET'])
def get_disney_glb():
    """Serve the disney_1_output.glb file"""
    if os.path.exists('disney_1_output.glb'):
        return send_file('disney_1_output.glb')
    else:
        return jsonify({'error': 'GLB file not found.'}), 404

@application.route('/assets/<path:filename>', methods=['GET'])
def serve_assets(filename):
    from flask import send_from_directory
    return send_from_directory('assets', filename)

@application.route('/generate-glb', methods=['POST'])
def generate_glb():
    """Generate GLB 3D model from the current floor plan data"""
    try:
        from generate_glb_model import generate_glb_model

        # Use the existing disney_1.json file
        json_path = 'disney_1.json'
        output_path = 'output.glb'

        if not os.path.exists(json_path):
            return jsonify({'error': 'No floor plan data found. Please analyze a floor plan first.'}), 404

        # Generate the GLB model
        generate_glb_model(json_path, output_path)

        # Return the GLB file
        return send_file(output_path, as_attachment=True, download_name='floorplan_3d.glb')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application.route('/generate-glb-custom', methods=['POST'])
def generate_glb_custom():
    """Generate GLB 3D model with custom parameters"""
    try:
        from generate_glb_model import generate_glb_model
        import json

        # Get custom JSON data from request
        json_data = request.get_json()

        # Save to temporary file
        temp_json_path = 'temp_floorplan.json'
        with open(temp_json_path, 'w') as f:
            json.dump(json_data, f)

        output_path = 'output.glb'

        # Generate the GLB model
        generate_glb_model(temp_json_path, output_path)

        return jsonify({'success': True, 'message': 'GLB model generated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@application.route('/output.glb', methods=['GET'])
def get_glb():
    """Serve the generated GLB file"""
    if os.path.exists('output.glb'):
        return send_file('output.glb')
    else:
        return jsonify({'error': 'GLB file not found. Please generate it first.'}), 404

@application.route('/disney_1.json', methods=['GET'])
def get_disney_json():
    """Serve the disney_1.json file"""
    if os.path.exists('disney_1.json'):
        return send_file('disney_1.json')
    else:
        return jsonify({'error': 'JSON file not found.'}), 404




# ============================
# Gemini Integration
# ============================
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

render_generator = None
if GEMINI_API_KEY:
    try:
        from gemini_render import GeminiRenderGenerator
        render_generator = GeminiRenderGenerator(api_key=GEMINI_API_KEY)
        print("[OK] Gemini render generator initialized")
    except Exception as e:
        print(f"[WARNING] Could not initialize Gemini render generator: {e}")
else:
    print("[WARNING] GEMINI_API_KEY not found in environment")


def auto_place_furniture(structures):
    """Intelligently place furniture based on detected room layout"""
    furniture = []
    walls = [p for i, p in enumerate(structures['points']) 
             if structures['classes'][i]['name'] == 'wall']
    
    if len(walls) >= 4:
        all_x = [p['x1'] for p in walls] + [p['x2'] for p in walls]
        all_y = [p['y1'] for p in walls] + [p['y2'] for p in walls]
        center_x = (min(all_x) + max(all_x)) / 2
        center_y = (min(all_y) + max(all_y)) / 2
        width = structures['Width']
        height = structures['Height']
        norm_x = center_x / width
        norm_y = center_y / height
        
        furniture.append({
            'name': 'sofa',
            'x': norm_x - 0.1,
            'y': norm_y,
            'width': 180,
            'depth': 90,
            'rotation': 0,
            'room': 'living_room'
        })
        
        furniture.append({
            'name': 'table',
            'x': norm_x + 0.1,
            'y': norm_y,
            'width': 120,
            'depth': 80,
            'rotation': 0,
            'room': 'dining_room'
        })
    
    return furniture


@application.route('/detect-complete', methods=['POST'])
def detect_complete():
    """Complete detection: structural elements + furniture using Gemini AI"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    try:
        print("\n[INFO] Starting complete detection workflow...")
        img_file = request.files['image']
        pil_img = Image.open(img_file.stream).convert('RGB')
        
        # Step 1: Detect structures
        print("[STEP 1] Detecting structural elements...")
        image, w, h = myImageLoader(pil_img)
        molded = mold_image(image, config)
        sample = expand_dims(molded, 0)
        r = global_model.detect(sample, verbose=0)[0]
        
        bboxes = r['rois'].tolist()
        norm_boxes, avg_door = normalizePoints(bboxes, r['class_ids'])
        json_boxes = turnSubArraysToJson(norm_boxes)
        
        structures = {
            'points': json_boxes,
            'classes': getClassNames(r['class_ids']),
            'Width': w,
            'Height': h,
            'averageDoor': avg_door
        }
        
        print(f"[OK] Detected {len(json_boxes)} structural elements")
        
        # Step 2: Detect furniture
        furniture = []
        furniture_detected = False
        
        if render_generator:
            try:
                print("[STEP 2] Attempting Gemini furniture detection...")
                if os.path.exists('generated_render.png'):
                    rendered_image = Image.open('generated_render.png')
                    furniture = render_generator.detect_furniture_from_render(
                        rendered_image=rendered_image,
                        floor_plan_width=w,
                        floor_plan_height=h,
                        reference_floor_plan=pil_img
                    )
                    furniture_detected = len(furniture) > 0
                    print(f"[OK] Gemini detected {len(furniture)} furniture items")
            except Exception as e:
                print(f"[WARNING] Gemini furniture detection failed: {e}")
        
        if not furniture_detected:
            print("[INFO] Using auto-placement fallback...")
            furniture = auto_place_furniture(structures)
            print(f"[OK] Auto-placed {len(furniture)} furniture items")
        
        complete_data = {
            **structures,
            'furniture': furniture
        }
        
        with open('disney_1.json', 'w') as f:
            json.dump(complete_data, f, indent=4)
        
        print("[OK] Complete detection finished\n")
        
        return jsonify({
            'success': True,
            'structures': structures,
            'furniture': furniture,
            'message': f'Detected {len(json_boxes)} structures and {len(furniture)} furniture items'
        })
    
    except Exception as e:
        print(f"[ERROR] Complete detection failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@application.route('/generate-render', methods=['POST'])
def generate_render():
    """Generate photorealistic floor plan render using Gemini"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    if not render_generator:
        return jsonify({'error': 'Gemini render generator not configured'}), 500
    
    try:
        print("[INFO] Generating photorealistic render...")
        img_file = request.files['image']
        pil_img = Image.open(img_file.stream).convert('RGB')
        
        rendered_image, render_path = render_generator.generate_render(
            floor_plan_image=pil_img,
            style='scandinavian_minimalist',
            output_path='generated_render.png'
        )
        
        if rendered_image:
            print(f"[OK] Render generated: {render_path}")
            return jsonify({
                'success': True,
                'render_path': render_path,
                'message': 'Photorealistic render generated successfully'
            })
        else:
            return jsonify({'error': 'Render generation failed'}), 500
    
    except Exception as e:
        print(f"[ERROR] Render generation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@application.route('/generated_render.png', methods=['GET'])
def get_generated_render():
    """Serve the generated render image"""
    if os.path.exists('generated_render.png'):
        return send_file('generated_render.png')
    else:
        return jsonify({'error': 'Render not found'}), 404


# ============================
# Entry Point
# ============================
if __name__ == '__main__':
    print("Starting Flask server...")
    application.run(host='0.0.0.0', port=5000)