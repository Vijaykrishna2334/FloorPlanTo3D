"""
Complete Workflow Endpoint for Floor Plan to 3D Model Generation
This module provides the unified endpoint that orchestrates the entire pipeline.
"""

from flask import request, jsonify
from PIL import Image
import json
import os
from numpy import expand_dims


def register_complete_workflow_endpoint(app, global_model, config, render_generator, 
                                        myImageLoader, mold_image, normalizePoints, 
                                        turnSubArraysToJson, getClassNames, auto_place_furniture):
    """
    Register the complete workflow endpoint with the Flask app.
    
    This endpoint orchestrates:
    1. Mask R-CNN structural detection
    2. Gemini render generation (with optional style extraction)
    3. Furniture detection from render
    4. Data combination
    5. 3D model generation
    """
    
    @app.route('/generate-complete-workflow', methods=['POST'])
    def generate_complete_workflow():
        """
        Complete unified workflow: Floor Plan → Gemini Render → Furniture Detection → 3D Model
        
        Request:
            - image: Floor plan image file (required)
            - reference_image: Reference image for style extraction (optional)
        
        Returns:
            JSON with structures, render info, furniture data, and 3D model path
        """
        if 'image' not in request.files:
            return jsonify({'error': 'No floor plan image provided'}), 400
        
        try:
            print("\n" + "="*80)
            print("STARTING COMPLETE WORKFLOW: Floor Plan → 2D Render → 3D Model")
            print("="*80 + "\n")
            
            # Get uploaded floor plan
            img_file = request.files['image']
            pil_img = Image.open(img_file.stream).convert('RGB')
            
            # Get optional reference image for style extraction
            reference_img = None
            if 'reference_image' in request.files:
                ref_file = request.files['reference_image']
                reference_img = Image.open(ref_file.stream).convert('RGB')
                print("[INFO] Reference image provided for style extraction")
            
            # ============================================================
            # STEP 1: Detect Structural Elements (Mask R-CNN)
            # ============================================================
            print("\n[STEP 1/5] Detecting structural elements with Mask R-CNN...")
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
            print(f"     - Walls: {sum(1 for c in structures['classes'] if c['name'] == 'wall')}")
            print(f"     - Doors: {sum(1 for c in structures['classes'] if c['name'] == 'door')}")
            print(f"     - Windows: {sum(1 for c in structures['classes'] if c['name'] == 'window')}")
            
            # ============================================================
            # STEP 2: Generate 2D Furnished Render with Gemini
            # ============================================================
            furniture = []
            rendered_image = None
            render_path = 'generated_render_complete.png'
            
            if render_generator:
                if reference_img:
                    # Enhanced 3-step workflow with style extraction
                    print("\n[STEP 2/5] Generating render with 3-step workflow (style extraction)...")
                    
                    # Step 2a: Extract style from reference
                    print("  [2a] Extracting style from reference image...")
                    style_description = render_generator.extract_style_from_reference(reference_img)
                    
                    # Step 2b: Analyze floor plan architecture
                    print("  [2b] Analyzing floor plan architecture...")
                    architecture_analysis = render_generator.analyze_floor_plan_architecture(pil_img)
                    
                    # Step 2c: Generate render with extracted style
                    print("  [2c] Generating photorealistic render...")
                    if style_description and architecture_analysis:
                        rendered_image, _ = render_generator.generate_render_with_style(
                            floor_plan_image=pil_img,
                            style_description=style_description,
                            architecture_analysis=architecture_analysis,
                            output_path=render_path
                        )
                    else:
                        print("[WARNING] Style extraction or architecture analysis failed, using simple render")
                        rendered_image, _ = render_generator.generate_render(
                            floor_plan_image=pil_img,
                            style='scandinavian_minimalist',
                            output_path=render_path
                        )
                else:
                    # Simple render without reference image
                    print("\n[STEP 2/5] Generating render with default style...")
                    rendered_image, _ = render_generator.generate_render(
                        floor_plan_image=pil_img,
                        style='scandinavian_minimalist',
                        output_path=render_path
                    )
                
                if rendered_image:
                    print(f"[OK] Render generated: {render_path}")
                else:
                    print("[WARNING] Render generation failed")
            else:
                print("\n[STEP 2/5] SKIPPED - Gemini render generator not configured")
            
            # ============================================================
            # STEP 3: Detect Furniture from Rendered Image
            # ============================================================
            if rendered_image and render_generator:
                print("\n[STEP 3/5] Detecting furniture from rendered image...")
                furniture = render_generator.detect_furniture_from_render(
                    rendered_image=rendered_image,
                    floor_plan_width=w,
                    floor_plan_height=h,
                    reference_floor_plan=pil_img
                )
                print(f"[OK] Detected {len(furniture)} furniture items")
                
                # Print furniture summary
                if furniture:
                    furniture_types = {}
                    for item in furniture:
                        ftype = item.get('name', 'unknown')
                        furniture_types[ftype] = furniture_types.get(ftype, 0) + 1
                    print("     Furniture breakdown:")
                    for ftype, count in sorted(furniture_types.items()):
                        print(f"       - {ftype}: {count}")
            else:
                print("\n[STEP 3/5] SKIPPED - No render available for furniture detection")
                # Fallback to auto-placement
                print("[INFO] Using intelligent auto-placement based on floor layout...")
                furniture = auto_place_furniture(structures)
                print(f"[OK] Auto-placed {len(furniture)} furniture items")
            
            # ============================================================
            # STEP 4: Combine Data and Save JSON
            # ============================================================
            print("\n[STEP 4/5] Combining structural and furniture data...")
            complete_data = {
                **structures,
                'furniture': furniture
            }
            
            # Save to disney_1.json
            json_path = 'disney_1.json'
            with open(json_path, 'w') as f:
                json.dump(complete_data, f, indent=4)
            print(f"[OK] Complete data saved to {json_path}")
            
            # ============================================================
            # STEP 5: Generate 3D GLB Model
            # ============================================================
            print("\n[STEP 5/5] Generating 3D GLB model...")
            from generate_glb_model import generate_glb_model
            
            output_glb_path = 'output.glb'
            generate_glb_model(json_path, output_glb_path)
            print(f"[OK] 3D model generated: {output_glb_path}")
            
            # ============================================================
            # Return Complete Results
            # ============================================================
            print("\n" + "="*80)
            print("WORKFLOW COMPLETE!")
            print("="*80 + "\n")
            
            return jsonify({
                'success': True,
                'message': 'Complete workflow executed successfully',
                'structures': {
                    'walls': sum(1 for c in structures['classes'] if c['name'] == 'wall'),
                    'doors': sum(1 for c in structures['classes'] if c['name'] == 'door'),
                    'windows': sum(1 for c in structures['classes'] if c['name'] == 'window'),
                    'total': len(json_boxes)
                },
                'render': {
                    'generated': rendered_image is not None,
                    'path': render_path if rendered_image else None
                },
                'furniture': {
                    'count': len(furniture),
                    'items': furniture
                },
                'model': {
                    'path': output_glb_path,
                    'download_url': '/output.glb'
                },
                'data_file': json_path
            })
        
        except Exception as e:
            print(f"\n[ERROR] Complete workflow failed: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Workflow failed: {str(e)}'}), 500
