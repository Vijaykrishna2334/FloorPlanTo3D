#!/usr/bin/env python3
"""List available image generation models"""

available_models = {
    "Imagen 3": {
        "model": "imagen-3.0-generate-001",
        "description": "Latest Imagen model - highest quality",
        "resolution": "Up to 1024x1024"
    },
    "Imagen 2": {
        "model": "imagegeneration@006",
        "description": "Previous generation Imagen",
        "resolution": "Up to 1024x1024"
    },
    "Stable Diffusion": {
        "model": "stable-diffusion-xl-1024-v1-00",
        "description": "Alternative option if Imagen unavailable",
        "resolution": "1024x1024"
    }
}

print("Available Image Generation Models:")
print("=" * 60)

for name, info in available_models.items():
    print(f"\n{name}")
    print(f"  Model ID: {info['model']}")
    print(f"  Description: {info['description']}")
    print(f"  Resolution: {info['resolution']}")

print("\n" + "=" * 60)
print("\nCurrent setting in .env:")

from dotenv import load_dotenv
import os

load_dotenv()
current = os.getenv('IMAGEN_MODEL', 'Not set')
print(f"  IMAGEN_MODEL={current}")

print("\nTo change, update .env with one of:")
for name, info in available_models.items():
    print(f"  IMAGEN_MODEL={info['model']}")
