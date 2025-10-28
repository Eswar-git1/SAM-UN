import sqlite3
import random
from datetime import datetime, timedelta
import json

# Standardized source categories for better demo
SOURCES = {
    'local': ['Local Govt', 'Local Police', 'Local Officials', 'Community Leaders'],
    'other': ['Other Source', 'Media Reports', 'Civilian Reports', 'Anonymous Tips'],
    'international': ['UN Agencies', 'NGO Partner', 'International NGO', 'Diplomatic Sources']
}

# Realistic incident types for UN peacekeeping context
INCIDENT_TYPES = [
    'Security Incident', 'Medical Emergency', 'Logistics Issue', 'Patrol Report',
    'Intelligence Report', 'Civilian Protection', 'Infrastructure Damage', 'Supply Shortage',
    'Communication Issue', 'Vehicle Breakdown', 'Weather Impact', 'Border Incident',
    'Humanitarian Crisis', 'Displacement Report', 'Resource Conflict', 'Training Exercise'
]

# Severity levels
SEVERITIES = ['Low', 'Medium', 'High', 'Critical']

# Status options
STATUSES = ['Active', 'Resolved', 'Under Investigation', 'Pending', 'Closed']

# Units for UN context
UNITS = [
    'UNMOGIP HQ', 'Sector North', 'Sector South', 'Mobile Team Alpha', 'Mobile Team Beta',
    'Logistics Unit', 'Medical Unit', 'Communications Unit', 'Engineering Unit', 'Transport Unit'
]

# Sample titles and descriptions for different incident types
INCIDENT_TEMPLATES = {
    'Security Incident': {
        'titles': [
            'Armed group movement reported near checkpoint',
            'Suspicious activity observed in sector',
            'Unauthorized personnel at observation post',
            'Potential threat assessment required',
            'Security breach at compound perimeter'
        ],
        'descriptions': [
            'Local sources report movement of armed individuals near the designated checkpoint. Patrol dispatched for verification.',
            'Observation post reported suspicious activity requiring immediate assessment and potential response.',
            'Unauthorized personnel attempted to access restricted area. Security protocols activated.',
            'Intelligence indicates potential security threat in the operational area requiring enhanced vigilance.',
            'Perimeter security detected unauthorized access attempt. Investigation ongoing.'
        ]
    },
    'Medical Emergency': {
        'titles': [
            'Medical evacuation requested for civilian',
            'Emergency medical assistance required',
            'Health facility support needed',
            'Medical supply shortage reported',
            'Disease outbreak investigation'
        ],
        'descriptions': [
            'Local authorities request medical evacuation for critically injured civilian requiring specialized treatment.',
            'Emergency medical response team deployed to assist with urgent medical situation in the area.',
            'Local health facility requests support due to overwhelming patient load and resource constraints.',
            'Critical shortage of medical supplies reported at regional health center requiring immediate attention.',
            'Potential disease outbreak reported requiring epidemiological investigation and containment measures.'
        ]
    },
    'Logistics Issue': {
        'titles': [
            'Supply convoy delayed due to road conditions',
            'Equipment malfunction at observation post',
            'Fuel shortage affecting operations',
            'Communication equipment failure',
            'Vehicle maintenance required'
        ],
        'descriptions': [
            'Scheduled supply convoy experiencing delays due to adverse road conditions and weather impact.',
            'Critical equipment malfunction at observation post affecting operational capability and requiring immediate repair.',
            'Fuel shortage impacting patrol operations and requiring emergency resupply coordination.',
            'Communication equipment failure disrupting coordination between units and headquarters.',
            'Vehicle breakdown requiring maintenance support and potential replacement for continued operations.'
        ]
    },
    'Patrol Report': {
        'titles': [
            'Routine patrol completed without incident',
            'Border area patrol observations',
            'Community engagement during patrol',
            'Infrastructure assessment patrol',
            'Security situation assessment'
        ],
        'descriptions': [
            'Routine patrol completed successfully with no significant incidents or security concerns observed.',
            'Border patrol conducted with observations of normal civilian activity and no unusual movements.',
            'Patrol engaged with local community leaders to assess current situation and address concerns.',
            'Infrastructure assessment patrol identified areas requiring maintenance and potential security improvements.',
            'Security assessment patrol completed with detailed observations of current threat level and recommendations.'
        ]
    }
}

