import sqlite3

def analyze_current_sources():
    """Analyze current source naming inconsistencies"""
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Get all unique sources with counts
    cursor.execute('SELECT source, COUNT(*) FROM sitreps GROUP BY source ORDER BY source')
    sources = cursor.fetchall()
    
    print('Current unique sources:')
    for i, (source, count) in enumerate(sources, 1):
        print(f'{i:2d}. {source:<25} ({count} entries)')
    
    conn.close()
    return sources

def create_source_mapping():
    """Create mapping from current sources to standardized 5 categories"""
    
    # Define the 5 standard categories as shown in the image
    STANDARD_SOURCES = {
        'Own': 'Own',
        'Local': 'Local', 
        'Rebel': 'Rebel',
        'NGO': 'NGO',
        'Other': 'Other'
    }
    
    # Mapping from current inconsistent names to standard categories
    source_mapping = {
        # Own Forces variations
        'HQ / Own Forces': 'Own',
        'own': 'Own',
        
        # Local Government variations
        'Local Govt': 'Local',
        'LOCAL GOVT': 'Local',
        'local govt': 'Local',
        'Local Officials': 'Local',
        'Local Police': 'Local',
        'Community Leaders': 'Local',
        'local': 'Local',
        
        # Rebel Group variations
        'Rebel Group': 'Rebel',
        
        # NGO variations
        'NGO': 'NGO',
        'ngo': 'NGO',
        'NGO Partner': 'NGO',
        'International NGO': 'NGO',
        'UN Agencies': 'NGO',
        
        # Other Source variations
        'Other Source': 'Other',
        'Media Reports': 'Other',
        'Civilian Reports': 'Other',
        'Anonymous Tips': 'Other',
        'Diplomatic Sources': 'Other'
    }
    
    return source_mapping

def standardize_sources():
    """Update database to use standardized source names"""
    
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Get the mapping
    source_mapping = create_source_mapping()
    
    print('\nApplying source standardization...')
    
    # Update each source according to the mapping
    for old_source, new_source in source_mapping.items():
        cursor.execute('UPDATE sitreps SET source = ? WHERE source = ?', (new_source, old_source))
        affected_rows = cursor.rowcount
        if affected_rows > 0:
            print(f'Updated {affected_rows} entries: "{old_source}" -> "{new_source}"')
    
    conn.commit()
    
    # Verify the results
    cursor.execute('SELECT source, COUNT(*) FROM sitreps GROUP BY source ORDER BY source')
    final_sources = cursor.fetchall()
    
    print('\nFinal standardized sources:')
    total_entries = 0
    for source, count in final_sources:
        print(f'  {source:<10} : {count} entries')
        total_entries += count
    
    print(f'\nTotal entries: {total_entries}')
    
    conn.close()
    
    return final_sources

def main():
    print('=== Source Standardization Analysis ===')
    
    # Analyze current sources
    current_sources = analyze_current_sources()
    
    # Show mapping that will be applied
    mapping = create_source_mapping()
    print('\nMapping to be applied:')
    for old, new in mapping.items():
        print(f'  "{old}" -> "{new}"')
    
    # Apply standardization
    print('\n=== Applying Standardization ===')
    final_sources = standardize_sources()
    
    # Verify we have exactly 5 categories
    if len(final_sources) == 5:
        print('\n✅ SUCCESS: Database now has exactly 5 standardized source categories!')
    else:
        print(f'\n⚠️  WARNING: Expected 5 categories, but found {len(final_sources)}')
        print('Additional manual review may be needed.')

if __name__ == '__main__':
    main()