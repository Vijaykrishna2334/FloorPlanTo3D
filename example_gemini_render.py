#!/usr/bin/env python3
"""
Complete example demonstrating Gemini render generation and furniture detection.
Shows how to use the new API endpoints for photorealistic rendering and 3D modeling.
"""

import requests
import json
import os
import sys
from pathlib import Path
from PIL import Image
import time


class FloorPlanAPI:
    """Client for Floor Plan to 3D API with Gemini rendering"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate_render_with_furniture(self, image_path, style="scandinavian_minimalist"):
        """
        Generate a photorealistic render and detect furniture.
        
        Args:
            image_path: Path to floor plan image
            style: Design style (scandinavian_minimalist, modern, classic)
        
        Returns:
            dict: Response with render path and furniture list
        """
        print(f"\n{'='*60}")
        print(f"STEP 1: Generate Render & Detect Furniture")
        print(f"{'='*60}")
        print(f"Image: {image_path}")
        print(f"Style: {style}")
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'style': style}
            response = self.session.post(
                f"{self.base_url}/generate-render-advanced",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"\n✓ Render generated: {result['render_saved']}")
                print(f"✓ Detected furniture: {result['furniture_count']} items")
                
                # Print furniture summary
                print(f"\nDetected Items:")
                for item in result['furniture']:
                    print(f"  • {item['name']:20} - Room: {item['room']:15} - "
                          f"Pos: ({item['x']:.2f}, {item['y']:.2f}) - "
                          f"Confidence: {item['confidence']:.0%}")
                
                return result
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"✗ API Error: {response.status_code}")
            print(response.text)
            return None
    
    def detect_complete(self, image_path):
        """
        Run complete detection pipeline: structures + furniture.
        
        Args:
            image_path: Path to floor plan image
        
        Returns:
            dict: Complete detection data
        """
        print(f"\n{'='*60}")
        print(f"STEP 2: Complete Detection Pipeline")
        print(f"{'='*60}")
        print(f"Running full detection on: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = self.session.post(
                f"{self.base_url}/detect-complete",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print(f"\n✓ {result['message']}")
                
                # Print structures summary
                structures = result['structures']
                print(f"\nStructural Elements:")
                print(f"  • Walls: {sum(1 for c in structures['classes'] if c['name'] == 'wall')}")
                print(f"  • Doors: {sum(1 for c in structures['classes'] if c['name'] == 'door')}")
                print(f"  • Windows: {sum(1 for c in structures['classes'] if c['name'] == 'window')}")
                print(f"  • Floor Size: {structures['Width']}x{structures['Height']}px")
                
                # Print furniture summary
                furniture = result['furniture']
                print(f"\nFurniture Items: {len(furniture)}")
                rooms = {}
                for item in furniture:
                    room = item.get('room', 'unknown')
                    if room not in rooms:
                        rooms[room] = []
                    rooms[room].append(item['name'])
                
                for room, items in rooms.items():
                    print(f"  • {room}: {', '.join(set(items))}")
                
                return result
            else:
                print(f"✗ Error: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"✗ API Error: {response.status_code}")
            return None
    
    def generate_glb_model(self, floor_plan_data=None):
        """
        Generate 3D GLB model from floor plan data.
        
        Args:
            floor_plan_data: Optional custom floor plan data dict
        
        Returns:
            bytes: GLB file content
        """
        print(f"\n{'='*60}")
        print(f"STEP 3: Generate 3D Model")
        print(f"{'='*60}")
        
        if floor_plan_data:
            print("Generating GLB from custom data...")
            response = self.session.post(
                f"{self.base_url}/generate-glb-custom",
                json=floor_plan_data
            )
        else:
            print("Generating GLB from disney_1.json...")
            response = self.session.post(f"{self.base_url}/generate-glb")
        
        if response.status_code == 200:
            print("✓ 3D model generated successfully")
            return response.content
        else:
            print(f"✗ Generation failed: {response.status_code}")
            return None
    
    def download_render(self, output_path="render.png"):
        """Download the generated render image."""
        print(f"\n{'='*60}")
        print(f"STEP 4: Download Generated Assets")
        print(f"{'='*60}")
        
        print(f"Downloading render...")
        response = self.session.get(f"{self.base_url}/generated_render.png")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Render saved: {output_path}")
        
        return output_path
    
    def download_model(self, output_path="model.glb"):
        """Download the generated 3D model."""
        print(f"Downloading 3D model...")
        response = self.session.get(f"{self.base_url}/output.glb")
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Model saved: {output_path}")
        
        return output_path


def example_1_render_detection(image_path):
    """Example 1: Simple render generation and furniture detection"""
    print(f"\n{'#'*60}")
    print(f"# EXAMPLE 1: Render Generation & Furniture Detection")
    print(f"{'#'*60}")
    
    api = FloorPlanAPI()
    
    # Generate render and detect furniture
    result = api.generate_render_with_furniture(image_path, "scandinavian_minimalist")
    
    if result and result['success']:
        # Save furniture data
        with open('furniture_detected.json', 'w') as f:
            json.dump(result['furniture'], f, indent=2)
        print(f"\n✓ Furniture data saved to: furniture_detected.json")
        
        # Download the render
        api.download_render('render_generated.png')
        
        return result
    
    return None


def example_2_complete_pipeline(image_path):
    """Example 2: Complete detection + 3D model generation"""
    print(f"\n{'#'*60}")
    print(f"# EXAMPLE 2: Complete Pipeline (Detect + Model)")
    print(f"{'#'*60}")
    
    api = FloorPlanAPI()
    
    # Run complete detection
    result = api.detect_complete(image_path)
    
    if result and result['success']:
        # Save complete data
        with open('floor_plan_complete.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Complete floor plan data saved to: floor_plan_complete.json")
        
        # Generate 3D model
        glb_content = api.generate_glb_model(result)
        
        if glb_content:
            with open('model_complete.glb', 'wb') as f:
                f.write(glb_content)
            print(f"✓ 3D model saved to: model_complete.glb")
            
            # Download assets
            api.download_render('render_complete.png')
            
            return result
    
    return None


def example_3_custom_furniture(image_path):
    """Example 3: Furniture detection with custom modifications"""
    print(f"\n{'#'*60}")
    print(f"# EXAMPLE 3: Furniture Detection + Custom Modifications")
    print(f"{'#'*60}")
    
    api = FloorPlanAPI()
    
    # Generate render and detect furniture
    result = api.generate_render_with_furniture(image_path, "modern")
    
    if result and result['success']:
        furniture = result['furniture']
        print(f"\nOriginal furniture count: {len(furniture)}")
        
        # Example modifications
        print("\nModifying furniture positions...")
        
        # Move beds to center
        for item in furniture:
            if 'bed' in item['name'].lower():
                item['x'] = 0.3
                item['y'] = 0.3
                print(f"  • Moved {item['name']} to center")
            
            # Rotate sofas
            if 'sofa' in item['name'].lower():
                item['rotation'] = 45
                print(f"  • Rotated {item['name']} 45 degrees")
        
        # Create modified floor plan data
        modified_data = {
            "points": [],
            "classes": [],
            "Width": 1024,
            "Height": 768,
            "furniture": furniture
        }
        
        # Try to load original structures if available
        if os.path.exists('disney_1.json'):
            with open('disney_1.json') as f:
                original = json.load(f)
                modified_data['points'] = original.get('points', [])
                modified_data['classes'] = original.get('classes', [])
                modified_data['Width'] = original.get('Width', 1024)
                modified_data['Height'] = original.get('Height', 768)
        
        # Generate new 3D model with modified furniture
        print("\nGenerating 3D model with modified furniture...")
        glb_content = api.generate_glb_model(modified_data)
        
        if glb_content:
            with open('model_custom.glb', 'wb') as f:
                f.write(glb_content)
            print(f"✓ Custom 3D model saved to: model_custom.glb")
        
        return modified_data
    
    return None


def example_4_batch_processing(image_folder):
    """Example 4: Process multiple floor plans in batch"""
    print(f"\n{'#'*60}")
    print(f"# EXAMPLE 4: Batch Processing Multiple Floor Plans")
    print(f"{'#'*60}")
    
    api = FloorPlanAPI()
    
    # Find all image files
    image_files = list(Path(image_folder).glob('*.png')) + \
                  list(Path(image_folder).glob('*.jpg'))
    
    print(f"Found {len(image_files)} floor plans to process")
    
    results = []
    for i, image_path in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {image_path.name}")
        
        result = api.generate_render_with_furniture(str(image_path), "scandinavian_minimalist")
        
        if result and result['success']:
            results.append({
                'file': image_path.name,
                'furniture_count': result['furniture_count'],
                'furniture': result['furniture']
            })
            
            # Save individual results
            output_file = f"batch_result_{image_path.stem}.json"
            with open(output_file, 'w') as f:
                json.dump(result['furniture'], f, indent=2)
            
            print(f"  ✓ Saved results to: {output_file}")
        
        # Rate limiting
        if i < len(image_files):
            print("  Waiting before next request...")
            time.sleep(2)
    
    # Save batch summary
    with open('batch_summary.json', 'w') as f:
        json.dump({
            'total_processed': len(results),
            'results': results
        }, f, indent=2)
    
    print(f"\n✓ Batch processing complete!")
    print(f"✓ Summary saved to: batch_summary.json")
    
    return results


def show_menu():
    """Display example menu"""
    print(f"\n{'='*60}")
    print("Gemini Render & Furniture Detection - Examples")
    print(f"{'='*60}")
    print("\nAvailable examples:")
    print("1. Simple render generation + furniture detection")
    print("2. Complete pipeline (detection + 3D model)")
    print("3. Furniture detection + custom modifications")
    print("4. Batch processing multiple floor plans")
    print("\nUsage:")
    print("  python example_gemini_render.py [example_number] [image_path]")
    print("\nExamples:")
    print("  python example_gemini_render.py 1 floor_plan.png")
    print("  python example_gemini_render.py 2 my_apartment.png")
    print("  python example_gemini_render.py 4 ./floor_plans/")


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        show_menu()
        return
    
    example_num = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else "floor_plan.png"
    
    # Check if server is running
    print("Checking API server...")
    try:
        response = requests.get("http://localhost:5000/")
        print("✓ Server is running!")
    except:
        print("✗ Error: Server not running on http://localhost:5000")
        print("  Start the server with: python application.py")
        return
    
    # Check if image exists
    if not example_num.isdigit() or not (1 <= int(example_num) <= 4):
        print("Invalid example number. Choose 1-4")
        show_menu()
        return
    
    if int(example_num) != 4 and not os.path.exists(image_path):
        print(f"✗ Image not found: {image_path}")
        return
    
    # Run selected example
    if example_num == '1':
        example_1_render_detection(image_path)
    elif example_num == '2':
        example_2_complete_pipeline(image_path)
    elif example_num == '3':
        example_3_custom_furniture(image_path)
    elif example_num == '4':
        example_4_batch_processing(image_path)
    
    print(f"\n{'='*60}")
    print("Example complete! Check generated files:")
    print("  • *.json - Data files with positions")
    print("  • *.png - Generated render images")
    print("  • *.glb - 3D models for viewing")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
