"""
Gemini Image Generation Module for Photorealistic Floor Plan Renders
Generates high-quality rendered floor plans and detects furniture positions
"""

import os
import json
import re
from PIL import Image
from io import BytesIO
from google import genai
from google.genai import types
from typing import Optional, List, Dict, Tuple
import base64

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
IMAGEN_MODEL = os.getenv('IMAGEN_MODEL', 'gemini-2.5-flash-image')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Google AI client with new SDK
client = genai.Client(api_key=GEMINI_API_KEY)

# Enhanced Prompt Templates (from AI Architectural Visualizer)
STYLE_EXTRACTION_PROMPT = """
You are an Expert Architectural Visualizer specializing in Digital Twins creating prompts for Gemini image generation.
**STEP 1: HYPER-SPECIFIC STYLE EXTRACTION**
Analyze the Reference Image. Extract:

1. **Flooring:** (e.g., "White Oak Herringbone", "Polished Carrara Marble", "Light Grey Ceramic Tiles 24x24 inch")
- Exact material, color name, pattern, finish (matte/glossy/satin), tile size if applicable
- NOT "wood flooring" → USE "Light oak wood planks, vertical grain, 6-inch wide, matte polyurethane finish"

2. **Walls:** (e.g., "Soft Ivory White SW7005", "Exposed Red Brick with White Grout", "Light Grey Painted Drywall")
- Specific color with name/code, texture (smooth/textured), material, finish
- NOT "white walls" → USE "Soft off-white painted walls, Benjamin Moore Simply White, smooth matte finish"

3. **Ceiling:** (e.g., "White Flat Ceiling with Recessed LED Lights", "Exposed Dark Wood Beams on White")
- Color, texture, special features (beams/coffered/tray), lighting fixtures
- NOT "ceiling" → USE "Flat white ceiling with four 6-inch recessed LED downlights, 3000K warm white"

4. **Furniture Catalog:** List EVERY visible piece with extreme detail:
Format: [Item]: [Style] [Material] [Specific Color] [Distinctive Features]

Example:
- Sofa: Modern low-profile, charcoal grey linen fabric, tufted back, walnut wood legs, 3-seater
- Coffee Table: Rectangular, light oak wood top with natural grain, matte black metal hairpin legs, 48x24 inches
- Armchair: Mid-century modern, mustard yellow velvet upholstery, walnut wood frame, angled legs
- Dining Table: Round, white marble top with grey veining, gold brushed metal pedestal base, 54-inch diameter
- Bed: King size, upholstered headboard in dove grey fabric, tufted diamond pattern, low platform base

**COUNT ALL ITEMS** - List every: chair, table, sofa, bed, cabinet, shelf, console, bench, ottoman, stool

5. **Lighting Setup:**
- Natural: Window direction, daylight intensity, time of day feeling
- Artificial: List each fixture: type, position, color temperature (2700K warm/3000K neutral/4000K cool)
- Shadow: Soft/hard, direction, intensity
- NOT "good lighting" → USE "Bright natural daylight from east-facing windows, supplemented by warm white (3000K) recessed ceiling lights, creating soft diffused shadows"

6. **Decorative Elements:**
- Rugs: Size, color/pattern, material, placement (e.g., "8x10 ft cream wool shag rug, centered under coffee table")
- Plants: Type, size, pot style/color, location (e.g., "Large fiddle leaf fig in white ceramic pot, corner next to window")
- Artwork: Type, size, frame, position (e.g., "Abstract canvas 36x48 inches, black frame, centered above sofa")
- Accessories: Cushions (colors/patterns), throws, vases, books, decorative objects
- Window treatments: Type, color, material (e.g., "Floor-length white linen curtains, sheer, 84 inches")

7. **Color Palette:** List in order:
Primary Color: [specific name]
Secondary Color: [specific name]
Accent Colors: [specific names]
Neutrals: [specific names]

NOT "neutral colors" → USE "Primary: Soft ivory white, Secondary: Warm walnut brown, Accents: Sage green, mustard yellow, Neutrals: Charcoal grey, cream"

Provide the output as a detailed, structured text description.
"""

