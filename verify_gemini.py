import os
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

def test_image_generation():
    load_dotenv(override=True)
    api_key = os.getenv('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)

    print("--------------------------------------------------")
    
    # ---------------------------------------------------------
    # TEST 1: Gemini 2.0 Flash Exp (Multimodal)
    # ---------------------------------------------------------
    # STRATEGY: Do NOT force 'response_modalities'. Just ask nicely.
    model_id = "gemini-2.0-flash-exp"
    print(f"🧪 Test 1: {model_id} (Multimodal Text-to-Image)...")
    
    try:
        response = client.models.generate_content(
            model=model_id,
            # We explicitly ask for the image in the text prompt
            contents='Generate a high-quality illustration of a futuristic robot holding a glowing neon sign.',
            config=types.GenerateContentConfig(
                temperature=0.7,
                # REMOVED: response_modalities=["IMAGE"] <-- This caused the 400 error
            )
        )

        image_saved = False
        if response.parts:
            for part in response.parts:
                # Check if the model decided to send back an image byte stream
                if part.inline_data:
                    print("   ✅ SUCCESS! Image received from Gemini 2.0.")
                    img_data = part.inline_data.data
                    image = Image.open(io.BytesIO(img_data))
                    image.save("gemini_2_output.jpg")
                    print("   ✓ Saved to 'gemini_2_output.jpg'")
                    image_saved = True
        
        if not image_saved:
            print("   ⚠️  Model responded with text only (No image).")
            print(f"      Response: {response.text[:100]}...")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n--------------------------------------------------")

    # ---------------------------------------------------------
    # TEST 2: Imagen 3 (Dedicated Image Model)
    # ---------------------------------------------------------
    # STRATEGY: Use the specific 'generate_images' method for Imagen models
    # This often works on free tier if Gemini 2.0 fails.
    imagen_model = "imagen-3.0-generate-001"
    print(f"🧪 Test 2: {imagen_model} (Dedicated Image Gen)...")

    try:
        response = client.models.generate_images(
            model=imagen_model,
            prompt='A futuristic robot holding a glowing neon sign',
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        
        if response.generated_images:
            for i, img in enumerate(response.generated_images):
                # Imagen returns 'image.image_bytes'
                image = Image.open(io.BytesIO(img.image.image_bytes))
                filename = f"imagen_output_{i}.jpg"
                image.save(filename)
                print(f"   ✅ SUCCESS! Saved to '{filename}'")
        else:
            print("   ⚠️  No images returned.")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        if "403" in str(e) or "404" in str(e) or "429" in str(e):
             print("      (Note: Imagen 3 might be restricted on your current API key tier)")

if __name__ == "__main__":
    test_image_generation()
