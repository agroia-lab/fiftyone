#!/usr/bin/env python3
"""
Create side-by-side comparison of representative images from each cluster
"""

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# Load data
data_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_with_gps.csv"
df = pd.read_csv(data_path)

# Create category column
df['category'] = df['tags'].apply(lambda x: 'High Altitude' if 'overview' in str(x) else 'Close-up')

print(f"Close-up images: {(df['category'] == 'Close-up').sum()}")
print(f"High Altitude images: {(df['category'] == 'High Altitude').sum()}")

# Select 4 representative images from each cluster
# For Close-up: spread across the embedding space
closeup_df = df[df['category'] == 'Close-up'].copy()
closeup_df = closeup_df.sort_values('umap_x')  # Sort by UMAP x to get spread
n_closeup = len(closeup_df)
indices = [0, n_closeup//3, 2*n_closeup//3, n_closeup-1]
closeup_samples = closeup_df.iloc[indices]

# For High Altitude: take all if <= 4, otherwise sample
highalt_df = df[df['category'] == 'High Altitude'].copy()
if len(highalt_df) <= 4:
    highalt_samples = highalt_df
else:
    highalt_samples = highalt_df.sample(4, random_state=42)

print(f"\nSelected Close-up images:")
for _, row in closeup_samples.iterrows():
    print(f"  {row['filename']}")

print(f"\nSelected High Altitude images:")
for _, row in highalt_samples.iterrows():
    print(f"  {row['filename']}")

# Create the figure
fig, axes = plt.subplots(2, 4, figsize=(16, 9))

# Top row: Close-up images
for idx, (_, row) in enumerate(closeup_samples.iterrows()):
    ax = axes[0, idx]
    img = Image.open(row['filepath'])
    # Resize for display
    img.thumbnail((800, 800))
    ax.imshow(img)
    ax.set_title(row['filename'].replace('.JPG', ''), fontsize=10)
    ax.axis('off')

# Bottom row: High Altitude images
for idx, (_, row) in enumerate(highalt_samples.iterrows()):
    ax = axes[1, idx]
    img = Image.open(row['filepath'])
    img.thumbnail((800, 800))
    ax.imshow(img)
    ax.set_title(row['filename'].replace('.JPG', ''), fontsize=10)
    ax.axis('off')

# Add row labels
fig.text(0.02, 0.72, 'Close-up\n(Low Altitude)', fontsize=14, fontweight='bold',
         va='center', ha='center', rotation=90, color='#2E86AB')
fig.text(0.02, 0.28, 'High Altitude\n(Overview)', fontsize=14, fontweight='bold',
         va='center', ha='center', rotation=90, color='#E94F37')

plt.suptitle('Santa Ines Drone Survey: Representative Images by Cluster',
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0.04, 0, 1, 0.95])

# Save
output_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/cluster_representative_images.png"
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nSaved: {output_path}")

print("\n=== Complete ===")
