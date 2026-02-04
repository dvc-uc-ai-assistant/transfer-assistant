from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Universities
    print("=== UNIVERSITIES ===")
    result = conn.execute(text('SELECT * FROM universities;'))
    for row in result:
        print(row)
    
    print("\n=== YEARS ===")
    result = conn.execute(text('SELECT * FROM years;'))
    for row in result:
        print(row)
    
    print("\n=== CATEGORIES ===")
    result = conn.execute(text('SELECT * FROM categories;'))
    for row in result:
        print(row)
    
    print(f"\n=== UC COURSES ({conn.execute(text('SELECT COUNT(*) FROM uc_courses;')).scalar()} total) ===")
    result = conn.execute(text('SELECT id, course_code, title, units FROM uc_courses LIMIT 10;'))
    for row in result:
        print(row)
    print("... and more")
    
    print(f"\n=== DVC COURSES ({conn.execute(text('SELECT COUNT(*) FROM dvc_courses;')).scalar()} total) ===")
    result = conn.execute(text('SELECT id, course_code, title, units FROM dvc_courses LIMIT 10;'))
    for row in result:
        print(row)
    print("... and more")
    
    print(f"\n=== COURSE EQUIVALENCIES ({conn.execute(text('SELECT COUNT(*) FROM course_equivalencies;')).scalar()} total) ===")
    result = conn.execute(text('SELECT uc_course_id, dvc_course_id FROM course_equivalencies LIMIT 10;'))
    for row in result:
        print(row)
    print("... and more")