FLOOR_PLAN_ANALYSIS_PROMPT = """
You are an Expert Architectural Visualizer specializing in Digital Twins creating prompts for Gemini image generation.
**STEP 2: FLOOR PLAN ARCHITECTURAL ANALYSIS**
Analyze the User Input (Floor Plan). Extract:

1. **Room Type:** Identify from layout/annotations (bedroom, living room, kitchen, bathroom, dining room, balcony, closet, entry, etc.)
   - READ text labels carefully: "Bedroom", "Living/Dining", "Kitchen", "Bathroom", "Balcony", "WIC", etc.
   - These labels determine what furniture to place

2. **Dimensions:** Extract exact measurements if shown (e.g., "14 ft × 12 ft" or "4.2m × 3.6m")

3. **Wall Configuration:** Count walls, note angles
- Example: "Rectangular room with 4 walls, standard 90-degree corners"
- Example: "L-shaped room with 6 walls, includes alcove on east side"

4. **Openings - CRITICAL FOR MISSING EDGES:**
- Doors: Location (which wall, which side), type (single/double/sliding/pocket), swing direction if shown, EXACT width of opening
- Windows: Location (which wall), quantity, approximate size, type (casement/sliding/bay), EXACT positions
- DOCUMENT EVERY OPENING - missing this causes edge cutoff issues

Example: "Single door opening 3 feet wide on south wall right side opens inward. Two window openings 4 feet wide each on east wall evenly spaced, casement style"

5. **Complete Perimeter:** Note the COMPLETE boundary of the floor plan
- Trace entire outline including all corners, edges, indentations
- Note any balconies, terraces, or projections that extend beyond main rectangle
- Identify if layout is regular (rectangular) or irregular (L-shape, U-shape, etc.)
- Example: "Complete perimeter includes main rectangular unit PLUS balcony projection on east side extending 4 feet beyond main wall"

6. **Existing Furniture (if shown):** Note any furniture outlines in floor plan
- Example: "Floor plan shows bed outline centered on north wall, two nightstand positions"
- This indicates INPUT TYPE: "With Furniture" - convert these outlines to detailed 3D furniture
- If NO furniture outlines visible, INPUT TYPE: "Without Furniture" - add furniture based on room labels

Provide the output as a detailed, structured text description.
"""


