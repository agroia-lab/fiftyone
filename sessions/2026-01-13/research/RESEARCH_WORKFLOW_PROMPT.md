# Research Writing Workflow Prompt

> **Purpose**: This prompt guides Claude Code to set up and develop research documentation for agricultural/computer vision projects using FiftyOne, CLIP embeddings, and LaTeX.

---

## PROMPT START

You are assisting with a research project that involves analyzing image datasets using computer vision techniques. Follow this workflow to set up the research infrastructure, analyze data, and produce a documented research paper.

### 1. Project Structure Setup

Create the following directory structure for the research project:

```
{PROJECT_ROOT}/
├── CLAUDE.md                    # Project-specific instructions
├── session_summary.md           # Work log and findings
├── *.py                         # Analysis scripts
├── *.R                          # R statistical scripts
├── *.csv                        # Exported data
├── *.png                        # Generated figures
└── research/
    ├── README.md
    ├── RESEARCH_WORKFLOW_PROMPT.md
    ├── data/
    │   ├── raw/                 # Original data links/refs
    │   └── processed/           # Cleaned CSVs
    ├── analysis/
    │   ├── python/
    │   └── R/
    └── paper/
        ├── main.tex             # Main LaTeX document
        ├── main.pdf             # Compiled PDF
        ├── CHANGELOG.txt        # Version history
        ├── sections/
        │   ├── abstract.tex
        │   ├── introduction.tex
        │   ├── objectives.tex
        │   ├── methods.tex
        │   ├── results.tex
        │   ├── discussion.tex
        │   ├── conclusions.tex
        │   ├── observations.tex
        │   └── technical.tex
        └── figures/
```

### 2. LaTeX Paper Template

Create `main.tex` with this structure:

```latex
\documentclass[11pt,a4paper]{article}

% Packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{graphicx}
\usepackage{float}
\usepackage{subcaption}
\graphicspath{{figures/}}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{amsmath}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{listings}
\usepackage{xcolor}

% Custom annotation commands
\definecolor{observation}{RGB}{39,174,96}
\definecolor{finding}{RGB}{41,128,185}
\definecolor{todo}{RGB}{231,76,60}
\newcommand{\observation}[1]{\textcolor{observation}{\textbf{[OBS:} #1\textbf{]}}}
\newcommand{\finding}[1]{\textcolor{finding}{\textbf{[FIND:} #1\textbf{]}}}
\newcommand{\todo}[1]{\textcolor{todo}{\textbf{[TODO:} #1\textbf{]}}}

% Document info - CUSTOMIZE THESE
\title{{PAPER_TITLE}}
\author{Research Notes - Draft v0.1}
\date{{MONTH} {YEAR} \\ \small Last updated: \today}

\begin{document}
\maketitle
\begin{abstract}
\input{sections/abstract}
\end{abstract}
\tableofcontents
\newpage

\section{Introduction}
\input{sections/introduction}

\section{Objectives}
\input{sections/objectives}

\section{Materials and Methods}
\input{sections/methods}

\section{Results}
\input{sections/results}

\section{Discussion}
\input{sections/discussion}

\section{Conclusions}
\input{sections/conclusions}

\appendix
\section{Observation Log}
\input{sections/observations}

\section{Technical Details}
\input{sections/technical}

\end{document}
```

### 3. Data Analysis Pipeline

#### 3.1 FiftyOne Dataset Setup

```python
# {PROJECT_NAME}_setup.py
import fiftyone as fo
import fiftyone.brain as fob
import pandas as pd
import os

# === CONFIGURATION - CUSTOMIZE ===
DATASET_NAME = "{DATASET_NAME}"
IMAGES_PATH = "{PATH_TO_IMAGES}"
OUTPUT_DIR = "{OUTPUT_DIR}"

# Load or create dataset
if DATASET_NAME in fo.list_datasets():
    dataset = fo.load_dataset(DATASET_NAME)
    print(f"Loaded existing dataset: {DATASET_NAME}")
else:
    dataset = fo.Dataset.from_images_dir(IMAGES_PATH, name=DATASET_NAME)
    print(f"Created new dataset: {DATASET_NAME} with {len(dataset)} samples")

# Compute CLIP embeddings
if "clip_viz" not in dataset.list_brain_runs():
    fob.compute_visualization(
        dataset,
        embeddings="clip-vit-base32-torch",
        method="umap",
        brain_key="clip_viz"
    )
    print("Computed CLIP embeddings")

# Export data to CSV
results = dataset.load_brain_results("clip_viz")
points = results.points

data = []
for i, sample in enumerate(dataset):
    data.append({
        'sample_id': sample.id,
        'filepath': sample.filepath,
        'filename': os.path.basename(sample.filepath),
        'umap_x': points[i, 0],
        'umap_y': points[i, 1],
        'tags': ','.join(sample.tags) if sample.tags else '',
        'width': sample.metadata.width if sample.metadata else None,
        'height': sample.metadata.height if sample.metadata else None,
        'size_bytes': sample.metadata.size_bytes if sample.metadata else None,
    })

df = pd.DataFrame(data)
df.to_csv(f"{OUTPUT_DIR}/{DATASET_NAME}_data.csv", index=False)
print(f"Exported {len(df)} samples to CSV")
```