# Geographic coordinates for realistic locations (Kashmir region)
LOCATIONS = [
    (34.0837, 74.7973),  # Srinagar area
    (33.7782, 76.5762),  # Leh area
    (32.7266, 74.8570),  # Jammu area
    (34.1526, 74.8914),  # Baramulla area
    (33.5574, 75.1711),  # Kargil area
    (34.2996, 74.4663),  # Kupwara area
    (33.2778, 75.3412),  # Doda area
    (32.9384, 74.8745),  # Kathua area
]

def generate_realistic_sitrep(date_time, source_category):
    """Generate a realistic SITREP entry"""
    
    # Select source from category
    source = random.choice(SOURCES[source_category])
    
    # Select incident type and get template
    incident_type = random.choice(INCIDENT_TYPES)
    template = INCIDENT_TEMPLATES.get(incident_type, INCIDENT_TEMPLATES['Security Incident'])
    
    # Generate realistic data
    title = random.choice(template['titles'])
    description = random.choice(template['descriptions'])
    severity = random.choice(SEVERITIES)
    status = random.choice(STATUSES)
    unit = random.choice(UNITS)
    lat, lon = random.choice(LOCATIONS)
    
    # Add some variation to coordinates
    lat += random.uniform(-0.1, 0.1)
    lon += random.uniform(-0.1, 0.1)
    
    # Generate contact info
    contact = f"Contact-{random.randint(1000, 9999)}"
    
    return {
        'source': source,
        'title': title,
        'description': description,
        'severity': severity,
        'lat': lat,
        'lon': lon,
        'created_at': date_time.strftime('%Y-%m-%d %H:%M:%S'),
        'source_category': source_category,
        'status': status,
        'unit': unit,
        'contact': contact,
        'incident_type': incident_type
    }

def add_demo_data():
    """Add comprehensive demo data for the last 2 weeks"""
    
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute('SELECT COUNT(*) FROM sitreps')
    current_count = cursor.fetchone()[0]
    print(f'Current SITREP count: {current_count}')
    
    # Calculate how many we need to add
    target_count = 250  # Aim for 250 total for a robust demo
    needed_count = target_count - current_count
    print(f'Adding {needed_count} new SITREPs to reach {target_count} total')
    
    # Generate data for last 2 weeks with good distribution
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    new_sitreps = []
    
    # Distribute entries across the 2-week period
    for i in range(needed_count):
        # Random time within the 2-week period
        random_days = random.uniform(0, 14)
        entry_date = start_date + timedelta(days=random_days)
        
        # Ensure good distribution across source categories
        if i % 3 == 0:
            source_category = 'local'
        elif i % 3 == 1:
            source_category = 'other'
        else:
            source_category = 'international'
        
        sitrep = generate_realistic_sitrep(entry_date, source_category)
        new_sitreps.append(sitrep)
    
    # Insert new data
    insert_query = '''
    INSERT INTO sitreps (source, title, description, severity, lat, lon, created_at, 
                        source_category, status, unit, contact, incident_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    for sitrep in new_sitreps:
        cursor.execute(insert_query, (
            sitrep['source'], sitrep['title'], sitrep['description'], sitrep['severity'],
            sitrep['lat'], sitrep['lon'], sitrep['created_at'], sitrep['source_category'],
            sitrep['status'], sitrep['unit'], sitrep['contact'], sitrep['incident_type']
        ))
    
    conn.commit()
    
    # Verify the results
    cursor.execute('SELECT COUNT(*) FROM sitreps')
    final_count = cursor.fetchone()[0]
    print(f'Final SITREP count: {final_count}')
    
    # Check last 2 weeks distribution
    two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    cursor.execute('SELECT source_category, COUNT(*) FROM sitreps WHERE created_at >= ? GROUP BY source_category', (two_weeks_ago,))
    print('\nLast 2 weeks by source category:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    cursor.execute('SELECT COUNT(*) FROM sitreps WHERE created_at >= ?', (two_weeks_ago,))
    recent_total = cursor.fetchone()[0]
    print(f'\nTotal SITREPs in last 2 weeks: {recent_total}')
    
    conn.close()
    print('\nDemo data generation completed successfully!')

if __name__ == '__main__':
    add_demo_data()