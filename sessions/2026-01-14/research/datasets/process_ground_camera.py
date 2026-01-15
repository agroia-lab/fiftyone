#!/usr/bin/env python3
"""
Process ground camera (celular) datasets with CLIP embeddings.
Creates FiftyOne datasets, computes embeddings, extracts GPS, and exports data.
"""

import os
import sys
import csv
import glob
from pathlib import Path
import fiftyone as fo
import fiftyone.brain as fob
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pillow_heif

# Register HEIC opener
pillow_heif.register_heif_opener()

# Dataset configurations
DATASETS = {
    "santa_ines_celular": {
        "path": "/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo1_ene_2026/Santa Ines/Celular/",
        "pattern": "*.jpg",
        "name": "Santa Ines (Ground Camera)",
        "site": "Santa Ines"
    },
    "la_capilla_celular": {
        "path": "/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo2_ene_2026/La Capilla/Celular/",
        "pattern": "*.jpg",
        "name": "La Capilla (Ground Camera)",
        "site": "La Capilla"
    },
    "apalta": {
        "path": "/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/Campo3_enero26/Apalta/Celular/",
        "pattern": "*.HEIC",
        "name": "Apalta (Ground Camera)",
        "site": "Apalta"
    },
    "camarico": {
        "path": "/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo4_enero26/Camarico/Celular/",
        "pattern": "*.jpg",
        "name": "Camarico (Ground Camera)",
        "site": "Camarico"
    }
}

BASE_DIR = Path(__file__).parent

def get_exif_data(image_path):
    """Extract EXIF data from image."""
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
        return None

def get_gps_info(exif_data):
    """Extract GPS info from EXIF data."""
    if not exif_data or 'GPSInfo' not in exif_data:
        return None
    gps_info = {}
    for key, val in exif_data['GPSInfo'].items():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = val
    return gps_info

def convert_to_degrees(value):
    """Convert GPS coordinates to degrees."""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)

def get_coordinates(gps_info):
    """Get latitude and longitude from GPS info."""
    if not gps_info:
        return None, None
    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        if gps_info['GPSLatitudeRef'] == 'S':
            lat = -lat
        lon = convert_to_degrees(gps_info['GPSLongitude'])
        if gps_info['GPSLongitudeRef'] == 'W':
            lon = -lon
        return lat, lon
    except (KeyError, TypeError):
        return None, None

def process_dataset(dataset_key, config):
    """Process a single dataset."""
    print(f"\n{'='*60}")
    print(f"Processing: {config['name']}")
    print(f"{'='*60}")

    # Check if dataset exists
    if dataset_key in fo.list_datasets():
        print(f"Dataset '{dataset_key}' already exists. Loading...")
        dataset = fo.load_dataset(dataset_key)
    else:
        # Create dataset
        print(f"Creating dataset from {config['path']}...")

        # Get image files
        image_files = glob.glob(os.path.join(config['path'], config['pattern']))
        image_files.extend(glob.glob(os.path.join(config['path'], config['pattern'].lower())))
        image_files = sorted(list(set(image_files)))

        print(f"Found {len(image_files)} images")

        if len(image_files) == 0:
            print(f"No images found! Skipping...")
            return None

        # Create samples
        samples = []
        for filepath in image_files:
            sample = fo.Sample(filepath=filepath)
            samples.append(sample)

        dataset = fo.Dataset(name=dataset_key)
        dataset.add_samples(samples)
        dataset.persistent = True

    print(f"Dataset has {len(dataset)} samples")

    # Compute metadata
    print("Computing metadata...")
    dataset.compute_metadata()

    # Compute CLIP embeddings with UMAP
    if "clip_viz" not in dataset.list_brain_runs():
        print("Computing CLIP embeddings with UMAP visualization...")
        fob.compute_visualization(
            dataset,
            brain_key="clip_viz",
            model="clip-vit-base32-torch",
            method="umap"
        )
    else:
        print("CLIP visualization already computed")

    # Compute similarity index
    if "clip_similarity" not in dataset.list_brain_runs():
        print("Computing similarity index...")
        fob.compute_similarity(
            dataset,
            brain_key="clip_similarity",
            embeddings="clip_viz"
        )
    else:
        print("Similarity index already computed")

    return dataset

def extract_gps_and_export(dataset, dataset_key, config):
    """Extract GPS and export to CSV."""
    print(f"\nExtracting GPS and exporting data for {config['name']}...")

    output_dir = BASE_DIR / dataset_key / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get visualization results
    viz_results = dataset.load_brain_results("clip_viz")
    points = viz_results.points

    # Export data
    csv_path = output_dir / f"{dataset_key}_data.csv"

    rows = []
    for i, sample in enumerate(dataset):
        # Get UMAP coordinates
        umap_x, umap_y = points[i] if i < len(points) else (0, 0)

        # Extract GPS
        exif = get_exif_data(sample.filepath)
        gps_info = get_gps_info(exif)
        lat, lon = get_coordinates(gps_info)

        rows.append({
            'sample_id': str(sample.id),
            'filepath': sample.filepath,
            'filename': os.path.basename(sample.filepath),
            'umap_x': umap_x,
            'umap_y': umap_y,
            'tags': ','.join(sample.tags) if sample.tags else '',
            'width': sample.metadata.width if sample.metadata else '',
            'height': sample.metadata.height if sample.metadata else '',
            'size_bytes': sample.metadata.size_bytes if sample.metadata else '',
            'latitude': lat if lat else '',
            'longitude': lon if lon else '',
            'site': config['site'],
            'camera_type': 'ground'
        })

        if lat:
            print(f"  {os.path.basename(sample.filepath)}: {lat:.6f}, {lon:.6f}")

    # Write CSV
    fieldnames = ['sample_id', 'filepath', 'filename', 'umap_x', 'umap_y', 'tags',
                  'width', 'height', 'size_bytes', 'latitude', 'longitude', 'site', 'camera_type']

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported to {csv_path}")

    # Count GPS
    gps_count = sum(1 for r in rows if r['latitude'])
    print(f"GPS coordinates found: {gps_count}/{len(rows)}")

    return rows, csv_path

def main():
    results = {}

    for dataset_key, config in DATASETS.items():
        try:
            dataset = process_dataset(dataset_key, config)
            if dataset:
                rows, csv_path = extract_gps_and_export(dataset, dataset_key, config)
                results[dataset_key] = {
                    'dataset': dataset,
                    'rows': rows,
                    'csv_path': csv_path,
                    'config': config
                }
        except Exception as e:
            print(f"Error processing {dataset_key}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for key, data in results.items():
        gps_count = sum(1 for r in data['rows'] if r['latitude'])
        print(f"{data['config']['name']}: {len(data['rows'])} images, {gps_count} with GPS")

if __name__ == "__main__":
    main()