#### 3.2 GPS Extraction (for drone imagery)

```python
# gps_extraction.py
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd

def get_exif_data(image_path):
    """Extract EXIF data from image"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is None:
            return None
        exif = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            exif[tag] = value
        return exif
    except Exception as e:
        print(f"Error reading {image_path}: {e}")
        return None

def get_gps_coords(exif_data):
    """Extract GPS coordinates from EXIF data"""
    if not exif_data or 'GPSInfo' not in exif_data:
        return None, None

    gps_info = exif_data['GPSInfo']
    gps_data = {}
    for key in gps_info.keys():
        tag = GPSTAGS.get(key, key)
        gps_data[tag] = gps_info[key]

    def convert_to_degrees(value):
        d, m, s = float(value[0]), float(value[1]), float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    lat = lon = None
    if 'GPSLatitude' in gps_data and 'GPSLatitudeRef' in gps_data:
        lat = convert_to_degrees(gps_data['GPSLatitude'])
        if gps_data['GPSLatitudeRef'] == 'S':
            lat = -lat

    if 'GPSLongitude' in gps_data and 'GPSLongitudeRef' in gps_data:
        lon = convert_to_degrees(gps_data['GPSLongitude'])
        if gps_data['GPSLongitudeRef'] == 'W':
            lon = -lon

    return lat, lon

# === USAGE ===
# df = pd.read_csv("dataset.csv")
# df['latitude'] = df['filepath'].apply(lambda p: get_gps_coords(get_exif_data(p))[0])
# df['longitude'] = df['filepath'].apply(lambda p: get_gps_coords(get_exif_data(p))[1])
```

#### 3.3 Satellite Map Visualization

```python
# satellite_map.py
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from io import BytesIO
import numpy as np

# === CONFIGURATION ===
API_KEY = "{GOOGLE_MAPS_API_KEY}"
DATA_PATH = "{DATA_CSV_PATH}"
OUTPUT_PATH = "{OUTPUT_PNG_PATH}"

def lat_lon_to_pixels(lat, lon, zoom, img_size):
    lat_rad = np.radians(lat)
    n = 2 ** zoom
    x = (lon + 180) / 360 * n * 256
    y = (1 - np.log(np.tan(lat_rad) + 1/np.cos(lat_rad)) / np.pi) / 2 * n * 256
    return x, y

def gps_to_image_coords(lat, lon, center_lat, center_lon, zoom, img_size):
    cx, cy = lat_lon_to_pixels(center_lat, center_lon, zoom, img_size)
    px, py = lat_lon_to_pixels(lat, lon, zoom, img_size)
    x = (px - cx) + img_size / 2
    y = (py - cy) + img_size / 2
    return x, y

# Load data
df = pd.read_csv(DATA_PATH)
center_lat, center_lon = df['latitude'].mean(), df['longitude'].mean()
zoom, img_size = 18, 640

# Fetch satellite image
url = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_lon}&zoom={zoom}&size={img_size}x{img_size}&maptype=satellite&key={API_KEY}"
response = requests.get(url)
satellite_img = mpimg.imread(BytesIO(response.content), format='png')

# Convert coordinates
df['img_x'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[0], axis=1)
df['img_y'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[1], axis=1)

# Plot
fig, ax = plt.subplots(figsize=(10, 10))
ax.imshow(satellite_img, extent=[0, img_size, img_size, 0])
# Add your scatter plot here with categories
plt.savefig(OUTPUT_PATH, dpi=150, bbox_inches='tight')
```

#### 3.4 Combined Analysis Figure

