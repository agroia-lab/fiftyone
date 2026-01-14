#!/usr/bin/env python3
"""
Create satellite map with GPS points using Google Maps Static API
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from io import BytesIO
import numpy as np

# Google Maps API key
API_KEY = "AIzaSyAtZgwi1Pg2lKi0w5qutlhTX45ilVsnW-k"

# Load data with GPS coordinates
data_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_with_gps.csv"
df = pd.read_csv(data_path)

# Create category column
df['category'] = df['tags'].apply(lambda x: 'High Altitude' if 'overview' in str(x) else 'Close-up')

print(f"Data loaded: {len(df)} images")
print(f"Lat range: {df['latitude'].min():.6f} to {df['latitude'].max():.6f}")
print(f"Lon range: {df['longitude'].min():.6f} to {df['longitude'].max():.6f}")

# Calculate bounds
lat_min, lat_max = df['latitude'].min(), df['latitude'].max()
lon_min, lon_max = df['longitude'].min(), df['longitude'].max()

# Add padding
lat_pad = (lat_max - lat_min) * 0.1
lon_pad = (lon_max - lon_min) * 0.1
lat_min -= lat_pad
lat_max += lat_pad
lon_min -= lon_pad
lon_max += lon_pad

center_lat = (lat_min + lat_max) / 2
center_lon = (lon_min + lon_max) / 2

print(f"Center: {center_lat:.6f}, {center_lon:.6f}")

# Fetch satellite image from Google Maps Static API
zoom = 18
img_size = 640  # Max free size

url = f"https://maps.googleapis.com/maps/api/staticmap?center={center_lat},{center_lon}&zoom={zoom}&size={img_size}x{img_size}&maptype=satellite&key={API_KEY}"

print(f"\nFetching satellite image...")
response = requests.get(url)

if response.status_code == 200:
    img = mpimg.imread(BytesIO(response.content), format='png')
    print(f"Image fetched: {img.shape}")
else:
    print(f"Error fetching image: {response.status_code}")
    print(response.text)
    exit(1)

# Calculate the extent of the image in lat/lon
# At zoom level z, the world is divided into 2^z tiles
# Each tile is 256 pixels, we have 640x640 image
def lat_lon_to_pixels(lat, lon, zoom, img_size):
    """Convert lat/lon to pixel coordinates in the image"""
    # Mercator projection
    lat_rad = np.radians(lat)
    n = 2 ** zoom
    x = (lon + 180) / 360 * n * 256
    y = (1 - np.log(np.tan(lat_rad) + 1/np.cos(lat_rad)) / np.pi) / 2 * n * 256
    return x, y

# Get center pixel coordinates
cx, cy = lat_lon_to_pixels(center_lat, center_lon, zoom, img_size)

# Convert GPS points to pixel coordinates relative to image
def gps_to_image_coords(lat, lon, center_lat, center_lon, zoom, img_size):
    """Convert GPS to image pixel coordinates"""
    cx, cy = lat_lon_to_pixels(center_lat, center_lon, zoom, img_size)
    px, py = lat_lon_to_pixels(lat, lon, zoom, img_size)
    # Relative to image center
    x = (px - cx) + img_size / 2
    y = (py - cy) + img_size / 2
    return x, y

# Convert all points
df['img_x'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[0], axis=1)
df['img_y'] = df.apply(lambda r: gps_to_image_coords(r['latitude'], r['longitude'], center_lat, center_lon, zoom, img_size)[1], axis=1)

# Create the plot
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Left plot: Satellite map with GPS points
ax1 = axes[0]
ax1.imshow(img, extent=[0, img_size, img_size, 0])

# Plot points by category
for cat, color in [('Close-up', '#00FF00'), ('High Altitude', '#FF0000')]:
    mask = df['category'] == cat
    ax1.scatter(df.loc[mask, 'img_x'], df.loc[mask, 'img_y'],
                c=color, s=50, alpha=0.8, edgecolors='white', linewidths=0.5,
                label=cat)

ax1.set_xlim(0, img_size)
ax1.set_ylim(img_size, 0)
ax1.set_title('Physical Location (GPS) - Satellite View', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.axis('off')

# Right plot: CLIP Embedding space
ax2 = axes[1]
for cat, color in [('Close-up', '#2E86AB'), ('High Altitude', '#E94F37')]:
    mask = df['category'] == cat
    ax2.scatter(df.loc[mask, 'umap_x'], df.loc[mask, 'umap_y'],
                c=color, s=50, alpha=0.8, edgecolors='white', linewidths=0.5,
                label=cat)

ax2.set_xlabel('UMAP Dimension 1')
ax2.set_ylabel('UMAP Dimension 2')
ax2.set_title('CLIP Embedding Space (Visual Similarity)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.suptitle('Santa Ines Drone Images: GPS Location vs Visual Embedding', fontsize=14, fontweight='bold')
plt.tight_layout()

# Save
output_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/satellite_gps_vs_embedding.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"\nSaved: {output_path}")

# Also save just the satellite map
fig2, ax = plt.subplots(figsize=(10, 10))
ax.imshow(img, extent=[0, img_size, img_size, 0])

for cat, color in [('Close-up', '#00FF00'), ('High Altitude', '#FF0000')]:
    mask = df['category'] == cat
    ax.scatter(df.loc[mask, 'img_x'], df.loc[mask, 'img_y'],
               c=color, s=80, alpha=0.9, edgecolors='white', linewidths=1,
               label=cat)

ax.set_xlim(0, img_size)
ax.set_ylim(img_size, 0)
ax.set_title('Santa Ines Drone Survey - GPS on Satellite', fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.axis('off')

output_path2 = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/satellite_gps_only.png"
plt.savefig(output_path2, dpi=150, bbox_inches='tight', facecolor='black')
print(f"Saved: {output_path2}")

print("\n=== Complete ===")
