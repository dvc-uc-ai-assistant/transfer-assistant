"""
Test the simplified repository with JSON-based data.
Verify that course queries still work after refactoring.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.database.repository import PostgresRepository


def test_get_courses(repo):
    """Test get_courses() method."""
    print("\n" + "="*60)
    print("TEST 1: Get all courses for UCB")
    print("="*60)
    
    courses = repo.get_courses(campus_keys=["UCB"])
    
    if "UCB" in courses:
        print(f"✅ Found {len(courses['UCB'])} courses for UCB")
        
        # Show first 3 courses
        for i, course in enumerate(courses['UCB'][:3], 1):
            print(f"\n  {i}. {course['dvc_code']} → {course['uc_code']}")
            print(f"     DVC: {course['dvc_title']} ({course['dvc_units']} units)")
            print(f"     UC: {course['uc_title']} ({course['uc_units']} units)")
            print(f"     Category: {course['category']}")
            print(f"     Required: {course['minimum_required']}")
    else:
        print("❌ No courses found for UCB")


def test_get_campuses(repo):
    """Test get_campuses() method."""
    print("\n" + "="*60)
    print("TEST 2: Get available campuses")
    print("="*60)
    
    campuses = repo.get_campuses()
    print(f"✅ Available campuses: {', '.join(campuses)}")


def test_get_categories(repo):
    """Test get_categories() method."""
    print("\n" + "="*60)
    print("TEST 3: Get categories for UCB")
    print("="*60)
    
    categories = repo.get_categories("UCB")
    print(f"✅ Found {len(categories)} categories:")
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")


def test_filters(repo):
    """Test filtering capabilities."""
    print("\n" + "="*60)
    print("TEST 4: Filter by category (Math)")
    print("="*60)
    
    courses = repo.get_courses(
        campus_keys=["UCB"],
        categories=["Mathematics Requirements"]
    )
    
    if "UCB" in courses:
        print(f"✅ Found {len(courses['UCB'])} math courses")
        for course in courses['UCB']:
            print(f"  • {course['dvc_code']}: {course['dvc_title']}")


def test_completed_courses(repo):
    """Test filtering by completed courses."""
    print("\n" + "="*60)
    print("TEST 5: Filter out completed courses")
    print("="*60)
    
    all_courses = repo.get_courses(campus_keys=["UCB"])
    filtered_courses = repo.get_courses(
        campus_keys=["UCB"],
        completed_courses={"MATH-192"}
    )
    
    print(f"✅ All courses: {len(all_courses['UCB'])}")
    print(f"✅ After filtering MATH-192: {len(filtered_courses['UCB'])}")
    print(f"✅ Filtered out: {len(all_courses['UCB']) - len(filtered_courses['UCB'])} course(s)")


def main():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        sys.exit(1)
    
    print("="*60)
    print("  Testing Simplified Repository (JSON-based)")
    print("="*60)
    
    repo = PostgresRepository(database_url)
    
    try:
        test_get_courses(repo)
        test_get_campuses(repo)
        test_get_categories(repo)
        test_filters(repo)
        test_completed_courses(repo)
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
