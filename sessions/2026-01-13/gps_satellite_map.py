#!/usr/bin/env python3
"""
Extract GPS from drone images and create satellite map overlay
"""

import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os

def get_exif_data(image_path):
    """Extract EXIF data from image"""
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
        print(f"Error reading {image_path}: {e}")
        return None

def get_gps_coords(exif_data):
    """Extract GPS coordinates from EXIF data"""
    if not exif_data or 'GPSInfo' not in exif_data:
        return None, None

    gps_info = exif_data['GPSInfo']
    gps_data = {}

    for key in gps_info.keys():
        tag = GPSTAGS.get(key, key)
        gps_data[tag] = gps_info[key]

    def convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    lat = lon = None

    if 'GPSLatitude' in gps_data and 'GPSLatitudeRef' in gps_data:
        lat = convert_to_degrees(gps_data['GPSLatitude'])
        if gps_data['GPSLatitudeRef'] == 'S':
            lat = -lat

    if 'GPSLongitude' in gps_data and 'GPSLongitudeRef' in gps_data:
        lon = convert_to_degrees(gps_data['GPSLongitude'])
        if gps_data['GPSLongitudeRef'] == 'W':
            lon = -lon

    return lat, lon

# Load existing data
data_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_data.csv"
df = pd.read_csv(data_path)

print(f"Processing {len(df)} images...")

# Extract GPS from each image
latitudes = []
longitudes = []

for idx, row in df.iterrows():
    filepath = row['filepath']
    exif = get_exif_data(filepath)
    lat, lon = get_gps_coords(exif)
    latitudes.append(lat)
    longitudes.append(lon)
    if idx % 20 == 0:
        print(f"  Processed {idx+1}/{len(df)}")

df['latitude'] = latitudes
df['longitude'] = longitudes

# Save updated CSV with GPS
output_path = "/home/malezainia1/dev/voxel51/fiftyone/sessions/2026-01-13/santa_ines_with_gps.csv"
df.to_csv(output_path, index=False)

# Print summary
valid_gps = df['latitude'].notna().sum()
print(f"\nGPS extraction complete:")
print(f"  Total images: {len(df)}")
print(f"  With valid GPS: {valid_gps}")
print(f"  Lat range: {df['latitude'].min():.6f} to {df['latitude'].max():.6f}")
print(f"  Lon range: {df['longitude'].min():.6f} to {df['longitude'].max():.6f}")
print(f"\nSaved to: {output_path}")
