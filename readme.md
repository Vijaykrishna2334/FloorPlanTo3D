# 🏠 FloorPlanTo3D: AI-Powered 2D to 3D Architectural Visualization

<p align="center">
  <img src="images/readme/3d_viewer_demo.png" alt="FloorPlanTo3D 3D Viewer Demo" width="100%"/>
</p>

<p align="center">
  <strong>Transform 2D floor plans into interactive 3D models using Mask R-CNN deep learning</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/TensorFlow-2.17-orange.svg" alt="TensorFlow"/>
  <img src="https://img.shields.io/badge/Model-Mask_RCNN-green.svg" alt="Mask R-CNN"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"/>
</p>

---

## 🎯 Overview

**FloorPlanTo3D** transforms 2D floor plan images into fully customizable, interactive 3D models. Using **Mask R-CNN** deep learning for architectural element detection and **Google Gemini AI** for photorealistic rendering.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Detection** | Mask R-CNN detects walls, windows, and doors automatically |
| 🎨 **Photorealistic Rendering** | Gemini AI generates stunning 3D visualizations |
| 🪑 **Smart Furniture Placement** | Intelligent auto-placement or manual customization |
| 📐 **GLB Model Export** | Compatible with any 3D viewer |
| 🌐 **Web Interface** | Easy-to-use browser-based application |
| ⚡ **Real-time Controls** | Adjust wall height, thickness, and more |

---

## 🖼️ Screenshots

<p align="center">
  <img src="images/readme/example_a.png" alt="Floor Plan Detection Example A" width="100%"/>
</p>

<p align="center">
  <img src="images/readme/example_b.png" alt="Floor Plan Detection Example B" width="100%"/>
</p>

---

## 🧠 The AI Model: Mask R-CNN

### What is Mask R-CNN?

**Mask R-CNN** (Mask Region-based Convolutional Neural Network) is a state-of-the-art instance segmentation model that can:
- **Detect** objects in an image
- **Classify** each detected object
- **Generate pixel-level masks** for each object

### Our Trained Model

| Property | Value |
|----------|-------|
| **Architecture** | Mask R-CNN with ResNet-101 backbone |
| **Training** | 15 epochs on floor plan dataset |
| **Weights File** | `maskrcnn_15_epochs.h5` (255 MB) |
| **Classes** | Wall, Window, Door (3 classes + background) |
| **Framework** | TensorFlow 2.17 with Keras |

### Detection Pipeline

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  2D Floor Plan  │ ──► │  Mask R-CNN  │ ──► │  Detected       │ ──► │  3D Model    │
│  Image Upload   │     │  Analysis    │     │  Elements       │     │  Generation  │
└─────────────────┘     └──────────────┘     └─────────────────┘     └──────────────┘
       PNG/JPG           Instance Seg.         Walls, Doors,          GLB Export
                                               Windows
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- **Git**
- **8GB RAM** minimum (CPU inference)
- **Google Gemini API key** (optional, for AI rendering)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Vijaykrishna2334/FloorPlanTo3D.git
cd FloorPlanTo3D

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional - for Gemini AI features)
echo "GEMINI_API_KEY=your_api_key_here" > .env

# 5. Run the application
python application.py
```

The server starts at **http://localhost:5000**

### Model Weights

The pre-trained Mask R-CNN weights (`maskrcnn_15_epochs.h5`) should be placed in:
```
weights/maskrcnn_15_epochs.h5
```

---

## 💻 Usage

### Web Interface

1. Open **http://localhost:5000** in your browser
2. Click **"Upload Floor Plan"** and select your image
3. Click **"Analyze"** to detect architectural elements
4. Review detection stats (Walls, Doors, Windows, Furniture)
5. Click **"Generate 3D Model"** to create the GLB file
6. Use **Model Controls** to adjust:
   - Wall Height
   - Wall Thickness
   - Furniture visibility

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Detect structural elements (walls, doors, windows) |
| `/detect-complete` | POST | Full detection including furniture |
| `/generate-glb` | POST | Generate 3D GLB model |
| `/generate-render` | POST | Generate photorealistic render |
| `/output.glb` | GET | Download generated 3D model |

#### Example: Predict Structures

```bash
curl -X POST -F "image=@floorplan.png" http://localhost:5000/predict
```

**Response:**
```json
{
  "points": [{"x1": 100, "y1": 50, "x2": 500, "y2": 55}],
  "classes": [{"name": "wall"}],
  "Width": 800,
  "Height": 600,
  "averageDoor": 90.5
}
```

---

## 📁 Project Structure

```
FloorPlanTo3D/
├── application.py              # Flask API server
├── generate_glb_model.py       # 3D model generation
├── gemini_render.py            # Gemini AI integration
├── create_furniture_assets.py  # Furniture 3D models
├── requirements.txt            # Dependencies
│
├── mrcnn/                      # Mask R-CNN implementation
│   ├── config.py               # Model configuration
│   ├── model.py                # Core Mask R-CNN model
│   ├── utils.py                # Utility functions
│   └── visualize.py            # Visualization tools
│
├── weights/                    # Model weights
│   └── maskrcnn_15_epochs.h5   # Trained weights (255 MB)
│
├── assets/                     # 3D textures and assets
├── images/                     # Example inputs and outputs
└── index.html                  # Web interface
```

---

## ⚙️ Configuration

### Model Configuration

```python
# application.py
class PredictionConfig(Config):
    NAME = "floorPlan_cfg"
    NUM_CLASSES = 1 + 3  # background + wall, window, door
    GPU_COUNT = 1        # Use 0 for CPU-only
    IMAGES_PER_GPU = 1
```

### Supported Input Formats

- **PNG, JPG, JPEG, BMP** floor plan images
- Clear wall boundaries work best
- Both CAD exports and hand-drawn sketches supported

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Model weights not found** | Place `maskrcnn_15_epochs.h5` in `weights/` folder |
| **Out of memory error** | Reduce image size before upload |
| **Poor detection** | Use high-contrast floor plans with clear walls |
| **Gemini API errors** | Check `.env` file has valid `GEMINI_API_KEY` |
| **TensorFlow errors** | Ensure TensorFlow 2.17 is installed correctly |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Deep Learning** | TensorFlow 2.17, Mask R-CNN (Matterport) |
| **Backend** | Python 3.10+, Flask, NumPy, OpenCV |
| **3D Generation** | Trimesh, GLB format |
| **AI Rendering** | Google Gemini API |
| **Frontend** | HTML5, CSS3, JavaScript, Three.js |

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file.

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- [Matterport Mask R-CNN](https://github.com/matterport/Mask_RCNN) - Base implementation
- [Google Gemini AI](https://ai.google.dev/) - Photorealistic rendering
- TensorFlow & Keras teams

---

<p align="center">
  <strong>Made with ❤️ for architects, designers, and visualization enthusiasts</strong>
</p>

<p align="center">
  <a href="https://github.com/Vijaykrishna2334/FloorPlanTo3D">⭐ Star this repo if you find it useful!</a>
</p>