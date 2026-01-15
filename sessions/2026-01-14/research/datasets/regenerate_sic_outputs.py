#!/usr/bin/env python3
"""
Regenerate figures and geo files for updated Santa Ines Celular dataset.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist
from pathlib import Path
import simplekml
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150

BASE_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets')
FIGURES_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/paper/figures')
DATA_DIR = BASE_DIR / 'santa_ines_celular/data'

def extract_date_from_filename(filename):
    """Extract date from filename like 20260106_134521.jpg or IMG_1234.HEIC"""
    try:
        # Try YYYYMMDD format
        parts = filename.split('_')[0]
        if len(parts) == 8 and parts.isdigit():
            return datetime.strptime(parts, '%Y%m%d').strftime('%Y-%m-%d')
    except:
        pass
    return None

def main():
    print("="*60)
    print("Regenerating Santa Ines Celular Outputs")
    print("="*60)

    # Load data
    df = pd.read_csv(DATA_DIR / 'santa_ines_celular_data.csv')
    print(f"Loaded {len(df)} images")
    print(f"  JPEG: {(df['file_type']=='JPEG').sum()}")
    print(f"  HEIC: {(df['file_type']=='HEIC').sum()}")

    # Perform K-means clustering
    coords = df[['umap_x', 'umap_y']].values
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(coords)

    sil = silhouette_score(coords, df['cluster'])
    print(f"\nK-means clustering: k=2, silhouette={sil:.3f}")

    # Extract dates
    df['date'] = df['filename'].apply(extract_date_from_filename)

    # Cluster colors
    colors = {0: '#2ecc71', 1: '#e74c3c'}

    # Calculate metrics
    centroids = df.groupby('cluster')[['umap_x', 'umap_y']].mean()
    inter_dist = np.sqrt(((centroids.iloc[0] - centroids.iloc[1])**2).sum())

    # Calculate cross-cluster edges
    k = 3
    distances = cdist(coords, coords)
    cross_edges = 0
    within_edges = 0
    for i in range(len(df)):
        neighbors = np.argsort(distances[i])[1:k+1]
        for j in neighbors:
            if df.iloc[i]['cluster'] == df.iloc[j]['cluster']:
                within_edges += 1
            else:
                cross_edges += 1

    total_edges = within_edges + cross_edges
    cross_pct = cross_edges / total_edges * 100 if total_edges > 0 else 0

    print(f"Inter-cluster distance: {inter_dist:.2f}")
    print(f"Cross-cluster edges: {cross_edges}/{total_edges} ({cross_pct:.1f}%)")

    # =========================================================================
    # Generate Figures
    # =========================================================================
    print("\nGenerating figures...")

    # 1. Combined analysis
    fig = plt.figure(figsize=(16, 12))

    # GPS plot
    ax1 = fig.add_subplot(2, 2, 1)
    for label in [0, 1]:
        mask = df['cluster'] == label
        ax1.scatter(df.loc[mask, 'longitude'], df.loc[mask, 'latitude'],
                   c=colors[label], alpha=0.5, s=10, label=f'Cluster {label}')
    ax1.legend(fontsize=8)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'(A) GPS Coordinates (n={len(df)})')

    # UMAP plot
    ax2 = fig.add_subplot(2, 2, 2)
    for label in [0, 1]:
        mask = df['cluster'] == label
        ax2.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                   c=colors[label], alpha=0.5, s=10, label=f'Cluster {label} (n={mask.sum()})')
    ax2.legend(fontsize=8)
    ax2.set_xlabel('UMAP Dimension 1')
    ax2.set_ylabel('UMAP Dimension 2')
    ax2.set_title(f'(B) CLIP Embedding Space')

    # Cluster distribution by file type
    ax3 = fig.add_subplot(2, 2, 3)
    cluster_type = df.groupby(['cluster', 'file_type']).size().unstack(fill_value=0)
    cluster_type.plot(kind='bar', ax=ax3, color=['#3498db', '#f39c12'])
    ax3.set_xlabel('Cluster')
    ax3.set_ylabel('Number of Images')
    ax3.set_title('(C) Cluster Distribution by File Type')
    ax3.legend(title='Format')
    ax3.tick_params(axis='x', rotation=0)

    # Metrics
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')
    metrics = f"""Dataset Summary
{'='*40}

