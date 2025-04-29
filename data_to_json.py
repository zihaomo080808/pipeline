#!/usr/bin/env python3
import json
import sqlite3
import os

def fetch_opportunities():
    """Fetch all opportunities from SQLite database"""
    # Connect to the database
    conn = sqlite3.connect('oppradar.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    
    # Query all opportunities
    cursor.execute("""
        SELECT 
            id, title, description, what, 
            when_at, where_city, who, 
            skills, topic_tags, source_url 
        FROM opportunities
        ORDER BY when_at DESC
    """)
    
    # Fetch all rows
    rows = cursor.fetchall()
    
    # Format the data for JSON
    opportunities = []
    for row in rows:
        # Parse JSON strings for skills and topics
        skills = json.loads(row['skills']) if row['skills'] else []
        topics = json.loads(row['topic_tags']) if row['topic_tags'] else []
        
        opportunities.append({
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'what': row['what'],
            'when_at': row['when_at'],
            'where_city': row['where_city'],
            'who': row['who'],
            'skills': skills,
            'topic_tags': topics,
            'source_url': row['source_url']
        })
    
    conn.close()
    return opportunities

def write_to_json():
    """Write opportunities data to JSON file"""
    opportunities = fetch_opportunities()
    
    with open('data.json', 'w') as file:
        json.dump(opportunities, file, indent=2)
    
    print(f"Successfully wrote {len(opportunities)} opportunities to data.json")

if __name__ == "__main__":
    write_to_json()