class GeminiRenderGenerator:
    """Generate photorealistic renders and detect furniture using Gemini AI"""
    
    def __init__(self, api_key: str = None):
        """Initialize with Gemini API key"""
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = client
        
        self.text_model = GEMINI_MODEL
        self.image_model = IMAGEN_MODEL
    
    def extract_style_from_reference(self, reference_image: Image.Image) -> str:
        """
        Extract detailed style information from a reference image.
        Uses sophisticated prompt to analyze materials, furniture, lighting, etc.
        
        Args:
            reference_image: PIL Image of the reference interior
        
        Returns:
            Detailed style description string
        """
        print("[INFO] Extracting style from reference image...")
        
        try:
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=[STYLE_EXTRACTION_PROMPT, reference_image]
            )
            
            style_description = response.text.strip()
            print(f"[OK] Style extracted ({len(style_description)} characters)")
            return style_description
            
        except Exception as e:
            print(f"[ERROR] Style extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def analyze_floor_plan_architecture(self, floor_plan_image: Image.Image) -> str:
        """
        Analyze floor plan architecture to extract room types, dimensions, openings, etc.
        
        Args:
            floor_plan_image: PIL Image of the floor plan
        
        Returns:
            Detailed architectural analysis string
        """
        print("[INFO] Analyzing floor plan architecture...")
        
        try:
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=[FLOOR_PLAN_ANALYSIS_PROMPT, floor_plan_image]
            )
            
            architecture_analysis = response.text.strip()
            print(f"[OK] Architecture analyzed ({len(architecture_analysis)} characters)")
            return architecture_analysis
            
        except Exception as e:
            print(f"[ERROR] Architecture analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def generate_render_with_style(self,
                                   floor_plan_image: Image.Image,
                                   style_description: str,
                                   architecture_analysis: str,
                                   output_path: str = 'generated_render.png') -> Tuple[Optional[Image.Image], str]:
        """
        Generate photorealistic render using extracted style and architecture analysis.
        This is the 3rd step in the enhanced workflow.
        
        Args:
            floor_plan_image: PIL Image of the floor plan
            style_description: Style extracted from reference image
            architecture_analysis: Architecture analysis from floor plan
            output_path: Path to save the generated render
        
        Returns:
            Tuple of (rendered_image, output_path)
        """
        print("[INFO] Generating photorealistic render with extracted style...")
        
        # Build final prompt combining style and architecture
        final_prompt = f"""
**PRIMARY DIRECTIVE: Your absolute first priority is to create a 3D model that is a geometrically perfect, 1:1 scale replica of the provided 2D floor plan image. The placement of every wall, door, window, and the shape of every room must be an exact extrusion of the source image. ALL other instructions about style, furniture, and lighting are secondary and must ONLY be applied AFTER the structure is perfectly replicated.**

**Input Analysis:**
<style_guide>
{style_description}
</style_guide>
<architectural_plan>
{architecture_analysis}
</architectural_plan>

**Rendering Command:**
Generate a single, photorealistic 3D architectural visualization based on the following precise parameters:

1.  **MODEL GEOMETRY:**
    - The 3D model's layout MUST be an exact, non-negotiable match to the 2D floor plan image.
    - **Wall Placement & Thickness:** Replicate all internal and external walls exactly as shown.
    - **Room Dimensions:** All rooms, closets, hallways, and staircases must retain the exact shape and proportions from the 2D plan.
    - **Openings:** Place all doors and windows in their precise locations with the correct dimensions.
    - **Perimeter:** The complete building footprint, including balconies or irregularities, must be flawlessly reproduced. Do not crop, simplify, or cut off any part of the plan.

2.  **CAMERA & VIEW:**
    - **Projection:** Use a top-down orthographic view (bird's eye view) to show the complete floor plan.
    - **Angle:** The camera is positioned directly above, looking straight down to show the floor and all furniture clearly.
    - **View:** Show the complete furnished floor plan with all rooms visible from above.

3.  **STYLING & FURNISHING:**
    - After the geometry is perfect, apply the interior design specified in the `<style_guide>`.
    - Place appropriate furniture (as detailed in the style guide) within the rooms identified in the `<architectural_plan>`.
    - Ensure furniture placement is logical, allows for movement, and fits the room's function.

4.  **LIGHTING & MATERIALS:**
    - Use physically-based rendering (PBR) materials for all surfaces as described in the style guide.
    - The scene should be lit with realistic global illumination and soft ambient occlusion to create depth and realism.

**Final Check:** Before outputting the image, perform a final verification: does the 3D architecture perfectly match the 2D source image? If not, rebuild it until it does. The structural accuracy is paramount.
"""
        
        try:
            # Generate render using Gemini
            response = self.client.models.generate_content(
                model=self.image_model,
                contents=[final_prompt, floor_plan_image]
            )
            
            # Extract image from response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        img_data = part.inline_data.data
                        rendered_image = Image.open(BytesIO(img_data))
                        
                        # Save to file
                        rendered_image.save(output_path)
                        print(f"[OK] Render saved: {output_path}")
                        
                        return rendered_image, output_path
            
            print("[WARNING] Gemini did not return an image in response")
            return None, None
            
        except Exception as e:
            print(f"[ERROR] Render generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def generate_render(self, 
                       floor_plan_image: Image.Image,
                       room_types: Optional[List[str]] = None,
                       style: str = 'scandinavian_minimalist',
                       output_path: str = 'generated_render.png') -> Tuple[Image.Image, str]:
        """
        Generate a photorealistic render of a floor plan with furniture.
        
        Args:
            floor_plan_image: PIL Image of the floor plan
            room_types: List of room types to consider (auto-detect if None)
            style: Interior design style ('scandinavian_minimalist', 'modern', 'classic', etc.)
            output_path: Path to save the generated render
        
        Returns:
            Tuple of (generated_image, output_path)
        """
        
        print("[INFO] Generating photorealistic render with Gemini...")
        
        # Create architectural visualization prompt
        if style == 'scandinavian_minimalist':
            style_prompt = """Transform this architectural floor plan into a photorealistic top-down render with furnished rooms.

STYLE & THEME:
- Scandinavian minimalist interior design
- Warm, inviting atmosphere with natural materials
- Color palette: Soft whites, warm grays, natural wood tones (light oak, beech)
- Clean, uncluttered spaces with thoughtful furniture placement

MATERIALS & FINISHES:
- Flooring: Light oak hardwood planks, 6-inch wide, matte finish with visible grain
- Walls: Soft off-white (Benjamin Moore Simply White), smooth matte texture
- Furniture: Mix of light wood (oak) and neutral fabric (light gray, beige)

LIGHTING:
- Natural warm lighting as if from windows (soft shadows)
- Ambient warm white tone (3000K-3500K)
- Gentle highlights on furniture surfaces"""
        
        elif style == 'modern':
            style_prompt = """Transform this architectural floor plan into a photorealistic top-down render with furnished rooms.

STYLE & THEME:
- Modern minimalist interior design
- Clean lines, contemporary materials
- Color palette: Whites, grays, blacks with accent colors
- Sleek, functional spaces with quality furniture

MATERIALS & FINISHES:
- Flooring: Light gray concrete or light tile
- Walls: Pure white or light gray, sleek finish
- Furniture: Contemporary pieces in black, gray, white metals

LIGHTING:
- Bright, even cool-white lighting (4000K-5000K)
- Minimal shadows, clinical appearance"""
        
        else:
            style_prompt = """Transform this architectural floor plan into a photorealistic top-down render with furnished rooms.

STYLE & THEME:
- Contemporary interior design
- Balanced between comfort and style
- Warm neutral tones

MATERIALS & FINISHES:
- Flooring: Medium oak or gray wood
- Walls: Light neutral colors
- Furniture: Mix of traditional and modern pieces

LIGHTING:
- Warm ambient lighting (3500K)
- Natural soft shadows"""
        
        prompt = style_prompt + """

FURNITURE PLACEMENT (place appropriate furniture for each detected room):
- BEDROOM: Queen/King bed with wooden frame, 2 nightstands, dresser
- LIVING ROOM: Sofa, armchairs, coffee table, minimal decor, TV stand
- KITCHEN/DINING: Dining table with 4-6 chairs, refrigerator, counters
- BATHROOM: Toilet, sink with vanity, bathtub or shower
- OFFICE: Desk, office chair, bookshelves if applicable

TECHNICAL REQUIREMENTS:
- Top-down orthographic view (EXACT bird's eye view)
- Maintain exact floor plan layout and proportions
- Show walls with clear visible thickness
- Filled rooms with appropriate floor materials
- Clean, professional appearance
- No annotations or labels
- High detail, photorealistic quality
- Professional architectural visualization

Generate a beautiful, cohesive interior render that looks like a real furnished apartment from above."""

        try:
            # Convert PIL image to bytes for sending to Gemini
            img_bytes = BytesIO()
            floor_plan_image.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Send to Gemini with image using new SDK
            print("[INFO] Sending floor plan to Gemini for rendering...")
            response = self.client.models.generate_content(
                model=self.image_model,
                contents=[prompt, floor_plan_image]
            )
            
            # Extract image from response if present
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and part.inline_data.mime_type.startswith('image/'):
                        # Convert inline data to image
                        img_data = part.inline_data.data
                        rendered_image = Image.open(BytesIO(img_data))
                        
                        # Save to file
                        rendered_image.save(output_path)
                        print(f"[OK] Render saved: {output_path}")
                        
                        return rendered_image, output_path
            
            print("[WARNING] Gemini did not return an image in response")
            return None, None
            
        except Exception as e:
            print(f"[ERROR] Render generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def detect_furniture_from_render(self,
                                    rendered_image: Image.Image,
                                    floor_plan_width: int,
                                    floor_plan_height: int,
                                    reference_floor_plan: Optional[Image.Image] = None) -> List[Dict]:
        """
        Detect furniture positions and types from a rendered floor plan.
        Uses the rendered image with optional reference floor plan for accuracy.
        
        Args:
            rendered_image: PIL Image of the rendered floor plan
            floor_plan_width: Width of original floor plan (pixels)
            floor_plan_height: Height of original floor plan (pixels)
            reference_floor_plan: Original floor plan for reference
        
        Returns:
            List of furniture dictionaries with position and properties
        """
        
        print("[INFO] Detecting furniture from rendered image...")
        
        # Create comprehensive furniture detection prompt
        prompt = f"""You are an expert architectural analyst. Analyze this RENDERED floor plan image with EXTREME PRECISION.

IMAGE DIMENSIONS: {floor_plan_width} x {floor_plan_height} pixels (reference dimensions of original floor plan)

TASK: Detect EVERY furniture item visible in this rendered floor plan with PIXEL-PERFECT positioning.

MEASUREMENT INSTRUCTIONS:
1. This is a RENDERED/FURNISHED floor plan - you will see actual furniture with colors, textures, and materials
2. For EACH furniture piece you see, measure its CENTER point in the image
3. Convert to normalized coordinates: x_normalized = center_x_pixels / {floor_plan_width}, y_normalized = center_y_pixels / {floor_plan_height}
4. Measure width and depth in pixels (not normalized)
5. Estimate rotation angle (0-360 degrees)

FURNITURE CATEGORIES:

BEDROOM:
- bed (primary sleeping furniture)
- nightstand/bedside_table (small tables beside bed)
- wardrobe/closet/dresser (clothing storage)
- lamp (bedside or wall lamp)

LIVING ROOM:
- sofa/couch (main seating)
- armchair/chair (individual seating)
- coffee_table (center table)
- tv_stand/media_unit (TV mounting)
- side_table/end_table (small tables)
- bookshelf/shelving (storage/display)
- rug/carpet (floor covering)

KITCHEN/DINING:
- dining_table (dining surface)
- dining_chair/chair (seating - COUNT EACH SEPARATELY)
- refrigerator/fridge (white appliance)
- stove/oven (cooking appliance)
- sink/basin (water fixture)
- kitchen_counter/counter (work surface)
- bar_stool (counter seating)

BATHROOM:
- toilet (commode)
- sink/vanity (wash basin)
- bathtub/bath (large water fixture)
- shower/shower_enclosure (standing wash area)

GENERAL:
- plant/planter (greenery)
- rug/carpet (floor covering)
- lamp/light (lighting fixture)

OUTPUT FORMAT (JSON array only, NO markdown wrapper):
[
  {{
    "name": "exact_furniture_type",
    "x": 0.234,
    "y": 0.567,
    "width": 120,
    "depth": 80,
    "rotation": 45,
    "room": "room_type",
    "color": "#8B6239",
    "confidence": 0.95
  }}
]

CRITICAL RULES:
1. PRECISION: Use 3 decimal places for normalized coordinates (e.g., 0.234, not 0.2)
2. MEASURE FROM CENTER: Visual center point of each furniture piece
3. COUNT SEPARATELY: Each chair, plant, or individual item = separate JSON entry
4. BE COMPLETE: Detect EVERY visible furniture item
5. NO MARKDOWN: Return pure JSON only, no ```json``` wrapper
6. EXACT POSITIONS: Match the visual positions you see in the render
7. REALISTIC DIMENSIONS: Measure actual pixel dimensions for width/depth
8. COLOR: Include hex color of dominant furniture color
9. CONFIDENCE: 0.9+ for clear items, 0.7+ for partially visible items
10. ROOM TYPE: Identify which room type each item is in (bedroom, living_room, kitchen, bathroom, etc.)

Analyze the rendered floor plan image and return the JSON array with ALL detected furniture items:"""

        try:
            print("[INFO] Sending rendered image to Gemini for furniture analysis...")
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=[prompt, rendered_image]
            )
            
            # Extract and parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            furniture_list = json.loads(response_text)
            
            print(f"[OK] Detected {len(furniture_list)} furniture items")
            
            # Validate and clean up furniture data
            validated_furniture = []
            for item in furniture_list:
                # Ensure required fields
                if all(k in item for k in ['name', 'x', 'y', 'width', 'depth']):
                    # Clamp normalized coordinates to valid range
                    item['x'] = max(0.0, min(1.0, float(item['x'])))
                    item['y'] = max(0.0, min(1.0, float(item['y'])))
                    item['width'] = max(1, int(item.get('width', 50)))
                    item['depth'] = max(1, int(item.get('depth', 50)))
                    item['rotation'] = float(item.get('rotation', 0)) % 360
                    item['room'] = item.get('room', 'unknown')
                    item['confidence'] = float(item.get('confidence', 0.8))
                    
                    validated_furniture.append(item)
            
            print(f"[OK] Validated {len(validated_furniture)} furniture items")
            return validated_furniture
            
        except json.JSONDecodeError as e:
            print(f"[WARNING] Failed to parse Gemini furniture response: {e}")
            print(f"Response text: {response_text[:500]}")
            return []
        
        except Exception as e:
            print(f"[ERROR] Furniture detection failed: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_and_detect(self,
                           floor_plan_image: Image.Image,
                           floor_plan_width: int,
                           floor_plan_height: int,
                           style: str = 'scandinavian_minimalist',
                           render_path: str = 'generated_render.png') -> Tuple[Optional[Image.Image], List[Dict]]:
        """
        Complete workflow: Generate render and detect furniture in one call.
        
        Args:
            floor_plan_image: PIL Image of the floor plan
            floor_plan_width: Width of original floor plan (pixels)
            floor_plan_height: Height of original floor plan (pixels)
            style: Interior design style
            render_path: Path to save the generated render
        
        Returns:
            Tuple of (rendered_image, furniture_list)
        """
        
        # Step 1: Generate render
        rendered_image, saved_path = self.generate_render(
            floor_plan_image,
            style=style,
            output_path=render_path
        )
        
        if rendered_image is None:
            print("[WARNING] Render generation failed, will use original floor plan")
            rendered_image = floor_plan_image
        
        # Step 2: Detect furniture
        furniture = self.detect_furniture_from_render(
            rendered_image,
            floor_plan_width,
            floor_plan_height,
            reference_floor_plan=floor_plan_image
        )
        
        return rendered_image, furniture
