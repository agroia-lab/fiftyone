#!/usr/bin/env python3
"""
Create KML, KMZ, and Shapefile (UTM 19S) for ground camera photo locations.
"""

import os
import csv
import zipfile
from pathlib import Path
import simplekml
import geopandas as gpd
from shapely.geometry import Point

BASE_DIR = Path(__file__).parent

DATASETS = {
    "santa_ines_celular": {
        "csv": BASE_DIR / "santa_ines_celular" / "data" / "santa_ines_celular_data.csv",
        "name": "Santa Ines (Ground Camera)",
        "color_primary": simplekml.Color.green,
        "color_secondary": simplekml.Color.lightgreen,
    },
    "la_capilla_celular": {
        "csv": BASE_DIR / "la_capilla_celular" / "data" / "la_capilla_celular_data.csv",
        "name": "La Capilla (Ground Camera)",
        "color_primary": simplekml.Color.blue,
        "color_secondary": simplekml.Color.lightblue,
    },
    "apalta": {
        "csv": BASE_DIR / "apalta" / "data" / "apalta_data.csv",
        "name": "Apalta (Ground Camera)",
        "color_primary": simplekml.Color.orange,
        "color_secondary": simplekml.Color.yellow,
    },
    "camarico": {
        "csv": BASE_DIR / "camarico" / "data" / "camarico_data.csv",
        "name": "Camarico (Ground Camera)",
        "color_primary": simplekml.Color.purple,
        "color_secondary": simplekml.Color.violet,
    }
}

def read_csv(csv_path):
    """Read CSV and return rows."""
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def create_kml(data, output_path, site_name, color):
    """Create KML file with photo locations."""
    kml = simplekml.Kml(name=f"{site_name}")

    valid_count = 0
    for row in data:
        lat = row.get('latitude')
        lon = row.get('longitude')

        if not lat or not lon or lat == '' or lon == '':
            continue

        lat = float(lat)
        lon = float(lon)
        valid_count += 1

        pnt = kml.newpoint(
            name=row['filename'],
            coords=[(lon, lat)]
        )

        pnt.style.iconstyle.color = color
        pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
        pnt.style.iconstyle.scale = 0.8

        pnt.description = f"""
        <![CDATA[
        <b>File:</b> {row['filename']}<br>
        <b>Site:</b> {row.get('site', site_name)}<br>
        <b>Camera:</b> Ground (Celular)<br>
        <b>Coordinates:</b> {lat:.6f}, {lon:.6f}<br>
        <b>UMAP X:</b> {row.get('umap_x', 'N/A')}<br>
        <b>UMAP Y:</b> {row.get('umap_y', 'N/A')}<br>
        ]]>
        """

    kml.save(output_path)
    print(f"KML saved: {output_path} ({valid_count} points)")
    return output_path

def create_kmz(kml_path, kmz_path):
    """Create KMZ (compressed KML) file."""
    with zipfile.ZipFile(kmz_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(kml_path, os.path.basename(kml_path))
    print(f"KMZ saved: {kmz_path}")
    return kmz_path

def create_shapefile(data, output_path, site_name):
    """Create shapefile in UTM 19S (EPSG:32719)."""
    records = []
    for row in data:
        lat = row.get('latitude')
        lon = row.get('longitude')

        if not lat or not lon or lat == '' or lon == '':
            continue

        lat = float(lat)
        lon = float(lon)

        records.append({
            'filename': row['filename'][:50],  # Truncate for shapefile
            'site': row.get('site', site_name)[:20],
            'camera': 'ground',
            'umap_x': float(row.get('umap_x', 0)),
            'umap_y': float(row.get('umap_y', 0)),
            'latitude': lat,
            'longitude': lon,
            'geometry': Point(lon, lat)
        })

    if not records:
        print(f"No GPS data for {site_name}, skipping shapefile")
        return None

    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    gdf_utm = gdf.to_crs("EPSG:32719")
    gdf_utm['utm_e'] = gdf_utm.geometry.x
    gdf_utm['utm_n'] = gdf_utm.geometry.y

    gdf_utm.to_file(output_path)
    print(f"Shapefile saved: {output_path} ({len(records)} points)")
    return output_path

def main():
    print("="*60)
    print("Creating geo files for ground camera datasets")
    print("="*60)

    for dataset_key, config in DATASETS.items():
        print(f"\n--- {config['name']} ---")

        csv_path = config['csv']
        if not csv_path.exists():
            print(f"CSV not found: {csv_path}")
            continue

        data = read_csv(csv_path)
        print(f"Read {len(data)} records")

        output_dir = csv_path.parent
        kml_path = output_dir / f"{dataset_key}_photos.kml"
        kmz_path = output_dir / f"{dataset_key}_photos.kmz"
        shp_path = output_dir / f"{dataset_key}_utm19s"

        create_kml(data, str(kml_path), config['name'], config['color_primary'])
        create_kmz(str(kml_path), str(kmz_path))
        create_shapefile(data, str(shp_path), config['name'])

    print("\n" + "="*60)
    print("COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
