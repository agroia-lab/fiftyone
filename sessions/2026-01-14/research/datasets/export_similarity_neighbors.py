#!/usr/bin/env python3
"""
Export similarity neighbors for all ground camera datasets.
Required for R similarity_analysis.R scripts.
Uses UMAP coordinates to compute k-nearest neighbors.
"""

import fiftyone as fo
import pandas as pd
from pathlib import Path
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Ground camera datasets
DATASETS = [
    "santa_ines_celular",
    "la_capilla_celular",
    "apalta",
    "camarico",
    "lo_castillo"
]

BASE_DIR = Path("/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets")

def export_similarity_neighbors(dataset_name, k=10):
    """Export k-nearest neighbors for a dataset using UMAP coordinates."""
    print(f"\n{'='*60}")
    print(f"Exporting similarity neighbors for: {dataset_name}")
    print(f"{'='*60}")

    # Load dataset
    if not fo.dataset_exists(dataset_name):
        print(f"  Dataset '{dataset_name}' not found. Skipping...")
        return None

    dataset = fo.load_dataset(dataset_name)
    print(f"  Loaded {len(dataset)} samples")

    # Check for visualization brain run
    if "clip_viz" not in dataset.list_brain_runs():
        print(f"  No CLIP visualization found. Skipping...")
        return None

    # Get visualization results for UMAP coordinates
    viz_results = dataset.load_brain_results("clip_viz")
    points = viz_results.current_points

    if points is None or len(points) == 0:
        print(f"  No UMAP points found. Skipping...")
        return None

    # Build filename list
    filenames = [Path(sample.filepath).name for sample in dataset]

    # Compute k-nearest neighbors using sklearn
    print(f"  Computing {k}-nearest neighbors...")
    knn = NearestNeighbors(n_neighbors=k+1, metric='euclidean')  # k+1 to include self
    knn.fit(points)
    distances, indices = knn.kneighbors(points)

    # Export neighbors
    neighbors_data = []

    for i in range(len(filenames)):
        source_filename = filenames[i]
        source_x, source_y = points[i]

        # Skip self (index 0), get k neighbors
        for rank in range(1, k+1):
            neighbor_idx = indices[i, rank]
            dist = distances[i, rank]

            neighbors_data.append({
                'source': source_filename,
                'neighbor': filenames[neighbor_idx],
                'rank': rank,
                'distance': dist,
                'source_umap_x': source_x,
                'source_umap_y': source_y,
                'neighbor_umap_x': points[neighbor_idx][0],
                'neighbor_umap_y': points[neighbor_idx][1]
            })

    # Save to CSV
    output_dir = BASE_DIR / dataset_name / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(neighbors_data)
    csv_path = output_dir / "similarity_neighbors.csv"
    df.to_csv(csv_path, index=False)

    print(f"  Saved: {csv_path}")
    print(f"  Total neighbor pairs: {len(df)}")

    return df

def main():
    results = {}

    for dataset_name in DATASETS:
        try:
            df = export_similarity_neighbors(dataset_name, k=10)
            if df is not None:
                results[dataset_name] = len(df)
        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, count in results.items():
        print(f"  {name}: {count} neighbor pairs exported")

if __name__ == "__main__":
    main()
