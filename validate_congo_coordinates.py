#!/usr/bin/env python3
"""
Script to validate and fix coordinates in SITREP database to ensure they fall within Republic of Congo boundaries.
"""

import sqlite3
import json
import random
from shapely.geometry import Point, shape
from shapely.ops import unary_union

def load_congo_boundary():
    """Load the Republic of Congo boundary from GeoJSON file."""
    try:
        with open('Assignment/GeoJSON Output/Republic of congo bdy.geojson', 'r', encoding='utf-8') as f:
            congo_geojson = json.load(f)
        
        # Extract the geometry from the GeoJSON
        features = congo_geojson['features']
        geometries = []
        
        for feature in features:
            geom = shape(feature['geometry'])
            geometries.append(geom)
        
        # Union all geometries to create a single boundary
        congo_boundary = unary_union(geometries)
        
        # Get bounding box
        bounds = congo_boundary.bounds
        print(f"Congo boundary bounds: {bounds}")
        print(f"Longitude range: {bounds[0]:.6f} to {bounds[2]:.6f}")
        print(f"Latitude range: {bounds[1]:.6f} to {bounds[3]:.6f}")
        
        return congo_boundary, bounds
        
    except Exception as e:
        print(f"Error loading Congo boundary: {e}")
        return None, None

def is_point_in_congo(lat, lon, congo_boundary):
    """Check if a point is within Congo boundaries."""
    if congo_boundary is None:
        return False
    
    point = Point(lon, lat)  # Note: Point takes (x, y) which is (lon, lat)
    return congo_boundary.contains(point)

def generate_random_congo_point(congo_boundary, bounds):
    """Generate a random point within Congo boundaries."""
    if congo_boundary is None or bounds is None:
        # Fallback to approximate Congo coordinates
        lat = random.uniform(-5.0, 3.5)
        lon = random.uniform(11.0, 19.0)
        return lat, lon
    
    # Try to generate a point within the bounding box that's also within the boundary
    max_attempts = 100
    for _ in range(max_attempts):
        lat = random.uniform(bounds[1], bounds[3])
        lon = random.uniform(bounds[0], bounds[2])
        
        if is_point_in_congo(lat, lon, congo_boundary):
            return lat, lon
    
    # If we can't find a point within the boundary, use the centroid
    centroid = congo_boundary.centroid
    return centroid.y, centroid.x

def validate_and_fix_coordinates():
    """Main function to validate and fix coordinates in the database."""
    print("Loading Congo boundary...")
    congo_boundary, bounds = load_congo_boundary()
    
    if congo_boundary is None:
        print("Could not load Congo boundary. Using approximate bounds.")
        # Approximate bounds for Republic of Congo
        bounds = (11.0, -5.0, 19.0, 3.5)  # (min_lon, min_lat, max_lon, max_lat)
    
    # Connect to database
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Get all records
    cursor.execute('SELECT id, lat, lon, title, source FROM sitreps')
    records = cursor.fetchall()
    
    print(f"\nAnalyzing {len(records)} records...")
    
    invalid_records = []
    valid_records = []
    
    for record in records:
        record_id, lat, lon, title, source = record
        
        # Check if coordinates are within Congo
        if congo_boundary:
            is_valid = is_point_in_congo(lat, lon, congo_boundary)
        else:
            # Fallback check using bounding box
            is_valid = (bounds[0] <= lon <= bounds[2] and bounds[1] <= lat <= bounds[3])
        
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append(record)
    
    print(f"\nValidation Results:")
    print(f"Valid records (within Congo): {len(valid_records)}")
    print(f"Invalid records (outside Congo): {len(invalid_records)}")
    
    if invalid_records:
        print(f"\nInvalid records:")
        print("ID | Current Lat | Current Lon | Title | Source")
        print("-" * 70)
        for record in invalid_records:
            record_id, lat, lon, title, source = record
            title_short = title[:20] + "..." if len(title) > 20 else title
            print(f"{record_id} | {lat:.6f} | {lon:.6f} | {title_short} | {source}")
        
        # Ask user if they want to fix the coordinates
        response = input(f"\nDo you want to fix {len(invalid_records)} invalid coordinates? (y/n): ")
        
        if response.lower() == 'y':
            print("\nFixing invalid coordinates...")
            
            for record in invalid_records:
                record_id, old_lat, old_lon, title, source = record
                
                # Generate new valid coordinates
                new_lat, new_lon = generate_random_congo_point(congo_boundary, bounds)
                
                # Update the database
                cursor.execute(
                    'UPDATE sitreps SET lat = ?, lon = ? WHERE id = ?',
                    (new_lat, new_lon, record_id)
                )
                
                print(f"Updated record {record_id}: ({old_lat:.6f}, {old_lon:.6f}) -> ({new_lat:.6f}, {new_lon:.6f})")
            
            # Commit changes
            conn.commit()
            print(f"\nSuccessfully updated {len(invalid_records)} records!")
        else:
            print("No changes made to the database.")
    else:
        print("\nAll coordinates are already within Congo boundaries!")
    
    conn.close()

if __name__ == "__main__":
    try:
        validate_and_fix_coordinates()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()