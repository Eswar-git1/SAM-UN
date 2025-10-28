#!/usr/bin/env python3
import sqlite3

def check_all_tables():
    conn = sqlite3.connect('sitreps.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} user tables:")
    for name, sql in tables:
        print(f"\nTable: {name}")
        print(f"SQL: {sql}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        count = cursor.fetchone()[0]
        print(f"Rows: {count}")
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({name})")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else ''} {'PK' if col[5] else ''}")
    
    conn.close()

if __name__ == '__main__':
    check_all_tables()