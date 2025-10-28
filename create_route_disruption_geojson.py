#!/usr/bin/env python3
"""
Script to create a route_disruptions.geojson file from SITREP data
This will make route disruptions a proper GeoJSON layer instead of a virtual layer
"""

import sqlite3
import json
import os

def create_route_disruption_geojson():
    """Create a GeoJSON file containing all route disruption entries from the SITREP database"""
    
    # Database path
    db_path = "sitreps.db"
    
    # Output path
    output_dir = r"C:\Users\Sarvam AI\Desktop\sam un\SAM UN\Assignment\GeoJSON Output"
    output_path = os.path.join(output_dir, "route_disruptions.geojson")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query for all route disruption entries
    query = """
    SELECT id, source, title, description, severity, lat, lon, created_at, status
    FROM sitreps 
    WHERE incident_type = 'route_disruption'
    ORDER BY created_at DESC
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Create GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Convert each row to a GeoJSON feature
    for row in rows:
        id_val, source, title, description, severity, lat, lon, created_at, status = row
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "id": id_val,
                "source": source,
                "title": title,
                "description": description,
                "severity": severity,
                "created_at": created_at,
                "status": status,
                "incident_type": "route_disruption",
                "marker-color": "#ff0000" if severity == "critical" else "#ff8800" if severity == "medium" else "#ffff00",
                "marker-size": "large" if severity == "critical" else "medium",
                "marker-symbol": "roadblock"
            }
        }
        
        geojson["features"].append(feature)
    
    # Write to file
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    conn.close()
    
    print(f"Created route_disruptions.geojson with {len(geojson['features'])} features")
    print(f"File saved to: {output_path}")
    
    return len(geojson['features'])

if __name__ == "__main__":
    count = create_route_disruption_geojson()
    print(f"Successfully created route disruption GeoJSON layer with {count} entries")