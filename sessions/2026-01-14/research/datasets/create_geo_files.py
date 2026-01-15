#!/usr/bin/env python3
"""
Create KML, KMZ, and Shapefile (UTM 19S) for drone photo locations.
"""

import os
import csv
import zipfile
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import simplekml
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

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
        print(f"Error reading {image_path}: {e}")
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

def extract_gps_from_images(csv_path, output_csv_path):
    """Extract GPS from images and update CSV."""
    print(f"Reading {csv_path}...")

    rows = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        # Add lat/lon columns if not present
        if 'latitude' not in fieldnames:
            fieldnames = list(fieldnames) + ['latitude', 'longitude']

        for row in reader:
            # Check if already has GPS
            if 'latitude' in row and row['latitude']:
                rows.append(row)
                continue

            # Extract GPS from image
            filepath = row['filepath']
            exif = get_exif_data(filepath)
            gps_info = get_gps_info(exif)
            lat, lon = get_coordinates(gps_info)

            row['latitude'] = lat if lat else ''
            row['longitude'] = lon if lon else ''
            rows.append(row)

            if lat:
                print(f"  {row['filename']}: {lat:.6f}, {lon:.6f}")

    # Write updated CSV
    with open(output_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Updated CSV saved to {output_csv_path}")
    return rows

def create_kml(data, output_path, site_name):
    """Create KML file with photo locations."""
    kml = simplekml.Kml(name=f"{site_name} Drone Photos")

    # Create folders for each category
    categories = {}

    for row in data:
        lat = row.get('latitude')
        lon = row.get('longitude')

        if not lat or not lon or lat == '' or lon == '':
            continue

        lat = float(lat)
        lon = float(lon)

        # Get category from tags
        tags = row.get('tags', '')
        if 'close-up' in tags or 'crop-inspection' in tags:
            category = 'Close-up/Inspection'
        elif 'very-close-up' in tags or 'plant-level' in tags:
            category = 'Very Close-up/Plant-level'
        elif 'overview' in tags or 'high-altitude' in tags:
            category = 'Overview/High-altitude'
        elif 'medium-altitude' in tags or 'row-visible' in tags:
            category = 'Medium-altitude/Row-visible'
        else:
            category = 'Other'

        # Create folder if not exists
        if category not in categories:
            categories[category] = kml.newfolder(name=category)

        # Add placemark
        pnt = categories[category].newpoint(
            name=row['filename'],
            coords=[(lon, lat)]
        )

        # Set style based on category
        if 'Close-up' in category or 'Very Close-up' in category:
            pnt.style.iconstyle.color = simplekml.Color.green
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
        else:
            pnt.style.iconstyle.color = simplekml.Color.red
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'

        # Add description
        pnt.description = f"""
        <![CDATA[
        <b>File:</b> {row['filename']}<br>
        <b>Category:</b> {category}<br>
        <b>Coordinates:</b> {lat:.6f}, {lon:.6f}<br>
        <b>UMAP X:</b> {row.get('umap_x', 'N/A')}<br>
        <b>UMAP Y:</b> {row.get('umap_y', 'N/A')}<br>
        ]]>
        """

    kml.save(output_path)
    print(f"KML saved to {output_path}")
    return output_path

def create_kmz(kml_path, kmz_path):
    """Create KMZ (compressed KML) file."""
    with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml_path, os.path.basename(kml_path).replace('.kml', '.kml'))
    print(f"KMZ saved to {kmz_path}")
    return kmz_path

def create_shapefile(data, output_path, site_name):
    """Create shapefile in UTM 19S (EPSG:32719)."""
    # Prepare data
    records = []
    for row in data:
        lat = row.get('latitude')
        lon = row.get('longitude')

        if not lat or not lon or lat == '' or lon == '':
            continue

        lat = float(lat)
        lon = float(lon)

        # Get category
        tags = row.get('tags', '')
        if 'close-up' in tags or 'crop-inspection' in tags:
            category = 'Close-up'
        elif 'very-close-up' in tags or 'plant-level' in tags:
            category = 'Very Close-up'
        elif 'overview' in tags or 'high-altitude' in tags:
            category = 'High-altitude'
        elif 'medium-altitude' in tags or 'row-visible' in tags:
            category = 'Medium-alt'
        else:
            category = 'Other'

        records.append({
            'filename': row['filename'],
            'category': category,
            'tags': tags,
            'umap_x': float(row.get('umap_x', 0)),
            'umap_y': float(row.get('umap_y', 0)),
            'latitude': lat,
            'longitude': lon,
            'geometry': Point(lon, lat)
        })

    # Create GeoDataFrame in WGS84
    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")

    # Reproject to UTM 19S
    gdf_utm = gdf.to_crs("EPSG:32719")

    # Add UTM coordinates
    gdf_utm['utm_e'] = gdf_utm.geometry.x
    gdf_utm['utm_n'] = gdf_utm.geometry.y

    # Save shapefile
    gdf_utm.to_file(output_path)
    print(f"Shapefile (UTM 19S) saved to {output_path}")

    return output_path

def main():
    base_dir = Path(__file__).parent

    # Process Santa Ines
    print("\n" + "="*60)
    print("Processing Santa Ines")
    print("="*60)

    si_csv = base_dir / "santa_ines" / "data" / "santa_ines_data.csv"
    si_csv_updated = base_dir / "santa_ines" / "data" / "santa_ines_data_gps.csv"
    si_data = extract_gps_from_images(si_csv, si_csv_updated)

    si_kml = base_dir / "santa_ines" / "data" / "santa_ines_photos.kml"
    si_kmz = base_dir / "santa_ines" / "data" / "santa_ines_photos.kmz"
    si_shp = base_dir / "santa_ines" / "data" / "santa_ines_utm19s"

    create_kml(si_data, str(si_kml), "Santa Ines")
    create_kmz(str(si_kml), str(si_kmz))
    create_shapefile(si_data, str(si_shp), "Santa Ines")

    # Process La Capilla
    print("\n" + "="*60)
    print("Processing La Capilla")
    print("="*60)

    lc_csv = base_dir / "la_capilla" / "data" / "la_capilla_data.csv"

    # Read La Capilla data (already has GPS)
    with open(lc_csv, 'r') as f:
        reader = csv.DictReader(f)
        lc_data = list(reader)

    lc_kml = base_dir / "la_capilla" / "data" / "la_capilla_photos.kml"
    lc_kmz = base_dir / "la_capilla" / "data" / "la_capilla_photos.kmz"
    lc_shp = base_dir / "la_capilla" / "data" / "la_capilla_utm19s"

    create_kml(lc_data, str(lc_kml), "La Capilla")
    create_kmz(str(lc_kml), str(lc_kmz))
    create_shapefile(lc_data, str(lc_shp), "La Capilla")

    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)
    print("\nGenerated files:")
    print(f"  Santa Ines:")
    print(f"    - KML: {si_kml}")
    print(f"    - KMZ: {si_kmz}")
    print(f"    - Shapefile: {si_shp}/")
    print(f"  La Capilla:")
    print(f"    - KML: {lc_kml}")
    print(f"    - KMZ: {lc_kmz}")
    print(f"    - Shapefile: {lc_shp}/")

if __name__ == "__main__":
    main()