```python
# combined_figure.py
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

# === CONFIGURATION ===
DATA_PATH = "{DATA_CSV_PATH}"
OUTPUT_PATH = "{OUTPUT_PNG_PATH}"
CATEGORY_COLUMN = "{CATEGORY_COLUMN}"  # Column for grouping
CATEGORY_VALUES = ["{CAT1}", "{CAT2}"]  # Category names
CATEGORY_COLORS = ["#00FF00", "#FF0000"]  # Colors for each

# Create figure with GridSpec
fig = plt.figure(figsize=(16, 14))
gs = GridSpec(3, 4, figure=fig, height_ratios=[1.2, 1.2, 1])

# Panel A: Satellite/GPS map (gs[0, :2])
# Panel B: Embedding space (gs[0, 2:])
# Panel C: Representative images category 1 (gs[1, :])
# Panel D: Representative images category 2 (gs[2, :])

# ... implementation details ...

plt.suptitle('{FIGURE_TITLE}', fontsize=14, fontweight='bold')
plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight')
```

#### 3.5 R Statistical Analysis

```r
# analysis.R
library(ggplot2)
library(dplyr)

# === CONFIGURATION ===
DATA_PATH <- "{DATA_CSV_PATH}"
OUTPUT_DIR <- "{OUTPUT_DIR}"

# Load data
df <- read.csv(DATA_PATH, stringsAsFactors = FALSE)
df$category <- ifelse(grepl("{PATTERN}", df$tags), "{CAT1}", "{CAT2}")

# Embedding visualization
p1 <- ggplot(df, aes(x = umap_x, y = umap_y, color = category)) +
  geom_point(size = 3, alpha = 0.8) +
  scale_color_manual(values = c("{CAT1}" = "#2E86AB", "{CAT2}" = "#E94F37")) +
  labs(title = "{TITLE}", x = "UMAP Dimension 1", y = "UMAP Dimension 2") +
  theme_minimal()

ggsave(file.path(OUTPUT_DIR, "embeddings_plot.png"), p1, width = 10, height = 8, dpi = 150)

# Summary statistics
summary_stats <- df %>%
  group_by(category) %>%
  summarise(
    n = n(),
    mean_x = mean(umap_x),
    sd_x = sd(umap_x),
    mean_y = mean(umap_y),
    sd_y = sd(umap_y),
    .groups = "drop"
  )
print(summary_stats)
```

### 4. Version Control & Documentation

#### 4.1 CHANGELOG.txt Template

```
================================================================================
CHANGELOG - {PAPER_TITLE}
================================================================================

Version X.Y - {DATE}
--------------------
NEW FEATURES:
- ...

NEW CONTENT:
- ...

FIGURES:
- Added: ...
- Updated: ...

BUG FIXES:
- ...

================================================================================
```

#### 4.2 Session Summary Template

```markdown
# Session Summary - {DATE}

## Overview
{Brief description of session goals}

## Tasks Completed

### 1. {Task Category}
- {Detail}
- {Detail}

### 2. {Task Category}
- {Detail}

## Files Generated
- `filename.ext` - Description
- `filename.ext` - Description

## Key Findings
1. {Finding}
2. {Finding}

## Next Steps
- {Todo item}
- {Todo item}
```

### 5. Compilation Commands

```bash
# Compile LaTeX (run twice for TOC/references)
cd research/paper
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# Open PDF
xdg-open main.pdf  # Linux
open main.pdf      # macOS
```

### 6. Workflow Checklist

When starting a new research project:

- [ ] Create directory structure
- [ ] Set up FiftyOne dataset
- [ ] Compute CLIP embeddings
- [ ] Export data to CSV
- [ ] Extract GPS if applicable
- [ ] Create initial LaTeX document
- [ ] Generate embedding visualization
- [ ] Identify clusters/patterns
- [ ] Create combined analysis figure
- [ ] Write results interpretation
- [ ] Update technical appendix
- [ ] Compile PDF
- [ ] Update CHANGELOG

---

## PROMPT END

---

## Example: Santa Ines Project

The Santa Ines drone imagery project demonstrates this workflow:

| Component | Implementation |
|-----------|----------------|
| Dataset | 97 drone images from vineyard |
| Embeddings | CLIP ViT-B/32 + UMAP |
| Categories | Close-up (89) vs High-altitude (8) |
| GPS | Extracted from EXIF, overlaid on Google satellite |
| Paper | 19 pages, v0.2.1 |

**Key files:**
- `gps_satellite_map.py` - GPS extraction
- `satellite_map.py` - Satellite visualization
- `combined_figure.py` - 4-panel figure
- `analysis.R` - Statistical analysis
- `similarity_analysis.R` - Network analysis

**Adapt for your project by:**
1. Changing `DATASET_NAME`, `IMAGES_PATH`, `OUTPUT_DIR`
2. Defining your own categories and classification logic
3. Customizing figure layouts and color schemes
4. Updating paper sections with project-specific content
