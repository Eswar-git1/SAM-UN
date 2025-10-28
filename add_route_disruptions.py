#!/usr/bin/env python3
"""
Script to add three new route disruption entries for October 15th and 16th, 2025
for the activity marking layer in the UN SITREP dashboard.
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "sitreps.db")

def add_route_disruptions():
    """Add three new route disruption entries for October 15th and 16th, 2025"""
    
    # Route disruption entries for October 15th and 16th
    disruptions = [
        {
            "source": "local",
            "source_category": "local",
            "title": "Road blockade on Route RN7 near Bukavu",
            "description": "Who: Local Police Liaison; Contact: Police Ops +243-xxx-1234\nWhat: Armed group roadblock; Effect: complete route closure, all traffic stopped\nWhere: Route RN7 near Bukavu checkpoint (lat 18.45, lon 1.25)\nWhen: Reported 08:15, Valid next 24 hours, Last update 09:00\nSeverity: Critical\nStatus: ongoing\nConfidence: high (multiple sources confirmed)\nRecommended action: avoid area, use alternate Route RN8",
            "severity": "critical",
            "status": "ongoing",
            "unit": "Local Police Liaison",
            "contact": "Police Ops, +243-xxx-1234",
            "incident_type": "route_disruption",
            "lat": 18.45,
            "lon": 1.25,
            "created_at": "2025-10-15 08:15:00"
        },
        {
            "source": "own",
            "source_category": "own",
            "title": "Bridge damage on Route RN12 - Engineering Assessment",
            "description": "Who: BN5 Engineering Unit; Contact: Eng Ops Desk +243-xxx-5678\nWhat: structural damage to bridge; Effect: weight restrictions, no heavy vehicles\nWhere: Route RN12 bridge crossing (lat 20.15, lon 0.85)\nWhen: Reported 14:30, Valid next 48 hours, Last update 15:00\nSeverity: Medium\nStatus: confirmed\nConfidence: high (engineering assessment complete)\nRecommended action: light vehicles only, max 5 tons",
            "severity": "medium",
            "status": "confirmed",
            "unit": "BN5 Engineering Unit",
            "contact": "Eng Ops Desk, +243-xxx-5678",
            "incident_type": "route_disruption",
            "lat": 20.15,
            "lon": 0.85,
            "created_at": "2025-10-15 14:30:00"
        },
        {
            "source": "ngo",
            "source_category": "ngo",
            "title": "Flooding on Route RN3 - Humanitarian Convoy Delayed",
            "description": "Who: Red Cross Field Office; Contact: RC Ops +243-xxx-9999\nWhat: seasonal flooding; Effect: road impassable, convoy rerouted\nWhere: Route RN3 low-lying section (lat 22.80, lon 1.95)\nWhen: Reported 06:45, Valid next 72 hours, Last update 07:30\nSeverity: Medium\nStatus: open\nConfidence: medium (weather dependent)\nRecommended action: monitor water levels, use Route RN4 alternative",
            "severity": "medium",
            "status": "open",
            "unit": "Red Cross Field Office",
            "contact": "RC Ops, +243-xxx-9999",
            "incident_type": "route_disruption",
            "lat": 22.80,
            "lon": 1.95,
            "created_at": "2025-10-16 06:45:00"
        }
    ]
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        print(f"Adding {len(disruptions)} route disruption entries...")
        
        for i, disruption in enumerate(disruptions, 1):
            cur.execute("""
                INSERT INTO sitreps (
                    source, source_category, title, description, severity, 
                    status, unit, contact, incident_type, lat, lon, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                disruption["source"],
                disruption["source_category"],
                disruption["title"],
                disruption["description"],
                disruption["severity"],
                disruption["status"],
                disruption["unit"],
                disruption["contact"],
                disruption["incident_type"],
                disruption["lat"],
                disruption["lon"],
                disruption["created_at"]
            ))
            
            print(f"  {i}. Added: {disruption['title']}")
            print(f"     Date: {disruption['created_at']}")
            print(f"     Location: ({disruption['lat']}, {disruption['lon']})")
            print(f"     Severity: {disruption['severity']}")
            print()
        
        conn.commit()
        print(f"✅ Successfully added {len(disruptions)} route disruption entries!")
        
        # Verify the additions
        cur.execute("""
            SELECT COUNT(*) FROM sitreps 
            WHERE incident_type = 'route_disruption' 
            AND created_at >= '2025-10-15'
        """)
        recent_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM sitreps WHERE incident_type = 'route_disruption'")
        total_count = cur.fetchone()[0]
        
        print(f"📊 Route disruption summary:")
        print(f"   - Total route disruptions: {total_count}")
        print(f"   - Added for Oct 15-16: {recent_count}")
        
    except Exception as e:
        print(f"❌ Error adding route disruptions: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🚧 Adding Route Disruption Entries for October 15-16, 2025")
    print("=" * 60)
    
    if add_route_disruptions():
        print("\n✅ Route disruption entries added successfully!")
        print("The new entries should now appear in the dashboard's route disruption layer.")
    else:
        print("\n❌ Failed to add route disruption entries.")