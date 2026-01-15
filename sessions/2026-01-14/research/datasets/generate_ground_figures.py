#!/usr/bin/env python3
"""
Generate figures for ground camera datasets similar to drone dataset figures.
Creates: embeddings plot, GPS vs embeddings, similarity network, cluster analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from scipy.spatial.distance import cdist
from pathlib import Path
import os
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10

# Dataset configurations
DATASETS = {
    'santa_ines_celular': {
        'csv': 'santa_ines_celular/data/santa_ines_celular_data.csv',
        'prefix': 'sic',
        'title': 'Santa Ines Ground Camera',
        'n_clusters': 2
    },
    'la_capilla_celular': {
        'csv': 'la_capilla_celular/data/la_capilla_celular_data.csv',
        'prefix': 'lcc',
        'title': 'La Capilla Ground Camera',
        'n_clusters': 2
    },
    'apalta': {
        'csv': 'apalta/data/apalta_data.csv',
        'prefix': 'ap',
        'title': 'Apalta Ground Camera',
        'n_clusters': 4
    },
    'camarico': {
        'csv': 'camarico/data/camarico_data.csv',
        'prefix': 'cam',
        'title': 'Camarico Ground Camera',
        'n_clusters': 2
    }
}

BASE_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets')
FIGURES_DIR = Path('/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/paper/figures')

def extract_date_from_filename(filename):
    """Extract date from filename like 20260106_134521.jpg"""
    try:
        date_str = filename.split('_')[0]
        if len(date_str) == 8 and date_str.isdigit():
            return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
    except:
        pass
    return None

def generate_embeddings_plot(df, title, output_path, cluster_labels=None, cluster_colors=None):
    """Generate UMAP embeddings scatter plot"""
    fig, ax = plt.subplots(figsize=(10, 8))

    if cluster_labels is not None and cluster_colors is not None:
        for label in sorted(df['cluster'].unique()):
            mask = df['cluster'] == label
            color = cluster_colors.get(label, 'gray')
            ax.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                      c=color, alpha=0.6, s=30, label=f'Cluster {label} (n={mask.sum()})')
        ax.legend(loc='best')
    else:
        scatter = ax.scatter(df['umap_x'], df['umap_y'], c='steelblue', alpha=0.6, s=30)

    ax.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax.set_title(f'{title}\nUMAP Projection of CLIP Embeddings (n={len(df)})', fontsize=14)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_gps_vs_embeddings(df, title, output_path, cluster_colors=None):
    """Generate side-by-side GPS and embeddings comparison"""
    # Filter to rows with valid GPS
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
    # Compute k-nearest neighbors in UMAP space
    coords = df[['umap_x', 'umap_y']].values
    distances = cdist(coords, coords)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw edges
    cross_edges = 0
    within_edges = 0

    for i in range(len(df)):
        # Get k nearest neighbors (excluding self)
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

    # Calculate cohesion (mean distance to 5 nearest neighbors within same cluster)
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

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
               f'{val:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_temporal_analysis(df, title, output_path, cluster_colors=None):
    """Generate temporal clustering analysis for datasets with date info"""
    # Extract dates from filenames
    df = df.copy()
    df['date'] = df['filename'].apply(extract_date_from_filename)

    if df['date'].isna().all():
        print(f"  Skipping temporal analysis - no dates extractable")
        return

    df_dated = df[df['date'].notna()]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Date distribution by cluster
    ax1 = axes[0]
    if 'cluster' in df_dated.columns:
        date_cluster = df_dated.groupby(['date', 'cluster']).size().unstack(fill_value=0)
        date_cluster.plot(kind='bar', ax=ax1, color=[cluster_colors.get(c, 'gray') for c in date_cluster.columns] if cluster_colors else None)
        ax1.set_xlabel('Survey Date', fontsize=12)
        ax1.set_ylabel('Number of Images', fontsize=12)
        ax1.set_title('Images per Date by Cluster', fontsize=12)
        ax1.legend(title='Cluster')
        ax1.tick_params(axis='x', rotation=45)

    # UMAP colored by date
    ax2 = axes[1]
    unique_dates = df_dated['date'].unique()
    date_colors = plt.cm.tab10(np.linspace(0, 1, len(unique_dates)))
    date_color_map = dict(zip(unique_dates, date_colors))

    for date in unique_dates:
        mask = df_dated['date'] == date
        ax2.scatter(df_dated.loc[mask, 'umap_x'], df_dated.loc[mask, 'umap_y'],
                   c=[date_color_map[date]], alpha=0.6, s=30, label=date)

    ax2.set_xlabel('UMAP Dimension 1', fontsize=12)
    ax2.set_ylabel('UMAP Dimension 2', fontsize=12)
    ax2.set_title('Embeddings Colored by Survey Date', fontsize=12)
    ax2.legend(loc='best', title='Date')

    fig.suptitle(f'{title}: Temporal Analysis', fontsize=14, y=1.02)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {output_path}")

def generate_combined_analysis(df, title, output_path, cluster_colors=None, sample_images=None):
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

    # 3. Cluster statistics (bottom left)
    ax3 = fig.add_subplot(2, 2, 3)
    if 'cluster' in df.columns:
        cluster_counts = df['cluster'].value_counts().sort_index()
        colors = [cluster_colors.get(c, 'gray') for c in cluster_counts.index] if cluster_colors else None
        bars = ax3.bar(range(len(cluster_counts)), cluster_counts.values, color=colors, alpha=0.7)
        ax3.set_xticks(range(len(cluster_counts)))
        ax3.set_xticklabels([f'Cluster {c}' for c in cluster_counts.index])
        ax3.set_ylabel('Number of Images')
        ax3.set_title('(C) Cluster Distribution')

        # Add percentage labels
        total = cluster_counts.sum()
        for bar, count in zip(bars, cluster_counts.values):
            pct = count / total * 100
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{count}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9)
    else:
        ax3.text(0.5, 0.5, 'No cluster data', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('(C) Cluster Distribution')

    # 4. Metrics summary (bottom right)
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.axis('off')

    metrics_text = f"Dataset Summary\n{'='*40}\n\n"
    metrics_text += f"Total Images: {len(df)}\n"
    metrics_text += f"Images with GPS: {len(df_gps)} ({len(df_gps)/len(df)*100:.1f}%)\n\n"

    if 'cluster' in df.columns:
        # Calculate inter-cluster distance
        centroids = df.groupby('cluster')[['umap_x', 'umap_y']].mean()
        if len(centroids) >= 2:
            centroid_dists = cdist(centroids.values, centroids.values)
            inter_dist = centroid_dists[np.triu_indices(len(centroids), k=1)].mean()
            metrics_text += f"Inter-cluster Distance: {inter_dist:.2f} UMAP units\n\n"

        # Silhouette score
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

def process_dataset(name, config):
    """Process a single dataset and generate all figures"""
    print(f"\n{'='*60}")
    print(f"Processing: {config['title']}")
    print(f"{'='*60}")

    # Load data
    csv_path = BASE_DIR / config['csv']
    if not csv_path.exists():
        print(f"  ERROR: CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"  Loaded {len(df)} images")

    # Perform K-means clustering
    n_clusters = config['n_clusters']
    coords = df[['umap_x', 'umap_y']].values
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(coords)

    # Calculate silhouette score
    sil = silhouette_score(coords, df['cluster'])
    print(f"  K-means clustering: k={n_clusters}, silhouette={sil:.3f}")

    # Define cluster colors
    colors = ['#2ecc71', '#e74c3c', '#3498db', '#f39c12', '#9b59b6']
    cluster_colors = {i: colors[i % len(colors)] for i in range(n_clusters)}

    prefix = config['prefix']
    title = config['title']

    # Generate figures
    print("\n  Generating figures...")

    # 1. Embeddings plot
    generate_embeddings_plot(df, title, FIGURES_DIR / f'{prefix}_embeddings_plot.png',
                            cluster_labels=True, cluster_colors=cluster_colors)

    # 2. GPS vs embeddings
    generate_gps_vs_embeddings(df, title, FIGURES_DIR / f'{prefix}_gps_vs_embeddings.png',
                              cluster_colors=cluster_colors)

    # 3. Similarity network
    within, cross = generate_similarity_network(df, title, FIGURES_DIR / f'{prefix}_similarity_network.png',
                                                k=3, cluster_colors=cluster_colors)
    total = within + cross
    if total > 0:
        print(f"  Network edges: {within} within-cluster, {cross} cross-cluster ({cross/total*100:.1f}%)")

    # 4. Cluster cohesion
    generate_cluster_analysis(df, title, FIGURES_DIR / f'{prefix}_cluster_cohesion.png',
                             cluster_colors=cluster_colors)

    # 5. Temporal analysis (for datasets with date info in filename)
    generate_temporal_analysis(df, title, FIGURES_DIR / f'{prefix}_temporal_analysis.png',
                              cluster_colors=cluster_colors)

    # 6. Combined analysis panel
    generate_combined_analysis(df, title, FIGURES_DIR / f'{prefix}_combined_analysis.png',
                              cluster_colors=cluster_colors)

    print(f"\n  Completed: {config['title']}")
    return df, sil

def main():
    """Main entry point"""
    print("="*60)
    print("Ground Camera Figure Generation")
    print("="*60)

    # Ensure output directory exists
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    results = {}
    for name, config in DATASETS.items():
        result = process_dataset(name, config)
        if result:
            results[name] = result

    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for name, (df, sil) in results.items():
        print(f"  {name}: {len(df)} images, silhouette={sil:.3f}")

    print("\nAll figures saved to:", FIGURES_DIR)

if __name__ == '__main__':
    main()
