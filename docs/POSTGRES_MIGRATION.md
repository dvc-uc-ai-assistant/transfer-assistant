## PostgreSQL Files Overview

Your Transfer Assistant project uses PostgreSQL to store course equivalency data. Here's a breakdown of all relevant files and their functions:

### **1. Core Database Setup & Configuration**

#### setup_postgresql.ps1
- **Purpose:** Windows PowerShell script to initialize PostgreSQL from scratch
- **Functions:**
  - Verifies PostgreSQL 17 is installed
  - Starts PostgreSQL service if stopped
  - Creates the `transfer_assistant_db` database
  - Creates `transfer_user` role with appropriate permissions
  - Sets up schema and grants privileges
- **When to run:** First-time setup only

#### init_db.py
- **Purpose:** Initialize PostgreSQL database tables using SQLAlchemy ORM
- **Functions:**
  - Reads `DATABASE_URL` from .env file
  - Creates all 6 tables based on models defined in models.py
  - No data migration—purely schema creation
- **When to run:** After PostgreSQL is running, before migrating data

### **2. Database Schema Models**

#### models.py
- **Purpose:** Defines SQLAlchemy ORM models (the database schema)
- **6 Tables:**
  1. **University** — UC campuses (Berkeley, Davis, San Diego)
  2. **Year** — Academic years per university (e.g., 2025-2026)
  3. **Category** — Course categories (CS, Math, Science, etc.) per year
  4. **UCCourse** — UC campus courses (source courses)
  5. **DVCCourse** — Diablo Valley College courses (equivalent courses)
  6. **CourseEquivalency** — Maps DVC courses → UC courses within a category
- **Key Features:**
  - Foreign key relationships with cascade delete
  - Unique constraints (e.g., can't have duplicate universities)
  - Indexes for fast queries
  - Timestamps on all records

### **3. Data Migration Scripts**

#### migrate_json_to_db.py
- **Purpose:** Migrates course data from JSON files (in `agreements_25-26/` directory) to PostgreSQL
- **Functions:**
  - Loads JSON files for each UC campus
  - Creates/updates University, Year, Category, and Course records
  - Establishes Course Equivalency mappings
  - Handles flexible JSON parsing (multiple naming conventions)
- **When to run:** When updating data annually or adding new campuses
- **Command:** `python migrate_json_to_db.py`

#### sync_json_to_postgres.py
- **Purpose:** Alternative migration script that also handles splitting course codes
- **Key Feature:** Can split DVC course codes separated by "/" or "," into individual rows
- **Example:** "MATH-192 / MATH-195" becomes two separate equivalency records
- **Command:** `python scripts/sync_json_to_postgres.py`

### **4. Data Access Layer**

#### repository.py
- **Purpose:** Query interface for the database (Data Access Object pattern)
- **Key Methods:**
  - **`get_courses()`** — Retrieves filtered course equivalencies by:
    - Campus (UCB, UCD, UCSD)
    - Category (CS, Math, etc.)
    - Required vs. optional courses
    - Subject focus (CS, math, science)
    - Completed courses (excludes them)
  - **`get_campuses()`** — Lists available UC campuses
  - **`get_categories()`** — Lists course categories for a specific campus
  - **Helper methods** — `_is_cs_course()`, `_is_math_course()`, `_is_science_course()`
- **Used by:** ai_agent.py to answer user queries about transfer requirements

### **5. Testing & Validation**

#### test_postgres_integration.py
- **Purpose:** Validates PostgreSQL integration by testing the AI agent
- **Tests:** Runs 3 sample queries through the system:
  - "What computer science courses do I need for UC Berkeley?"
  - "What math courses do I need for UC Davis?"
  - "What science courses do I need for UC San Diego?"
- **When to run:** After migration to verify everything works
- **Command:** `python test_postgres_integration.py`

### **6. Documentation**

#### POSTGRES_MIGRATION.md
- **Status:** Production-ready as of December 21, 2025
- **Metrics:** 3 universities, 45 course equivalencies, 100% data integrity
- **Contains:** Setup instructions, schema documentation, data management procedures

---

## Workflow Summary

1. **Initial Setup:** Run setup_postgresql.ps1 → init_db.py
2. **Load Data:** Run migrate_json_to_db.py (or sync_json_to_postgres.py)
3. **Verify:** Run test_postgres_integration.py
4. **Use:** Application queries via `PostgresRepository` in ai_agent.py