Total Images: {len(df)}
  - JPEG: {(df['file_type']=='JPEG').sum()}
  - HEIC: {(df['file_type']=='HEIC').sum()}

GPS Coverage: {df['latitude'].notna().sum()}/{len(df)} (100.0%)

Clustering Metrics:
  - Silhouette Score: {sil:.3f}
  - Inter-cluster Distance: {inter_dist:.2f}
  - Cross-cluster Edges: {cross_pct:.1f}%

Cluster Sizes:
  - Cluster 0: {(df['cluster']==0).sum()} ({(df['cluster']==0).sum()/len(df)*100:.1f}%)
  - Cluster 1: {(df['cluster']==1).sum()} ({(df['cluster']==1).sum()/len(df)*100:.1f}%)
"""
    ax4.text(0.1, 0.9, metrics, transform=ax4.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
    ax4.set_title('(D) Dataset Metrics')

    fig.suptitle('Santa Ines Ground Camera (Updated: 1,325 images)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'sic_combined_analysis.png', bbox_inches='tight')
    plt.close()
    print("  Saved: sic_combined_analysis.png")

    # 2. Embeddings plot
    fig, ax = plt.subplots(figsize=(10, 8))
    for label in [0, 1]:
        mask = df['cluster'] == label
        ax.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                  c=colors[label], alpha=0.5, s=20, label=f'Cluster {label} (n={mask.sum()})')
    ax.legend()
    ax.set_xlabel('UMAP Dimension 1')
    ax.set_ylabel('UMAP Dimension 2')
    ax.set_title(f'Santa Ines Ground Camera - UMAP Projection (n={len(df)})')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'sic_embeddings_plot.png', bbox_inches='tight')
    plt.close()
    print("  Saved: sic_embeddings_plot.png")

    # 3. Similarity network
    fig, ax = plt.subplots(figsize=(10, 8))
    # Draw subset of edges for visibility
    np.random.seed(42)
    sample_idx = np.random.choice(len(df), min(500, len(df)), replace=False)
    for i in sample_idx:
        neighbors = np.argsort(distances[i])[1:k+1]
        for j in neighbors:
            if j in sample_idx:
                x1, y1 = coords[i]
                x2, y2 = coords[j]
                if df.iloc[i]['cluster'] == df.iloc[j]['cluster']:
                    ax.plot([x1, x2], [y1, y2], 'gray', alpha=0.1, linewidth=0.3)
                else:
                    ax.plot([x1, x2], [y1, y2], 'orange', alpha=0.5, linewidth=0.8)

    for label in [0, 1]:
        mask = df['cluster'] == label
        ax.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                  c=colors[label], alpha=0.6, s=15, zorder=5, label=f'Cluster {label}')
    ax.legend()
    ax.set_xlabel('UMAP Dimension 1')
    ax.set_ylabel('UMAP Dimension 2')
    ax.set_title(f'Santa Ines Ground Camera - Similarity Network\n(k={k}, cross-cluster: {cross_pct:.1f}%)')
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'sic_similarity_network.png', bbox_inches='tight')
    plt.close()
    print("  Saved: sic_similarity_network.png")

    # 4. Temporal analysis
    df_dated = df[df['date'].notna()]
    if len(df_dated) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Date by cluster
        ax1 = axes[0]
        date_cluster = df_dated.groupby(['date', 'cluster']).size().unstack(fill_value=0)
        date_cluster.plot(kind='bar', ax=ax1, color=[colors[0], colors[1]])
        ax1.set_xlabel('Survey Date')
        ax1.set_ylabel('Number of Images')
        ax1.set_title('Images per Date by Cluster')
        ax1.tick_params(axis='x', rotation=45)

        # UMAP by date
        ax2 = axes[1]
        unique_dates = sorted(df_dated['date'].unique())
        date_colors = plt.cm.tab10(np.linspace(0, 1, len(unique_dates)))
        for i, date in enumerate(unique_dates):
            mask = df_dated['date'] == date
            ax2.scatter(df_dated.loc[mask, 'umap_x'], df_dated.loc[mask, 'umap_y'],
                       c=[date_colors[i]], alpha=0.5, s=15, label=date)
        ax2.legend(title='Date')
        ax2.set_xlabel('UMAP Dimension 1')
        ax2.set_ylabel('UMAP Dimension 2')
        ax2.set_title('Embeddings Colored by Survey Date')

        fig.suptitle('Santa Ines Ground Camera - Temporal Analysis', fontsize=14)
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / 'sic_temporal_analysis.png', bbox_inches='tight')
        plt.close()
        print("  Saved: sic_temporal_analysis.png")

    # 5. GPS vs Embeddings
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax1 = axes[0]
    for label in [0, 1]:
        mask = df['cluster'] == label
        ax1.scatter(df.loc[mask, 'longitude'], df.loc[mask, 'latitude'],
                   c=colors[label], alpha=0.5, s=10, label=f'Cluster {label}')
    ax1.legend()
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title('GPS Coordinates')

    ax2 = axes[1]
    for label in [0, 1]:
        mask = df['cluster'] == label
        ax2.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                   c=colors[label], alpha=0.5, s=10, label=f'Cluster {label}')
    ax2.legend()
    ax2.set_xlabel('UMAP Dimension 1')
    ax2.set_ylabel('UMAP Dimension 2')
    ax2.set_title('CLIP Embedding Space')

    fig.suptitle(f'Santa Ines Ground Camera: GPS vs Embedding Space (n={len(df)})', fontsize=14)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'sic_gps_vs_embeddings.png', bbox_inches='tight')
    plt.close()
    print("  Saved: sic_gps_vs_embeddings.png")

    # 6. Cluster cohesion
    fig, ax = plt.subplots(figsize=(8, 5))
    cohesion = {}
    for label in [0, 1]:
        mask = df['cluster'] == label
        cluster_coords = coords[mask]
        dists = cdist(cluster_coords, cluster_coords)
        cohesion[label] = np.mean([np.sort(d)[1:6].mean() for d in dists])

    bars = ax.bar([0, 1], [cohesion[0], cohesion[1]], color=[colors[0], colors[1]], alpha=0.7)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([f'Cluster 0\n(n={(df["cluster"]==0).sum()})',
                        f'Cluster 1\n(n={(df["cluster"]==1).sum()})'])
    ax.set_ylabel('Mean Distance to 5-NN')
    ax.set_title('Santa Ines Ground Camera - Cluster Cohesion')
    for bar, val in zip(bars, cohesion.values()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
               f'{val:.3f}', ha='center', fontsize=10)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / 'sic_cluster_cohesion.png', bbox_inches='tight')
    plt.close()
    print("  Saved: sic_cluster_cohesion.png")

    # =========================================================================
    # Generate Geo Files
    # =========================================================================
    print("\nGenerating geo files...")

    # KML
    kml = simplekml.Kml()
    for _, row in df.iterrows():
        pnt = kml.newpoint(name=row['filename'])
        pnt.coords = [(row['longitude'], row['latitude'])]
        pnt.description = f"Cluster: {row['cluster']}\nType: {row['file_type']}"

    kml_path = DATA_DIR / 'santa_ines_celular_photos.kml'
    kml.save(str(kml_path))
    print(f"  Saved: {kml_path}")

    # KMZ
    kmz_path = DATA_DIR / 'santa_ines_celular_photos.kmz'
    kml.savekmz(str(kmz_path))
    print(f"  Saved: {kmz_path}")

    # Shapefile
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    gdf_utm = gdf.to_crs("EPSG:32719")

    shp_dir = DATA_DIR / 'santa_ines_celular_utm19s'
    shp_dir.mkdir(exist_ok=True)
    shp_path = shp_dir / 'santa_ines_celular_utm19s.shp'
    gdf_utm.to_file(str(shp_path))
    print(f"  Saved: {shp_path}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Total images: {len(df)}")
    print(f"  JPEG: {(df['file_type']=='JPEG').sum()}")
    print(f"  HEIC: {(df['file_type']=='HEIC').sum()}")
    print(f"GPS coverage: 100%")
    print(f"Silhouette score: {sil:.3f}")
    print(f"Inter-cluster distance: {inter_dist:.2f}")
    print(f"Cross-cluster edges: {cross_pct:.1f}%")

    # Date analysis
    if len(df_dated) > 0:
        print(f"\nTemporal breakdown (JPEG only):")
        for date in sorted(df_dated['date'].unique()):
            count = (df_dated['date'] == date).sum()
            print(f"  {date}: {count} images")

if __name__ == "__main__":
    main()
