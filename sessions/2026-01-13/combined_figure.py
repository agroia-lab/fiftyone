#!/usr/bin/env python3
"""
Create combined figure for paper: satellite map, GPS vs embeddings, and cluster samples
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
from PIL import Image
import requests
from io import BytesIO
import numpy as np

# Google Maps API key
API_KEY = "AIzaSyAtZgwi1Pg2lKi0w5qutlhTX45ilVsnW-k"

# Load data
data_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_with_gps.csv"
df = pd.read_csv(data_path)
df['category'] = df['tags'].apply(lambda x: 'High Altitude' if 'overview' in str(x) else 'Close-up')

print(f"Loaded {len(df)} images")

# =============================================================================
# Helper functions
# =============================================================================

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

# =============================================================================
# Fetch satellite image
# =============================================================================

center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()
zoom = 18
img_size = 640

url = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_lon}&zoom={zoom}&size={img_size}x{img_size}&maptype=satellite&key={API_KEY}"

print("Fetching satellite image...")
response = requests.get(url)
satellite_img = mpimg.imread(BytesIO(response.content), format='png')
print(f"  Got {satellite_img.shape}")

# Convert GPS to image coordinates
df['img_x'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[0], axis=1)
df['img_y'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[1], axis=1)

# =============================================================================
# Select representative images
# =============================================================================

closeup_df = df[df['category'] == 'Close-up'].sort_values('umap_x')
n_closeup = len(closeup_df)
indices = [0, n_closeup//3, 2*n_closeup//3, n_closeup-1]
closeup_samples = closeup_df.iloc[indices]

highalt_df = df[df['category'] == 'High Altitude']
highalt_samples = highalt_df.sample(min(4, len(highalt_df)), random_state=42)

# =============================================================================
# Create combined figure
# =============================================================================

fig = plt.figure(figsize=(16, 14))
gs = GridSpec(3, 4, figure=fig, height_ratios=[1.2, 1.2, 1], hspace=0.25, wspace=0.15)

# -----------------------------------------------------------------------------
# Row 1: Satellite map (left 2 cols) + Embedding space (right 2 cols)
# -----------------------------------------------------------------------------

# Satellite map with GPS points
ax_sat = fig.add_subplot(gs[0, :2])
ax_sat.imshow(satellite_img, extent=[0, img_size, img_size, 0])

for cat, color, marker in [('Close-up', '#00FF00', 'o'), ('High Altitude', '#FF0000', 's')]:
    mask = df['category'] == cat
    ax_sat.scatter(df.loc[mask, 'img_x'], df.loc[mask, 'img_y'],
                   c=color, s=40, alpha=0.9, edgecolors='white', linewidths=0.5,
                   marker=marker, label=cat)

ax_sat.set_xlim(0, img_size)
ax_sat.set_ylim(img_size, 0)
ax_sat.set_title('A) Physical Location (GPS on Satellite)', fontsize=12, fontweight='bold', loc='left')
ax_sat.legend(loc='upper right', fontsize=9, framealpha=0.9)
ax_sat.axis('off')

# Embedding space plot
ax_emb = fig.add_subplot(gs[0, 2:])

for cat, color, marker in [('Close-up', '#2E86AB', 'o'), ('High Altitude', '#E94F37', 's')]:
    mask = df['category'] == cat
    ax_emb.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                   c=color, s=40, alpha=0.8, edgecolors='white', linewidths=0.5,
                   marker=marker, label=cat)

ax_emb.set_xlabel('UMAP Dimension 1', fontsize=10)
ax_emb.set_ylabel('UMAP Dimension 2', fontsize=10)
ax_emb.set_title('B) CLIP Embedding Space (Visual Similarity)', fontsize=12, fontweight='bold', loc='left')
ax_emb.legend(loc='upper right', fontsize=9)
ax_emb.grid(True, alpha=0.3)

# -----------------------------------------------------------------------------
# Row 2: Close-up representative images
# -----------------------------------------------------------------------------

for idx, (_, row) in enumerate(closeup_samples.iterrows()):
    ax = fig.add_subplot(gs[1, idx])
    img = Image.open(row['filepath'])
    img.thumbnail((600, 600))
    ax.imshow(img)
    ax.set_title(row['filename'].replace('.JPG', ''), fontsize=9)
    ax.axis('off')
    if idx == 0:
        ax.text(-0.15, 0.5, 'C) Close-up\n(Low Alt.)', transform=ax.transAxes,
                fontsize=11, fontweight='bold', va='center', ha='right',
                color='#2E86AB', rotation=90)

# -----------------------------------------------------------------------------
# Row 3: High-altitude representative images
# -----------------------------------------------------------------------------

for idx, (_, row) in enumerate(highalt_samples.iterrows()):
    ax = fig.add_subplot(gs[2, idx])
    img = Image.open(row['filepath'])
    img.thumbnail((600, 600))
    ax.imshow(img)
    ax.set_title(row['filename'].replace('.JPG', ''), fontsize=9)
    ax.axis('off')
    if idx == 0:
        ax.text(-0.15, 0.5, 'D) High Alt.\n(Overview)', transform=ax.transAxes,
                fontsize=11, fontweight='bold', va='center', ha='right',
                color='#E94F37', rotation=90)

# Main title
fig.suptitle('Santa Ines Drone Survey: Spatial Distribution and Visual Clustering',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0.03, 0, 1, 0.96])

# Save to paper figures directory
output_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/research/paper/figures/combined_analysis.png"
plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {output_path}")

# Also save a copy in session directory
output_path2 = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/combined_analysis.png"
plt.savefig(output_path2, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {output_path2}")

print("\n=== Complete ===")
