"""
Sync agreements_25-26/*.json into PostgreSQL.
- Wipes existing tables (universities, years, categories, courses, equivalencies)
- Loads UC Berkeley / UC Davis / UC San Diego mappings from JSON
- Splits DVC course codes with separators (/, ,) into individual rows
Usage:
    python scripts/sync_json_to_postgres.py
Requires:
    - DATABASE_URL in .env
"""

import os
import sys
import json
import glob
import re
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Ensure repo root on sys.path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.database.models import Base, University, Year, Category, UCCourse, DVCCourse, CourseEquivalency

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise SystemExit("DATABASE_URL missing in .env")

ENGINE = create_engine(DB_URL, echo=False)

CAMPUS_NAME_MAP = {
    "Berkeley": "UC Berkeley",
    "Davis": "UC Davis",
    "San_Diego": "UC San Diego",
    "San Diego": "UC San Diego",
}

UC_KEYS = {"UC_Berkeley", "UC_Davis", "UC_SanDiego"}


def split_codes(raw: str) -> List[str]:
    if not raw:
        return []
    parts = re.split(r"[/,]", raw)
    out = []
    for p in parts:
        s = p.strip().replace("  ", " ")
        if s:
            out.append(s)
    return out


def parse_units(val):
    if val is None:
        return None
    try:
        f = float(val)
        return int(f) if f.is_integer() else f
    except Exception:
        return None


def get_uc_block(course_dict: Dict) -> Tuple[str, str, int]:
    for k, v in course_dict.items():
        if k in UC_KEYS and isinstance(v, dict):
            code = v.get("Course_Code", "").strip()
            title = v.get("Title", "").strip()
            units = parse_units(v.get("Units"))
            return code, title, units
    return "", "", None


def ensure_university(session: Session, name: str) -> University:
    uni = session.query(University).filter_by(name=name).first()
    if uni:
        return uni
    uni = University(name=name)
    session.add(uni)
    session.flush()
    return uni


def ensure_year(session: Session, uni_id: int, year_str: str) -> Year:
    year = session.query(Year).filter_by(university_id=uni_id, year=year_str).first()
    if year:
        return year
    year = Year(year=year_str, university_id=uni_id)
    session.add(year)
    session.flush()
    return year


def ensure_category(session: Session, year_id: int, name: str, minimum_required: str) -> Category:
    cat = session.query(Category).filter_by(year_id=year_id, name=name).first()
    if cat:
        cat.minimum_required = minimum_required
        return cat
    cat = Category(name=name, minimum_required=minimum_required, year_id=year_id)
    session.add(cat)
    session.flush()
    return cat


def ensure_uc_course(session: Session, code: str, title: str, units):
    code = code.strip()
    if not code:
        return None
    uc = session.query(UCCourse).filter_by(course_code=code).first()
    if uc:
        if title:
            uc.title = title
        if units is not None:
            uc.units = units
        return uc
    uc = UCCourse(course_code=code, title=title, units=units)
    session.add(uc)
    session.flush()
    return uc


def ensure_dvc_course(session: Session, code: str, title: str, units):
    code = code.strip()
    if not code:
        return None
    dvc = session.query(DVCCourse).filter_by(course_code=code).first()
    if dvc:
        if title:
            dvc.title = title
        if units is not None:
            dvc.units = units
        return dvc
    dvc = DVCCourse(course_code=code, title=title, units=units)
    session.add(dvc)
    session.flush()
    return dvc


def import_file(session: Session, path: str) -> Dict[str, int]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    inserted = {"universities": 0, "years": 0, "categories": 0, "uc_courses": 0, "dvc_courses": 0, "equivalencies": 0}

    for campus_key, sections in data.items():
        uni_name = CAMPUS_NAME_MAP.get(campus_key, campus_key.replace("_", " "))
        uni = ensure_university(session, uni_name)

        # year is in first element
        year_str = ""
        if sections and isinstance(sections[0], dict):
            year_str = sections[0].get("Year", "").strip()
        year_obj = ensure_year(session, uni.id, year_str or "Unknown")

        for block in sections[1:]:
            if not isinstance(block, dict):
                continue
            cat_name = block.get("Category", "").strip()
            min_req = str(block.get("Minimum_Required", "")).strip()
            if not cat_name:
                continue
            cat = ensure_category(session, year_obj.id, cat_name, min_req)

            courses = block.get("Courses", [])
            if not isinstance(courses, list):
                continue
            for course_entry in courses:
                if not isinstance(course_entry, dict):
                    continue
                uc_code, uc_title, uc_units = get_uc_block(course_entry)
                uc_course = ensure_uc_course(session, uc_code, uc_title, uc_units) if uc_code else None

                dvc_raw = course_entry.get("DVC")
                if dvc_raw is None:
                    continue
                if isinstance(dvc_raw, dict):
                    dvc_list = [dvc_raw]
                elif isinstance(dvc_raw, list):
                    dvc_list = dvc_raw
                else:
                    continue

                for dvc_item in dvc_list:
                    if not isinstance(dvc_item, dict):
                        continue
                    if "note" in dvc_item:
                        continue
                    codes = split_codes(dvc_item.get("Course_Code", ""))
                    title = dvc_item.get("Title", "").strip()
                    units = parse_units(dvc_item.get("Units"))
                    for code in codes:
                        dvc_course = ensure_dvc_course(session, code, title, units)
                        if not dvc_course:
                            continue
                        eq = CourseEquivalency(
                            category_id=cat.id,
                            uc_course_id=uc_course.id if uc_course else None,
                            dvc_course_id=dvc_course.id,
                        )
                        session.add(eq)
                        inserted["equivalencies"] += 1

    session.flush()
    return inserted


def reset_tables(session: Session):
    # Order matters due to FK constraints
    session.query(CourseEquivalency).delete()
    session.query(DVCCourse).delete()
    session.query(UCCourse).delete()
    session.query(Category).delete()
    session.query(Year).delete()
    session.query(University).delete()
    session.commit()


def main():
    paths = glob.glob(os.path.join("agreements_25-26", "*.json"))
    if not paths:
        raise SystemExit("No JSON files found under agreements_25-26/")

    with Session(ENGINE) as session:
        print("Resetting tables...")
        reset_tables(session)

        totals = {"universities": 0, "years": 0, "categories": 0, "uc_courses": 0, "dvc_courses": 0, "equivalencies": 0}
        for p in paths:
            stats = import_file(session, p)
            for k, v in stats.items():
                totals[k] += v
            session.commit()
            print(f"Imported {os.path.basename(p)}")

        print("\nImport complete.")
        print(f"  Equivalencies: {totals['equivalencies']}")

if __name__ == "__main__":
    main()
