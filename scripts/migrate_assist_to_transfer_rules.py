"""
One-time migration: assist_data (JSON in PostgreSQL) -> transfer_rules rows.

This script does NOT read local JSON files. It only reads existing database rows
from assist_data and writes normalized SQL rows into transfer_rules.
"""

import os
import sys
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.models import AssistData, TransferRule  # noqa: E402
from backend.database.repository import PostgresRepository  # noqa: E402


def _to_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


UC_INFO_KEYS_BY_CAMPUS = {
    "UCB": ["UC_Berkeley", "UC Berkeley"],
    "UCD": ["UC_Davis", "UC Davis"],
    "UCSD": [
        "UC_SanDiego",
        "UC_San_Diego",
        "UC San Diego",
        "UCSD",
    ],
}


def _extract_uc_info(course_item: Dict, target_college: str) -> Dict:
    """Extract UC-side articulation info using the target campus key first."""
    for key in UC_INFO_KEYS_BY_CAMPUS.get((target_college or "").upper(), []):
        uc_info = course_item.get(key)
        if isinstance(uc_info, dict):
            return uc_info

    # Fallback for legacy payload variants with unexpected key names.
    for key, value in course_item.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            continue
        if key.upper().startswith("UC"):
            return value

    return {}


def _iter_transfer_rows(repo: PostgresRepository, record: AssistData) -> List[Dict]:
    payload = record.agreements_json or {}
    categories = payload.get("categories", [])
    year = str(payload.get("year") or "").strip() or "2025-2026"

    rows: List[Dict] = []

    for item in categories:
        if not isinstance(item, dict):
            continue
        if "Year" in item:
            continue

        category_name = (item.get("Category") or "").strip()
        if not category_name:
            continue

        minimum_required_raw = item.get("Minimum_Required", 0)
        try:
            minimum_required = int(minimum_required_raw)
        except Exception:
            minimum_required = 0

        for course_item in item.get("Courses", []):
            if not isinstance(course_item, dict):
                continue

            uc_info = _extract_uc_info(course_item, record.target_college)
            dvc_info = course_item.get("DVC", {})
            dvc_list = dvc_info if isinstance(dvc_info, list) else [dvc_info]

            for dvc in dvc_list:
                if not isinstance(dvc, dict):
                    continue

                dvc_code = (dvc.get("Course_Code") or "").strip()
                if not dvc_code:
                    continue

                dvc_title = (dvc.get("Title") or "").strip()
                domain = repo._course_domain(dvc_code, dvc_title, None)

                rows.append(
                    {
                        "source_college": record.source_college,
                        "target_college": record.target_college,
                        "academic_year": year,
                        "major": record.major,
                        "category_name": category_name,
                        "minimum_required": minimum_required,
                        "is_required": minimum_required > 0,
                        "domain": domain,
                        "dvc_course_code": dvc_code,
                        "dvc_course_title": dvc_title,
                        "dvc_units": _to_decimal(dvc.get("Units")),
                        "uc_course_code": (uc_info.get("Course_Code") or "").strip() or None,
                        "uc_course_title": (uc_info.get("Title") or "").strip() or None,
                        "uc_units": _to_decimal(uc_info.get("Units")),
                    }
                )

    return rows


def migrate(repo: PostgresRepository, dry_run: bool = False) -> Tuple[int, int]:
    """Return (assist_records, inserted_rows)."""
    inserted_rows = 0

    with Session(repo.engine) as session:
        records = (
            session.query(AssistData)
            .order_by(AssistData.target_college.asc(), AssistData.updated_at.desc())
            .all()
        )

        if not records:
            return 0, 0

        latest_by_campus = {}
        for rec in records:
            key = (rec.source_college, rec.target_college, rec.major)
            if key not in latest_by_campus:
                latest_by_campus[key] = rec

        selected = list(latest_by_campus.values())

        now = datetime.utcnow()
        for rec in selected:
            rows = _iter_transfer_rows(repo, rec)

            if dry_run:
                inserted_rows += len(rows)
                continue

            session.query(TransferRule).filter_by(
                source_college=rec.source_college,
                target_college=rec.target_college,
                major=rec.major,
            ).delete()

            seen = set()
            for row in rows:
                dedupe = (
                    row["source_college"],
                    row["target_college"],
                    row["academic_year"],
                    row.get("major") or "",
                    row["category_name"],
                    row["dvc_course_code"],
                    row.get("uc_course_code") or "",
                )
                if dedupe in seen:
                    continue
                seen.add(dedupe)

                session.add(
                    TransferRule(
                        source_college=row["source_college"],
                        target_college=row["target_college"],
                        academic_year=row["academic_year"],
                        major=row.get("major"),
                        category_name=row["category_name"],
                        minimum_required=row["minimum_required"],
                        is_required=row["is_required"],
                        domain=row["domain"],
                        dvc_course_code=row["dvc_course_code"],
                        dvc_course_title=row["dvc_course_title"],
                        dvc_units=row["dvc_units"],
                        uc_course_code=row["uc_course_code"],
                        uc_course_title=row["uc_course_title"],
                        uc_units=row["uc_units"],
                        created_at=now,
                        updated_at=now,
                    )
                )

            inserted_rows += len(seen)

        if not dry_run:
            session.commit()

    return len(selected), inserted_rows


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate assist_data JSON rows into transfer_rules")
    parser.add_argument("--dry-run", action="store_true", help="Show row counts without writing")
    args = parser.parse_args()

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        sys.exit(1)

    repo = PostgresRepository(database_url)

    assist_count, row_count = migrate(repo, dry_run=args.dry_run)

    mode = "DRY RUN" if args.dry_run else "MIGRATION COMPLETE"
    print("=" * 60)
    print(f"{mode}")
    print("=" * 60)
    print(f"AssistData records processed: {assist_count}")
    print(f"TransferRule rows generated:  {row_count}")


if __name__ == "__main__":
    main()
