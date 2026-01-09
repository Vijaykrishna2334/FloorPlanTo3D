export const STYLE_EXTRACTION_PROMPT = `
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
`;

export const FLOOR_PLAN_ANALYSIS_PROMPT = `
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
`;


export const getFinalPromptTemplate = (styleDescription: string, floorPlanAnalysis: string) => `
**PRIMARY DIRECTIVE: Your absolute first priority is to create a 3D model that is a geometrically perfect, 1:1 scale replica of the provided 2D floor plan image. The placement of every wall, door, window, and the shape of every room must be an exact extrusion of the source image. ALL other instructions about style, furniture, and lighting are secondary and must ONLY be applied AFTER the structure is perfectly replicated.**

**Input Analysis:**
<style_guide>
${styleDescription}
</style_guide>
<architectural_plan>
${floorPlanAnalysis}
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
    - **Projection:** Use a 3D axonometric projection (isometric or dimetric) to create a 'dollhouse' view.
    - **Angle:** The camera is positioned high above and to one side, looking down at a 30 to 45-degree angle to show both the floor and two visible interior walls for each room.
    - **Cutaway:** The view is achieved by removing the ceiling entirely. Any walls that would obstruct the camera's line of sight into the interior rooms are to be cut away or made invisible. The goal is a clear, unobstructed view into the entire furnished space.

3.  **STYLING & FURNISHING:**
    - After the geometry is perfect, apply the interior design specified in the \`<style_guide>\`.
    - Place appropriate furniture (as detailed in the style guide) within the rooms identified in the \`<architectural_plan>\`.
    - Ensure furniture placement is logical, allows for movement, and fits the room's function.

4.  **LIGHTING & MATERIALS:**
    - Use physically-based rendering (PBR) materials for all surfaces as described in the style guide.
    - The scene should be lit with realistic global illumination and soft ambient occlusion to create depth and realism.

**Final Check:** Before outputting the image, perform a final verification: does the 3D architecture perfectly match the 2D source image? If not, rebuild it until it does. The structural accuracy is paramount.
`;
