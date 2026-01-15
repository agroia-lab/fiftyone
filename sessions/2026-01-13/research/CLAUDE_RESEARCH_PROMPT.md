# Claude Research Project Prompt

> Copy this prompt when starting a new research project with Claude Code.

---

## PROMPT

I need help setting up and developing a research project for analyzing image datasets. Follow the workflow established in the Santa Ines project (`/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/research/`).

### Project Details

- **Project Name**: {YOUR_PROJECT_NAME}
- **Dataset Path**: {PATH_TO_YOUR_IMAGES}
- **Output Directory**: {WHERE_TO_SAVE_RESULTS}
- **Research Focus**: {WHAT_YOU_ARE_ANALYZING}

### Tasks

1. **Setup Structure**: Create the research directory structure with `paper/`, `data/`, `figures/` folders

2. **FiftyOne Analysis**:
   - Load images into FiftyOne dataset
   - Compute CLIP embeddings with UMAP visualization
   - Export data to CSV for R/Python analysis

3. **GPS/Geospatial** (if applicable):
   - Extract GPS from EXIF metadata
   - Create satellite map overlay using Google Maps API
   - Key: `AIzaSyAtZgwi1Pg2lKi0w5qutlhTX45ilVsnW-k`

4. **Visualizations**:
   - Embedding space plot (UMAP projection)
   - Category/cluster comparison
   - Representative sample images grid
   - Combined multi-panel figure for paper

5. **LaTeX Paper**:
   - Create `main.tex` with standard sections (abstract, intro, methods, results, discussion, conclusions)
   - Include technical appendix with code documentation
   - Maintain CHANGELOG.txt for version tracking

6. **Documentation**:
   - Update session_summary.md with findings
   - Update CLAUDE.md with project-specific procedures

### Reference Templates

Use code templates from:
- `sessions/2026-01-13/gps_satellite_map.py` - GPS extraction
- `sessions/2026-01-13/satellite_map.py` - Satellite visualization
- `sessions/2026-01-13/combined_figure.py` - Multi-panel figures
- `sessions/2026-01-13/analysis.R` - R statistical analysis
- `sessions/2026-01-13/research/paper/` - LaTeX paper structure

### Customization Points

Replace these placeholders in templates:
- `{DATASET_NAME}` → Your dataset name
- `{IMAGES_PATH}` → Path to your images
- `{CATEGORY_COLUMN}` → Column used for grouping
- `{CAT1}`, `{CAT2}` → Your category names
- `{PAPER_TITLE}` → Your paper title

---

## QUICK START COMMANDS

```bash
# Create project structure
mkdir -p {PROJECT}/research/{paper/{sections,figures},data/{raw,processed}}

# Copy templates
cp sessions/2026-01-13/research/paper/main.tex {PROJECT}/research/paper/
cp sessions/2026-01-13/research/paper/sections/*.tex {PROJECT}/research/paper/sections/

# Run analysis
python {PROJECT}/setup_dataset.py
Rscript {PROJECT}/analysis.R

# Compile paper
cd {PROJECT}/research/paper && pdflatex main.tex && pdflatex main.tex
```

---

## EXAMPLE USAGE

**For a new vineyard analysis project:**

```
I need help setting up a research project for analyzing drone imagery from the Maipo Valley vineyard.

Project Details:
- Project Name: maipo_valley_2026
- Dataset Path: /home/user/data/maipo_valley/drone_images/
- Output Directory: /home/user/sessions/2026-01-15/
- Research Focus: Comparing irrigation zones using visual embeddings

Please follow the Santa Ines workflow and create the full research infrastructure.
```

**For a pest detection project:**

```
I need help analyzing crop images for pest detection patterns.

Project Details:
- Project Name: pest_detection_tomatoes
- Dataset Path: /home/user/data/tomato_fields/inspection/
- Output Directory: /home/user/sessions/2026-01-20/
- Research Focus: Clustering images by pest presence/absence using CLIP

Use the research workflow from sessions/2026-01-13 as reference.
```
