#!/usr/bin/env python3
"""
Migrate JSON agreement files to PostgreSQL using SQLAlchemy ORM.
This handles timestamps automatically and ensures proper relationships.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from backend.database.models import (
    Base, University, Year, Category, UCCourse, DVCCourse, CourseEquivalency
)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env file")

def load_json_files(json_dir="agreements_25-26"):
    """Load all JSON files from the specified directory."""
    json_files = {}
    json_path = Path(json_dir)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Directory not found: {json_dir}")
    
    for json_file in sorted(json_path.glob("*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                json_files[json_file.stem] = data
                print(f"✓ Loaded {json_file.name}")
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing {json_file.name}: {e}")
    
    if not json_files:
        raise ValueError(f"No JSON files found in {json_dir}")
    
    return json_files

def migrate_data(session, json_files):
    """Migrate all data from JSON files to PostgreSQL."""
    
    # University name mapping
    uni_mapping = {
        "Berkeley": "UC Berkeley",
        "Davis": "UC Davis",
        "San Diego": "UC San Diego",
        "San_Diego": "UC San Diego",
    }
    
    for filename, data in json_files.items():
        print(f"\nProcessing {filename}...")
        
        for university_name_short, university_data in data.items():
            # Get full university name
            full_uni_name = uni_mapping.get(university_name_short, university_name_short)
            print(f"  University: {full_uni_name}")
            
            # Create or get university
            uni = session.query(University).filter_by(name=full_uni_name).first()
            if not uni:
                uni = University(name=full_uni_name)
                session.add(uni)
                session.flush()  # Get the ID
            
            # Extract year and categories from the list
            year_str = None
            categories_data = []
            
            for item in university_data:
                if isinstance(item, dict):
                    if "Year" in item:
                        year_str = item["Year"]
                    elif "Category" in item:
                        categories_data.append(item)
            
            if not year_str:
                print(f"    ⚠ Warning: No year information found")
                continue
            
            # Create or get year
            year = session.query(Year).filter_by(year=year_str, university_id=uni.id).first()
            if not year:
                year = Year(year=year_str, university_id=uni.id)
                session.add(year)
                session.flush()
            
            print(f"    Year: {year_str}")
            
            # Process categories
            for category_data in categories_data:
                category_name = category_data.get("Category", "Unknown")
                min_required = category_data.get("Minimum_Required")
                
                # Create category
                category = Category(
                    name=category_name,
                    minimum_required=min_required,
                    year_id=year.id
                )
                session.add(category)
                session.flush()
                
                print(f"      Category: {category_name} (Required: {min_required})")
                
                # Process courses
                courses = category_data.get("Courses", [])
                for course_pair in courses:
                    # Handle different campus key names (UC_Berkeley, UC_Davis, UC_San_Diego, etc.)
                    uc_key = None
                    uc_data = None
                    for key in course_pair.keys():
                        if key.startswith("UC_") and key != "UC_Campus":
                            uc_key = key
                            uc_data = course_pair[key]
                            break
                    
                    if not uc_key:
                        # Fallback to UC_Campus if present
                        uc_data = course_pair.get("UC_Campus", {})
                    
                    dvc_data = course_pair.get("DVC", {})
                    
                    if uc_data and dvc_data:
                        # Get or create UC course
                        uc_code = uc_data.get("Course_Code", "")
                        uc_course = session.query(UCCourse).filter_by(course_code=uc_code).first()
                        if not uc_course:
                            # Parse units: convert to int if possible, otherwise use None
                            units_raw = uc_data.get("Units")
                            units = None
                            if isinstance(units_raw, int):
                                units = units_raw
                            elif isinstance(units_raw, str):
                                try:
                                    units = int(units_raw)
                                except (ValueError, TypeError):
                                    units = None  # Skip non-numeric units
                            
                            uc_course = UCCourse(
                                course_code=uc_code,
                                title=uc_data.get("Title", ""),
                                units=units
                            )
                            session.add(uc_course)
                            session.flush()
                        
                        # Handle DVC courses (can be single or list)
                        dvc_list = dvc_data if isinstance(dvc_data, list) else [dvc_data]
                        
                        for dvc_item in dvc_list:
                            dvc_code = dvc_item.get("Course_Code", "")
                            dvc_course = session.query(DVCCourse).filter_by(course_code=dvc_code).first()
                            if not dvc_course:
                                # Parse units: convert to int if possible, otherwise use None
                                units_raw = dvc_item.get("Units")
                                units = None
                                if isinstance(units_raw, int):
                                    units = units_raw
                                elif isinstance(units_raw, str):
                                    try:
                                        units = int(units_raw)
                                    except (ValueError, TypeError):
                                        units = None  # Skip non-numeric units like "sequence"
                                
                                dvc_course = DVCCourse(
                                    course_code=dvc_code,
                                    title=dvc_item.get("Title", ""),
                                    units=units
                                )
                                session.add(dvc_course)
                                session.flush()
                            
                            # Create equivalency
                            equiv = CourseEquivalency(
                                category_id=category.id,
                                uc_course_id=uc_course.id,
                                dvc_course_id=dvc_course.id
                            )
                            session.add(equiv)
            
            session.commit()
            print(f"  ✓ {full_uni_name} completed")

def main():
    """Main migration function."""
    print("=== JSON to PostgreSQL Migration ===\n")
    
    # Load JSON files
    print("Loading JSON files...")
    json_files = load_json_files()
    print(f"Found {len(json_files)} JSON file(s)\n")
    
    # Connect to database
    print(f"Connecting to: {DATABASE_URL}\n")
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Clear existing data (optional - comment out to preserve)
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)
    
    # Migrate data
    with Session(engine) as session:
        try:
            migrate_data(session, json_files)
            print("\n=== Migration Complete ===")
            
            # Print summary
            print("\n📊 Data Summary:")
            uni_count = session.query(University).count()
            year_count = session.query(Year).count()
            cat_count = session.query(Category).count()
            uc_count = session.query(UCCourse).count()
            dvc_count = session.query(DVCCourse).count()
            equiv_count = session.query(CourseEquivalency).count()
            
            print(f"  Universities: {uni_count}")
            print(f"  Years: {year_count}")
            print(f"  Categories: {cat_count}")
            print(f"  UC Courses: {uc_count}")
            print(f"  DVC Courses: {dvc_count}")
            print(f"  Equivalencies: {equiv_count}")
            
        except Exception as e:
            print(f"\n✗ Migration failed: {e}")
            session.rollback()
            raise

if __name__ == "__main__":
    main()
