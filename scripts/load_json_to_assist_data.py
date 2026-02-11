"""
Load JSON files from data/archived into assist_data table.
This preserves the original JSON structure for simple querying.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.repository import PostgresRepository


def load_json_files():
    """Load all JSON files from data/archived directory."""
    json_dir = Path("data/archived")
    
    if not json_dir.exists():
        print(f"❌ Directory not found: {json_dir}")
        return []
    
    files = []
    for json_file in sorted(json_dir.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                files.append((json_file.stem, data))
                print(f"✅ Loaded {json_file.name}")
        except Exception as e:
            print(f"❌ Error loading {json_file.name}: {e}")
    
    return files


def parse_filename(filename):
    """
    Parse filename to extract campus and year.
    Examples: 
      - ucb_25-26.json -> (UCB, 2025-2026)
      - ucd_24-25.json -> (UCD, 2024-2025)
    """
    parts = filename.split('_')
    if len(parts) >= 2:
        campus = parts[0].upper()
        year_raw = parts[1]
        
        # Convert 25-26 to 2025-2026
        year_parts = year_raw.split('-')
        if len(year_parts) == 2:
            start_year = f"20{year_parts[0]}"
            end_year = f"20{year_parts[1]}"
            year = f"{start_year}-{end_year}"
        else:
            year = year_raw
        
        return campus, year
    return None, None


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)
    
    print("="*60)
    print("  Loading JSON files into assist_data table")
    print("="*60)
    
    # Load JSON files
    files = load_json_files()
    if not files:
        print("❌ No JSON files found")
        sys.exit(1)
    
    print(f"\n📦 Found {len(files)} JSON file(s)")
    
    # Connect to database
    print("\n🔗 Connecting to database...")
    repo = PostgresRepository(database_url)
    
    # Load data into assist_data table
    print("\n💾 Saving to assist_data table...\n")
    
    for filename, data in files:
        campus, year = parse_filename(filename)
        
        if not campus:
            print(f"⚠️  Skipping {filename} (couldn't parse filename)")
            continue
        
        # The JSON structure is: { "Berkeley": [...], "Davis": [...], etc }
        # We store the entire campus array as the JSON
        for campus_name, campus_data in data.items():
            # Extract year from first element if present
            if campus_data and isinstance(campus_data, list) and len(campus_data) > 0:
                first_elem = campus_data[0]
                if isinstance(first_elem, dict) and "Year" in first_elem:
                    year = first_elem["Year"]
            
            # Save to assist_data
            saved = repo.save_assist_data(
                source_college="DVC",
                target_college=campus,
                major=None,  # General education/all majors
                agreements_json={
                    "campus_name": campus_name,
                    "year": year,
                    "categories": campus_data
                }
            )
            
            print(f"  ✅ {campus} ({year}): {len(campus_data)} categories")
    
    print("\n" + "="*60)
    print("  ✅ Data loaded successfully!")
    print("="*60)
    
    # Show summary
    print("\n📊 Database Summary:")
    all_data = repo.get_assist_data()
    for record in all_data:
        print(f"  • {record.source_college} → {record.target_college} ({record.updated_at:%Y-%m-%d})")


if __name__ == "__main__":
    main()
