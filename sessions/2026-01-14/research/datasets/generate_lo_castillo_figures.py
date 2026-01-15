#!/usr/bin/env python3
"""
Generate figures for Lo Castillo ground camera dataset.
Creates: embeddings plot, GPS vs embeddings, similarity network, cluster analysis, combined panel
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist
from pathlib import Path
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

# Paths
BASE_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets')
CSV_PATH = BASE_DIR / 'lo_castillo/data/lo_castillo_data.csv'
FIGURES_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/paper/figures')
LOCAL_FIGURES_DIR = BASE_DIR / 'lo_castillo/figures'

PREFIX = 'loc'
TITLE = 'Lo Castillo Ground Camera'

def extract_date_from_filename(filename):
    """Extract date from filename like 20260106_134521.jpg or IMG_1234.HEIC"""
    try:
        # Try YYYYMMDD_ format first
        date_str = filename.split('_')[0]
        if len(date_str) == 8 and date_str.isdigit():
            return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    except:
        pass
    return None

def find_optimal_clusters(coords, max_k=6):
    """Find optimal number of clusters using silhouette score"""
    best_k = 2
    best_score = -1

    for k in range(2, min(max_k + 1, len(coords) // 10)):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(coords)
        score = silhouette_score(coords, labels)
        print(f"    k={k}: silhouette={score:.3f}")
        if score > best_score:
            best_score = score
            best_k = k

    return best_k, best_score

def generate_embeddings_plot(df, title, output_path, cluster_colors=None):
    """Generate UMAP embeddings scatter plot"""
    fig, ax = plt.subplots(figsize=(10, 8))

    if 'cluster' in df.columns and cluster_colors is not None:
        for label in sorted(df['cluster'].unique()):
            mask = df['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                      c=color, alpha=0.6, s=30, label=f'Cluster {label} (n={mask.sum()})')
        ax.legend(loc='best')
    else:
        ax.scatter(df['umap_x'], df['umap_y'], c='steelblue', alpha=0.6, s=30)

    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax.set_title(f'{title}\nUMAP Projection of CLIP Embeddings (n={len(df)})', fontsize=14)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_gps_vs_embeddings(df, title, output_path, cluster_colors=None):
    """Generate side-by-side GPS and embeddings comparison"""
    df_gps = df[(df['latitude'].notna()) & (df['longitude'].notna())].copy()

    if len(df_gps) < 10:
        print(f"  Skipping GPS plot - only {len(df_gps)} points with GPS")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # GPS plot
    ax1 = axes[0]
    if 'cluster' in df_gps.columns and cluster_colors:
        for label in sorted(df_gps['cluster'].unique()):
            mask = df_gps['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax1.scatter(df_gps.loc[mask, 'longitude'], df_gps.loc[mask, 'latitude'],
                       c=color, alpha=0.6, s=30, label=f'Cluster {label}')
        ax1.legend(loc='best')
    else:
        ax1.scatter(df_gps['longitude'], df_gps['latitude'], c='steelblue', alpha=0.6, s=30)

    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.set_title('GPS Coordinates', fontsize=12)

    # Embedding plot
    ax2 = axes[1]
    if 'cluster' in df_gps.columns and cluster_colors:
        for label in sorted(df_gps['cluster'].unique()):
            mask = df_gps['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax2.scatter(df_gps.loc[mask, 'umap_x'], df_gps.loc[mask, 'umap_y'],
                       c=color, alpha=0.6, s=30, label=f'Cluster {label}')
        ax2.legend(loc='best')
    else:
        ax2.scatter(df_gps['umap_x'], df_gps['umap_y'], c='steelblue', alpha=0.6, s=30)

    ax2.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax2.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax2.set_title('CLIP Embedding Space', fontsize=12)

    fig.suptitle(f'{title}: GPS vs Embedding Space (n={len(df_gps)} with GPS)', fontsize=14, y=1.02)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_similarity_network(df, title, output_path, k=3, cluster_colors=None):
    """Generate k-NN similarity network visualization"""
    coords = df[['umap_x', 'umap_y']].values
    distances = cdist(coords, coords)

    fig, ax = plt.subplots(figsize=(10, 8))

    cross_edges = 0
    within_edges = 0

    for i in range(len(df)):
        neighbor_indices = np.argsort(distances[i])[1:k+1]

        for j in neighbor_indices:
            x1, y1 = coords[i]
            x2, y2 = coords[j]

            if 'cluster' in df.columns:
                if df.iloc[i]['cluster'] == df.iloc[j]['cluster']:
                    ax.plot([x1, x2], [y1, y2], 'gray', alpha=0.2, linewidth=0.5)
                    within_edges += 1
                else:
                    ax.plot([x1, x2], [y1, y2], 'orange', alpha=0.5, linewidth=1.0)
                    cross_edges += 1
            else:
                ax.plot([x1, x2], [y1, y2], 'gray', alpha=0.2, linewidth=0.5)

    # Draw points
    if 'cluster' in df.columns and cluster_colors:
        for label in sorted(df['cluster'].unique()):
            mask = df['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                      c=color, alpha=0.8, s=40, zorder=5, label=f'Cluster {label}')
        ax.legend(loc='best')
    else:
        ax.scatter(df['umap_x'], df['umap_y'], c='steelblue', alpha=0.8, s=40, zorder=5)

    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)

    total_edges = within_edges + cross_edges
    if 'cluster' in df.columns:
        cross_pct = (cross_edges / total_edges * 100) if total_edges > 0 else 0
        ax.set_title(f'{title}\nSimilarity Network (k={k}, cross-cluster edges: {cross_pct:.1f}%)', fontsize=14)
    else:
        ax.set_title(f'{title}\nSimilarity Network (k={k})', fontsize=14)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

    return within_edges, cross_edges

def generate_cluster_analysis(df, title, output_path, cluster_colors=None):
    """Generate cluster cohesion bar chart"""
    if 'cluster' not in df.columns:
        return

    coords = df[['umap_x', 'umap_y']].values

    cohesion = {}
    for label in sorted(df['cluster'].unique()):
        mask = df['cluster'] == label
        cluster_coords = coords[mask]
        if len(cluster_coords) > 5:
            dists = cdist(cluster_coords, cluster_coords)
            mean_dist = np.mean([np.sort(d)[1:6].mean() for d in dists])
            cohesion[label] = mean_dist
        else:
            cohesion[label] = 0

    fig, ax = plt.subplots(figsize=(8, 5))

    labels = list(cohesion.keys())
    values = list(cohesion.values())
    colors = [cluster_colors.get(l, 'gray') for l in labels] if cluster_colors else ['steelblue'] * len(labels)

    bars = ax.bar(range(len(labels)), values, color=colors, alpha=0.7)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([f'Cluster {l}\n(n={sum(df["cluster"]==l)})' for l in labels])
    ax.set_ylabel('Mean Distance to 5-NN (UMAP units)', fontsize=12)
    ax.set_title(f'{title}\nCluster Cohesion (lower = tighter cluster)', fontsize=14)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
               f'{val:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_format_analysis(df, title, output_path, cluster_colors=None):
    """Generate file format distribution analysis (JPEG vs HEIC)"""
    if 'file_type' not in df.columns:
        print("  Skipping format analysis - no file_type column")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Format distribution by cluster
    ax1 = axes[0]
    if 'cluster' in df.columns:
        format_cluster = df.groupby(['file_type', 'cluster']).size().unstack(fill_value=0)
        colors = [cluster_colors.get(c, 'gray') for c in format_cluster.columns] if cluster_colors else None
        format_cluster.plot(kind='bar', ax=ax1, color=colors)
        ax1.set_xlabel('File Format', fontsize=12)
        ax1.set_ylabel('Number of Images', fontsize=12)
        ax1.set_title('Images per Format by Cluster', fontsize=12)
        ax1.legend(title='Cluster')
        ax1.tick_params(axis='x', rotation=0)

    # UMAP colored by format
    ax2 = axes[1]
    format_colors = {'JPEG': '#3498db', 'HEIC': '#e74c3c'}
    for fmt in df['file_type'].unique():
        mask = df['file_type'] == fmt
        ax2.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                   c=format_colors.get(fmt, 'gray'), alpha=0.6, s=30, label=f'{fmt} (n={mask.sum()})')

    ax2.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax2.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax2.set_title('Embeddings Colored by File Format', fontsize=12)
    ax2.legend(loc='best')

    fig.suptitle(f'{title}: Format Analysis', fontsize=14, y=1.02)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_combined_analysis(df, title, output_path, cluster_colors=None):
    """Generate combined 2x2 analysis panel"""
    fig = plt.figure(figsize=(16, 12))

    # 1. GPS plot (top left)
    ax1 = fig.add_subplot(2, 2, 1)
    df_gps = df[(df['latitude'].notna()) & (df['longitude'].notna())]
    if len(df_gps) > 0 and 'cluster' in df.columns and cluster_colors:
        for label in sorted(df_gps['cluster'].unique()):
            mask = df_gps['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax1.scatter(df_gps.loc[mask, 'longitude'], df_gps.loc[mask, 'latitude'],
                       c=color, alpha=0.6, s=20, label=f'Cluster {label}')
        ax1.legend(loc='best', fontsize=8)
    elif len(df_gps) > 0:
        ax1.scatter(df_gps['longitude'], df_gps['latitude'], c='steelblue', alpha=0.6, s=20)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title(f'(A) GPS Coordinates (n={len(df_gps)})')

    # 2. UMAP plot (top right)
    ax2 = fig.add_subplot(2, 2, 2)
    if 'cluster' in df.columns and cluster_colors:
        for label in sorted(df['cluster'].unique()):
            mask = df['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax2.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                       c=color, alpha=0.6, s=20, label=f'Cluster {label} (n={mask.sum()})')
        ax2.legend(loc='best', fontsize=8)
    else:
        ax2.scatter(df['umap_x'], df['umap_y'], c='steelblue', alpha=0.6, s=20)
    ax2.set_xlabel('UMAP Dimension 1')
    ax2.set_ylabel('UMAP Dimension 2')
    ax2.set_title(f'(B) CLIP Embedding Space (n={len(df)})')

    # 3. Cluster/Format distribution (bottom left)
    ax3 = fig.add_subplot(2, 2, 3)
    if 'cluster' in df.columns and 'file_type' in df.columns:
        format_cluster = df.groupby(['cluster', 'file_type']).size().unstack(fill_value=0)
        format_colors = {'JPEG': '#3498db', 'HEIC': '#e74c3c'}
        format_cluster.plot(kind='bar', ax=ax3, color=[format_colors.get(c, 'gray') for c in format_cluster.columns])
        ax3.set_xlabel('Cluster')
        ax3.set_ylabel('Number of Images')
        ax3.set_title('(C) Format Distribution by Cluster')
        ax3.legend(title='Format')
        ax3.tick_params(axis='x', rotation=0)
    elif 'cluster' in df.columns:
        cluster_counts = df['cluster'].value_counts().sort_index()
        colors = [cluster_colors.get(c, 'gray') for c in cluster_counts.index] if cluster_colors else None
        bars = ax3.bar(range(len(cluster_counts)), cluster_counts.values, color=colors, alpha=0.7)
        ax3.set_xticks(range(len(cluster_counts)))
        ax3.set_xticklabels([f'Cluster {c}' for c in cluster_counts.index])
        ax3.set_ylabel('Number of Images')
        ax3.set_title('(C) Cluster Distribution')

    # 4. Metrics summary (bottom right)
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    metrics_text = f"Dataset Summary\n{'='*40}\n\n"
    metrics_text += f"Total Images: {len(df)}\n"
    metrics_text += f"Images with GPS: {len(df_gps)} ({len(df_gps)/len(df)*100:.1f}%)\n\n"

    if 'file_type' in df.columns:
        metrics_text += "File Formats:\n"
        for fmt in df['file_type'].unique():
            count = (df['file_type'] == fmt).sum()
            metrics_text += f"  {fmt}: {count} ({count/len(df)*100:.1f}%)\n"
        metrics_text += "\n"

    if 'cluster' in df.columns:
        centroids = df.groupby('cluster')[['umap_x', 'umap_y']].mean()
        if len(centroids) >= 2:
            centroid_dists = cdist(centroids.values, centroids.values)
            inter_dist = centroid_dists[np.triu_indices(len(centroids), k=1)].mean()
            metrics_text += f"Inter-cluster Distance: {inter_dist:.2f} UMAP units\n\n"

        if len(df['cluster'].unique()) > 1:
            sil = silhouette_score(df[['umap_x', 'umap_y']], df['cluster'])
            metrics_text += f"Silhouette Score: {sil:.3f}\n\n"

        metrics_text += "Cluster Sizes:\n"
        for label in sorted(df['cluster'].unique()):
            count = (df['cluster'] == label).sum()
            pct = count / len(df) * 100
            metrics_text += f"  Cluster {label}: {count} ({pct:.1f}%)\n"

    ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=11,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
    ax4.set_title('(D) Dataset Metrics')

    fig.suptitle(f'{title}', fontsize=16, fontweight='bold', y=0.98)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def main():
    print("="*60)
    print("Lo Castillo Ground Camera Figure Generation")
    print("="*60)

    # Ensure output directories exist
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"\nLoading: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"  Loaded {len(df)} images")

    # Show file format breakdown
    if 'file_type' in df.columns:
        print(f"\n  File formats:")
        for fmt in df['file_type'].unique():
            count = (df['file_type'] == fmt).sum()
            print(f"    {fmt}: {count} ({count/len(df)*100:.1f}%)")

    # GPS coverage
    gps_count = df['latitude'].notna().sum()
    print(f"\n  GPS coverage: {gps_count}/{len(df)} ({gps_count/len(df)*100:.1f}%)")

    # Find optimal clusters
    print("\n  Finding optimal clusters...")
    coords = df[['umap_x', 'umap_y']].values
    best_k, best_score = find_optimal_clusters(coords)
    print(f"  Optimal k={best_k}, silhouette={best_score:.3f}")

    # Perform clustering
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(coords)

    # Define cluster colors
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12', '#9b59b6']
    cluster_colors = {i: colors[i % len(colors)] for i in range(best_k)}

    # Generate figures
    print("\nGenerating figures...")

    # 1. Embeddings plot
    generate_embeddings_plot(df, TITLE, FIGURES_DIR / f'{PREFIX}_embeddings_plot.png',
                            cluster_colors=cluster_colors)

    # 2. GPS vs embeddings
    generate_gps_vs_embeddings(df, TITLE, FIGURES_DIR / f'{PREFIX}_gps_vs_embeddings.png',
                              cluster_colors=cluster_colors)

    # 3. Similarity network
    within, cross = generate_similarity_network(df, TITLE, FIGURES_DIR / f'{PREFIX}_similarity_network.png',
                                                k=3, cluster_colors=cluster_colors)
    total = within + cross
    cross_pct = (cross / total * 100) if total > 0 else 0
    print(f"  Network edges: {within} within-cluster, {cross} cross-cluster ({cross_pct:.1f}%)")

    # 4. Cluster cohesion
    generate_cluster_analysis(df, TITLE, FIGURES_DIR / f'{PREFIX}_cluster_cohesion.png',
                             cluster_colors=cluster_colors)

    # 5. Format analysis (JPEG vs HEIC)
    generate_format_analysis(df, TITLE, FIGURES_DIR / f'{PREFIX}_format_analysis.png',
                            cluster_colors=cluster_colors)

    # 6. Combined analysis panel
    generate_combined_analysis(df, TITLE, FIGURES_DIR / f'{PREFIX}_combined_analysis.png',
                              cluster_colors=cluster_colors)

    # Copy figures to local directory as well
    print("\nCopying figures to local dataset directory...")
    import shutil
    for fig_file in FIGURES_DIR.glob(f'{PREFIX}_*.png'):
        shutil.copy(fig_file, LOCAL_FIGURES_DIR / fig_file.name)
        print(f"  Copied: {fig_file.name}")

    # Print summary statistics for paper
    print("\n" + "="*60)
    print("SUMMARY STATISTICS FOR PAPER")
    print("="*60)
    print(f"Total images: {len(df)}")
    print(f"File formats: JPEG={sum(df['file_type']=='JPEG')}, HEIC={sum(df['file_type']=='HEIC')}")
    print(f"GPS coverage: {gps_count}/{len(df)} ({gps_count/len(df)*100:.1f}%)")
    print(f"Optimal clusters: {best_k}")
    print(f"Silhouette score: {best_score:.3f}")

    # Inter-cluster distance
    centroids = df.groupby('cluster')[['umap_x', 'umap_y']].mean()
    if len(centroids) >= 2:
        centroid_dists = cdist(centroids.values, centroids.values)
        inter_dist = centroid_dists[np.triu_indices(len(centroids), k=1)].mean()
        print(f"Inter-cluster distance: {inter_dist:.2f} UMAP units")

    print(f"Cross-cluster edges: {cross}/{total} ({cross_pct:.1f}%)")

    print("\nCluster breakdown:")
    for label in sorted(df['cluster'].unique()):
        count = (df['cluster'] == label).sum()
        pct = count / len(df) * 100

        # Get centroid
        cx = df[df['cluster']==label]['umap_x'].mean()
        cy = df[df['cluster']==label]['umap_y'].mean()
        sx = df[df['cluster']==label]['umap_x'].std()
        sy = df[df['cluster']==label]['umap_y'].std()

        print(f"  Cluster {label}: {count} ({pct:.1f}%), centroid=({cx:.2f}±{sx:.2f}, {cy:.2f}±{sy:.2f})")

    print("\n" + "="*60)
    print("Complete!")
    print("="*60)

if __name__ == '__main__':
    main()
