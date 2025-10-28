#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to Supabase PostgreSQL
"""

import sqlite3
import psycopg2
import os
import json
from datetime import datetime
from config import get_config

def connect_sqlite(db_path):
    """Connect to SQLite database"""
    return sqlite3.connect(db_path)

def connect_postgresql(database_url):
    """Connect to PostgreSQL database"""
    return psycopg2.connect(database_url)

def create_postgresql_tables(pg_conn):
    """Create tables in PostgreSQL"""
    cursor = pg_conn.cursor()
    
    # Create sitreps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sitreps (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            location VARCHAR(255),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            priority VARCHAR(50) DEFAULT 'medium',
            status VARCHAR(50) DEFAULT 'active',
            tags TEXT,
            created_by VARCHAR(100),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create chatbot_conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_conversations (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            user_message TEXT,
            bot_response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context_data TEXT
        )
    """)
    
    pg_conn.commit()
    print("PostgreSQL tables created successfully")

def migrate_sitreps(sqlite_conn, pg_conn):
    """Migrate sitreps data from SQLite to PostgreSQL"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Get all sitreps from SQLite
    sqlite_cursor.execute("SELECT * FROM sitreps")
    sitreps = sqlite_cursor.fetchall()
    
    # Get column names
    sqlite_cursor.execute("PRAGMA table_info(sitreps)")
    columns = [column[1] for column in sqlite_cursor.fetchall()]
    
    print(f"Migrating {len(sitreps)} sitreps...")
    
    for sitrep in sitreps:
        # Map SQLite data to PostgreSQL
        data = dict(zip(columns, sitrep))
        
        # Insert into PostgreSQL (excluding id to use SERIAL)
        # Handle NULL values for required fields
        content = data.get('description', data.get('content'))
        if content is None:
            content = "No content provided"  # Default value for NULL content
            
        # Map SQLite column names to Supabase column names with default coordinates for Congo
        pg_cursor.execute("""
            INSERT INTO sitreps (title, content, location, latitude, longitude, 
                               timestamp, priority, status, source, source_category, incident_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('title', 'Untitled'),  # Default title if NULL
            content,
            data.get('location', ''),
            data.get('lat', data.get('latitude')) or -2.5 + sitrep[0] * 0.05,  # Default coordinates for Congo
            data.get('lon', data.get('longitude')) or 28.8 + sitrep[0] * 0.05,  # Default coordinates for Congo
            data.get('created_at', data.get('timestamp')),  # Try both column names
            data.get('severity', 'medium'),  # Map severity to priority
            data.get('status', 'active'),
            data.get('source', ''),
            data.get('source_category', ''),
            data.get('incident_type', '')
        ))
    
    pg_conn.commit()
    print(f"Successfully migrated {len(sitreps)} sitreps")

def migrate_chatbot_conversations(sqlite_conn, pg_conn):
    """Migrate chatbot conversations if they exist"""
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Check if chatbot_conversations table exists in SQLite
        sqlite_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='chatbot_conversations'
        """)
        
        if sqlite_cursor.fetchone():
            sqlite_cursor.execute("SELECT * FROM chatbot_conversations")
            conversations = sqlite_cursor.fetchall()
            
            # Get column names
            sqlite_cursor.execute("PRAGMA table_info(chatbot_conversations)")
            columns = [column[1] for column in sqlite_cursor.fetchall()]
            
            print(f"Migrating {len(conversations)} chatbot conversations...")
            
            for conversation in conversations:
                data = dict(zip(columns, conversation))
                
                pg_cursor.execute("""
                    INSERT INTO chatbot_conversations (session_id, user_message, 
                                                     bot_response, timestamp, context_data)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data.get('session_id'),
                    data.get('user_message'),
                    data.get('bot_response'),
                    data.get('timestamp'),
                    data.get('context_data')
                ))
            
            pg_conn.commit()
            print(f"Successfully migrated {len(conversations)} conversations")
        else:
            print("No chatbot_conversations table found in SQLite")
            
    except Exception as e:
        print(f"Error migrating chatbot conversations: {e}")

def main():
    """Main migration function"""
    print("Starting migration from SQLite to Supabase PostgreSQL...")
    
    # Load configuration
    config = get_config()
    
    # Database paths
    sqlite_path = os.path.join(os.path.dirname(__file__), "sitreps.db")
    postgresql_url = os.environ.get('SUPABASE_DATABASE_URL')
    
    if not postgresql_url or not postgresql_url.startswith('postgresql'):
        print("Error: SUPABASE_DATABASE_URL not configured or invalid")
        return
        
    print(f"Using PostgreSQL URL: {postgresql_url}")
    
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite database not found at {sqlite_path}")
        return
    
    try:
        # Connect to databases
        print("Connecting to databases...")
        sqlite_conn = connect_sqlite(sqlite_path)
        pg_conn = connect_postgresql(postgresql_url)
        
        # Create PostgreSQL tables
        create_postgresql_tables(pg_conn)
        
        # Migrate data
        migrate_sitreps(sqlite_conn, pg_conn)
        migrate_chatbot_conversations(sqlite_conn, pg_conn)
        
        # Close connections
        sqlite_conn.close()
        pg_conn.close()
        
        print("Migration completed successfully!")
        print("\nNext steps:")
        print("1. Verify data in your Supabase dashboard")
        print("2. Update your .env file with FLASK_ENV=production")
        print("3. Deploy to Railway with the new configuration")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return

if __name__ == "__main__":
    main()