# Session Summary - January 13, 2026

## Overview

First working session with FiftyOne for analyzing agricultural drone imagery datasets. Successfully set up the development environment and computed CLIP embeddings for visualization.

## Tasks Completed

### 1. Project Setup

- Created `CLAUDE.md` documentation file for the FiftyOne repository
- Installed FiftyOne from source using `bash install.sh`
- Verified installation: FiftyOne v1.12.0
- Installed additional dependencies: `umap-learn`, `torch`, `torchvision`

### 2. Dataset Loading

Loaded drone imagery from Santa Ines field:
- **Path**: `/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo1_ene_2026/Santa Ines/Dron`
- **Dataset name**: `santa_ines_dron`
- **Total images**: 97 DJI drone photos (JPG format, ~10-12 MB each)
- **Image range**: DJI_0460.JPG to DJI_0557.JPG

### 3. Embedding Computation

Computed CLIP embeddings for semantic image analysis:
- **Model**: `clip-vit-base32-torch` (ViT-B/32)
- **Brain key**: `clip_viz`
- **Dimensionality reduction**: UMAP (2D visualization)
- **Processing time**: ~2-3 minutes for 97 high-resolution images

### 4. Visualization & Analysis

Launched FiftyOne App at `http://localhost:5151` with embeddings panel.

**Key findings from embedding analysis:**
- **Main cluster**: 89 images with similar visual content (field views)
- **Outlier cluster**: 8 images with distinct characteristics:
  - DJI_0469.JPG
  - DJI_0509.JPG
  - DJI_0552.JPG - DJI_0557.JPG (6 images in tight cluster)

**Embedding coordinate ranges:**
- X (UMAP Dim 1): 6.83 to 11.80
- Y (UMAP Dim 2): -0.87 to 4.43

Outlier images cluster at bottom-right (x≈11.5, y≈-0.7), suggesting visually distinct content from main field imagery.

## Files Generated

- `/home/malezainia1/santa_ines_embeddings.png` - Matplotlib visualization of embedding space
- `/home/malezainia1/fiftyone/santa_ines_dron/` - Dataset storage location

## Commands Reference

```python
import fiftyone as fo
import fiftyone.brain as fob

# Load dataset
dataset = fo.load_dataset("santa_ines_dron")

# Access embeddings
results = dataset.load_brain_results("clip_viz")
points = results.points  # Shape: (97, 2)

# Launch app
session = fo.launch_app(dataset, port=5151)
```

## Image Classification by Embeddings

Based on embedding analysis, images were automatically tagged:

| Tag | Count | Description |
|-----|-------|-------------|
| `close-up`, `crop-inspection` | 89 | Low-altitude tomato inspection photos |
| `overview`, `high-altitude` | 8 | High-altitude field mapping shots |

**Outlier images identified** (high-altitude/overview):
- DJI_0469.JPG, DJI_0509.JPG
- DJI_0552.JPG - DJI_0557.JPG

**Key finding**: CLIP embeddings successfully separated images by altitude/scale, not just GPS position. This enables automatic categorization of drone survey data.

## Session Update - January 14, 2026

### Tasks Completed

#### 1. GPS Extraction & Satellite Map Integration

- Extracted GPS coordinates from drone image EXIF metadata
- Integrated Google Maps Static API for satellite imagery background
- Created visualization comparing GPS locations vs CLIP embedding space

**GPS Range**:
- Latitude: -34.474854 to -34.474401
- Longitude: -70.952951 to -70.950338

#### 2. Combined Analysis Figure

Created comprehensive 4-panel figure (`combined_analysis.png`):
- Panel A: GPS coordinates on satellite imagery
- Panel B: CLIP embedding space (UMAP projection)
- Panel C: Representative close-up images (4 samples)
- Panel D: Representative high-altitude images (4 samples)

#### 3. Research Paper Updates (v0.2)

Updated LaTeX paper with:
- New combined analysis figure (Figure 1)
- Detailed interpretation of GPS vs embedding comparison
- Visual characteristics breakdown for each cluster
- Key findings on semantic-spatial decoupling

**Paper location**: `research/paper/main.pdf` (17 pages)

### Files Generated (Jan 14)

- `santa_ines_with_gps.csv` - Dataset with GPS coordinates
- `gps_satellite_map.py` - GPS extraction script
- `satellite_map.py` - Satellite visualization script
- `cluster_samples.py` - Representative image selection
- `combined_figure.py` - Combined 4-panel figure generator
- `satellite_gps_vs_embedding.png` - GPS vs embedding comparison
- `satellite_gps_only.png` - Satellite map with GPS points
- `cluster_representative_images.png` - Sample images by cluster
- `combined_analysis.png` - Final combined figure for paper

### Key Findings

1. **Spatial-Semantic Decoupling**: GPS positions show systematic flight pattern, but CLIP embeddings cluster by visual content regardless of location

2. **Visual Distinction**: Close-up images show plant detail/texture; high-altitude images show geometric row patterns

3. **Cluster Cohesion**: High-altitude cluster is 35% tighter (lower neighbor distance) despite fewer samples

## Next Steps

- Compute similarity index for image search functionality
- Load additional datasets from other field locations for comparison
- Use tags to filter views for specific analysis tasks
- Extend analysis to temporal changes (multi-date surveys)
