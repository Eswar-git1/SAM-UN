import sqlite3
from datetime import datetime, timedelta

def analyze_database():
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Check database schema
    cursor.execute('PRAGMA table_info(sitreps)')
    columns = cursor.fetchall()
    print('Database schema:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    # Get total count
    cursor.execute('SELECT COUNT(*) FROM sitreps')
    total_count = cursor.fetchone()[0]
    print(f'\nTotal SITREPs: {total_count}')
    
    # Get count by source
    cursor.execute('SELECT source, COUNT(*) FROM sitreps GROUP BY source')
    print('\nBy source:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1]}')
    
    # Check if we have a date/timestamp column
    column_names = [col[1] for col in columns]
    date_column = None
    for col in ['date', 'timestamp', 'created_at', 'datetime']:
        if col in column_names:
            date_column = col
            break
    
    if date_column:
        # Get date range
        cursor.execute(f'SELECT MIN({date_column}), MAX({date_column}) FROM sitreps')
        dates = cursor.fetchone()
        print(f'\nDate range: {dates[0]} to {dates[1]}')
        
        # Check last 2 weeks coverage
        two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        cursor.execute(f'SELECT COUNT(*) FROM sitreps WHERE {date_column} >= ?', (two_weeks_ago,))
        recent_count = cursor.fetchone()[0]
        print(f'SITREPs in last 2 weeks: {recent_count}')
        
        # Get recent data by source
        cursor.execute(f'SELECT source, COUNT(*) FROM sitreps WHERE {date_column} >= ? GROUP BY source', (two_weeks_ago,))
        print('\nLast 2 weeks by source:')
        for row in cursor.fetchall():
            print(f'  {row[0]}: {row[1]}')
        
        # Sample some recent entries
        cursor.execute(f'SELECT id, {date_column}, source, title FROM sitreps ORDER BY {date_column} DESC LIMIT 5')
        print('\nMost recent entries:')
        for row in cursor.fetchall():
            print(f'  {row[0]}: {row[1]} [{row[2]}] {row[3][:50]}...')
    else:
        print('\nNo date column found in database')
        # Just show some sample entries
        cursor.execute('SELECT id, source, title FROM sitreps LIMIT 5')
        print('\nSample entries:')
        for row in cursor.fetchall():
            print(f'  {row[0]}: [{row[1]}] {row[2][:50]}...')
    
    conn.close()

if __name__ == '__main__':
    analyze_database()