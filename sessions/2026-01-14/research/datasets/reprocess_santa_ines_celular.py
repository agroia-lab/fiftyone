#!/usr/bin/env python3
"""
Re-process Santa Ines Celular with both JPG and HEIC files.
Total expected: 635 JPG + 690 HEIC = 1,325 images
"""

import fiftyone as fo
import fiftyone.brain as fob
from pathlib import Path
import glob
from PIL import Image
from pillow_heif import register_heif_opener
import pandas as pd

# Register HEIC support
register_heif_opener()

# Configuration
DATASET_NAME = "santa_ines_celular"
SOURCE_PATH = "/home/malezainia1/dev/INIA_DeepLearning_Ubuntu_mod_lleon/data/campo1_ene_2026/Santa Ines/Celular"
OUTPUT_DIR = Path("/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-14/research/datasets/santa_ines_celular/data")

def get_gps_from_image(filepath):
    """Extract GPS from both JPEG and HEIC files."""
    try:
        img = Image.open(filepath)
        exif = img.getexif()

        if not exif:
            return None, None

        # Try IFD-based GPS extraction (works for HEIC)
        gps_ifd = exif.get_ifd(34853)

        if gps_ifd and 2 in gps_ifd and 4 in gps_ifd:
            # Latitude
            lat_data = gps_ifd[2]
            lat_ref = gps_ifd.get(1, 'N')
            lat = float(lat_data[0]) + float(lat_data[1])/60 + float(lat_data[2])/3600
            if lat_ref == 'S':
                lat = -lat

            # Longitude
            lon_data = gps_ifd[4]
            lon_ref = gps_ifd.get(3, 'E')
            lon = float(lon_data[0]) + float(lon_data[1])/60 + float(lon_data[2])/3600
            if lon_ref == 'W':
                lon = -lon

            return lat, lon

        # Fallback: try standard EXIF GPS tags
        gps_info = exif.get(34853)
        if gps_info:
            # Standard EXIF extraction...
            pass

    except Exception as e:
        print(f"  GPS error for {Path(filepath).name}: {e}")

    return None, None

def main():
    print("="*60)
    print("Re-processing Santa Ines Celular (JPG + HEIC)")
    print("="*60)

    # Find all images
    jpg_files = glob.glob(f"{SOURCE_PATH}/*.jpg") + glob.glob(f"{SOURCE_PATH}/*.JPG")
    heic_files = glob.glob(f"{SOURCE_PATH}/*.HEIC") + glob.glob(f"{SOURCE_PATH}/*.heic")

    all_files = sorted(jpg_files + heic_files)

    print(f"\nFound images:")
    print(f"  JPG:  {len(jpg_files)}")
    print(f"  HEIC: {len(heic_files)}")
    print(f"  Total: {len(all_files)}")

    # Delete existing dataset if present
    if fo.dataset_exists(DATASET_NAME):
        print(f"\nDeleting existing dataset: {DATASET_NAME}")
        fo.delete_dataset(DATASET_NAME)

    # Create new dataset
    print(f"\nCreating dataset: {DATASET_NAME}")
    dataset = fo.Dataset(name=DATASET_NAME)

    # Add samples
    print("Adding samples...")
    samples = []
    for filepath in all_files:
        sample = fo.Sample(filepath=filepath)
        samples.append(sample)

    dataset.add_samples(samples)
    print(f"  Added {len(dataset)} samples")

    # Compute CLIP embeddings with UMAP
    print("\nComputing CLIP embeddings (this may take a few minutes)...")
    fob.compute_visualization(
        dataset,
        brain_key="clip_viz",
        model="clip-vit-base32-torch",
        method="umap"
    )
    print("  CLIP + UMAP complete")

    # Compute similarity index
    print("\nComputing similarity index...")
    fob.compute_similarity(
        dataset,
        brain_key="clip_similarity",
        embeddings="clip_viz"
    )
    print("  Similarity index complete")

    # Extract GPS and prepare data
    print("\nExtracting GPS coordinates...")
    gps_count = 0
    data_rows = []

    # Get visualization results
    viz_results = dataset.load_brain_results("clip_viz")
    points = viz_results.current_points

    for i, sample in enumerate(dataset):
        lat, lon = get_gps_from_image(sample.filepath)

        if lat is not None:
            sample["latitude"] = lat
            sample["longitude"] = lon
            gps_count += 1

        # Get file type
        ext = Path(sample.filepath).suffix.upper()
        file_type = "HEIC" if ext in [".HEIC"] else "JPEG"

        data_rows.append({
            "sample_id": sample.id,
            "filepath": sample.filepath,
            "filename": Path(sample.filepath).name,
            "umap_x": points[i][0] if points is not None else None,
            "umap_y": points[i][1] if points is not None else None,
            "latitude": lat,
            "longitude": lon,
            "file_type": file_type,
            "site": "Santa Ines",
            "camera_type": "ground"
        })

        sample.save()

    print(f"  GPS extracted: {gps_count}/{len(dataset)} ({gps_count/len(dataset)*100:.1f}%)")

    # Save to CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data_rows)
    csv_path = OUTPUT_DIR / "santa_ines_celular_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    # Summary by file type
    print("\n" + "="*60)
    print("Summary by File Type")
    print("="*60)
    type_counts = df['file_type'].value_counts()
    for ftype, count in type_counts.items():
        gps_pct = df[df['file_type']==ftype]['latitude'].notna().mean() * 100
        print(f"  {ftype}: {count} images, {gps_pct:.1f}% with GPS")

    # Make dataset persistent
    dataset.persistent = True

    print("\n" + "="*60)
    print("Complete!")
    print("="*60)
    print(f"Dataset: {DATASET_NAME}")
    print(f"Total images: {len(dataset)}")
    print(f"GPS coverage: {gps_count}/{len(dataset)} ({gps_count/len(dataset)*100:.1f}%)")

if __name__ == "__main__":
    main()
