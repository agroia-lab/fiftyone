# Session: 2026-01-14

## Objective
Multi-dataset analysis of agricultural drone imagery using CLIP embeddings.

## Datasets

| Dataset | Location | Images | Clusters | Inter-cluster Dist | Cross-category Edges |
|---------|----------|--------|----------|-------------------|---------------------|
| Santa Ines | -34.4746, -70.9516 | 97 | Close-up (89) / High-alt (8) | 3.56 | 2.7% |
| La Capilla | TBD | 111 | Very-close-up (26) / Medium-alt (85) | 12.93 | 0.0% |

## Folder Structure

```
sessions/2026-01-14/
├── CLAUDE.md                    # This file
├── research/
│   ├── datasets/
│   │   ├── santa_ines/          # First dataset (from Jan 13)
│   │   │   ├── data/            # santa_ines_data.csv, similarity_neighbors.csv
│   │   │   ├── figures/         # Generated plots
│   │   │   └── analysis/        # R scripts
│   │   └── la_capilla/          # Second dataset (new)
│   │       ├── data/            # la_capilla_data.csv, similarity_neighbors.csv
│   │       ├── figures/         # Generated plots
│   │       └── analysis/        # R scripts
│   ├── paper/                   # LaTeX paper (multi-dataset)
│   └── common/                  # Shared analysis scripts
```

## FiftyOne Datasets

| Dataset Name | Brain Key | Description |
|--------------|-----------|-------------|
| santa_ines_dron | clip_viz | CLIP + UMAP (computed Jan 13) |
| santa_ines_dron | clip_similarity | Similarity index |
| la_capilla_dron | clip_viz | CLIP + UMAP (computed Jan 14) |
| la_capilla_dron | clip_similarity | Similarity index |

## La Capilla Analysis Results

### Dataset Summary
- **Source**: `/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo2_ene_2026/La Capilla/Dron/`
- **Images**: 111 DJI drone images
- **Size**: ~1.4 GB total

### Cluster Analysis
| Category | Count | % | UMAP X | UMAP Y | Mean Size |
|----------|-------|---|--------|--------|-----------|
| Very Close-up | 26 | 23.4% | -0.43 ± 0.34 | 2.45 ± 0.48 | 10.4 MB |
| Medium Altitude | 85 | 76.6% | 12.07 ± 1.85 | 5.74 ± 1.63 | 13.1 MB |

### Key Metrics
- **Inter-cluster distance**: 12.93 UMAP units
- **Cross-category edges**: 0/333 (0.0%) - **perfect separation**
- **Cluster cohesion**: Very close-up 0.410, Medium altitude 0.726

### Visual Characteristics
- **Very Close-up** (DJI_0569-0594): Dense foliage fills frame, individual leaves visible, no row structure
- **Medium Altitude** (DJI_0595-0679): Clear row structure, soil paths visible, multiple rows in frame

### Generated Figures
- `embeddings_plot.png` - UMAP scatter plot
- `similarity_network.png` - k-NN network visualization
- `cluster_cohesion.png` - Cohesion bar chart
- `size_analysis.png` - File size distribution
- `distance_distribution.png` - Distance histogram
- `combined_analysis.png` - Summary panel

## Comparison: Santa Ines vs La Capilla

| Metric | Santa Ines | La Capilla |
|--------|------------|------------|
| Total Images | 97 | 111 |
| Cluster Ratio | 92%/8% | 77%/23% |
| Inter-cluster Distance | 3.56 | 12.93 |
| Cross-category Edges | 2.7% | 0.0% |
| Semantic Distinction | Altitude (close vs overview) | Detail level (plant vs row) |

**Key Insight**: La Capilla shows much stronger cluster separation (12.93 vs 3.56), likely because both clusters represent inspection-level imagery with subtle altitude differences, whereas Santa Ines had distinct mapping vs inspection purposes.

## Progress Log

### 2026-01-14
- [x] Create multi-dataset folder structure
- [x] Copy Santa Ines data to new structure
- [x] Create La Capilla dataset in FiftyOne (111 images)
- [x] Compute CLIP embeddings with UMAP visualization
- [x] Identify and tag clusters (Very close-up vs Medium altitude)
- [x] Compute similarity index
- [x] Export data to CSV for R analysis
- [x] Generate R visualizations (6 figures)
- [x] Document results

## Next Steps
- [ ] Extract GPS coordinates from EXIF data
- [ ] Create combined GPS vs embeddings visualization
- [ ] Update LaTeX paper with La Capilla results
- [ ] Compare clustering patterns across sites
