"""
SQLAlchemy ORM models for Transfer Assistant database.
Defines the schema for universities, courses, and equivalency mappings.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class University(Base):
    """UC campus entity."""
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    years = relationship("Year", back_populates="university", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<University(id={self.id}, name='{self.name}')>"


class Year(Base):
    """Academic year for a specific university."""
    __tablename__ = "years"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String(20), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("year", "university_id", name="uq_year_university"),
        Index("idx_year_university_id", "university_id"),
    )

    # Relationships
    university = relationship("University", back_populates="years")
    categories = relationship("Category", back_populates="year", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Year(id={self.id}, year='{self.year}', university_id={self.university_id})>"


class Category(Base):
    """Course category (e.g., Mathematics, Computer Science, Breadth)."""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    minimum_required = Column(String(50), nullable=True)  # "all", a number, or "None"
    year_id = Column(Integer, ForeignKey("years.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_category_year_id", "year_id"),
    )

    # Relationships
    year = relationship("Year", back_populates="categories")
    equivalencies = relationship("CourseEquivalency", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', year_id={self.year_id})>"


class UCCourse(Base):
    """UC course definition (source course)."""
    __tablename__ = "uc_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    units = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    equivalencies = relationship("CourseEquivalency", back_populates="uc_course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UCCourse(id={self.id}, code='{self.course_code}', title='{self.title}')>"


class DVCCourse(Base):
    """DVC course definition (equivalent course)."""
    __tablename__ = "dvc_courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    units = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    equivalencies = relationship("CourseEquivalency", back_populates="dvc_course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DVCCourse(id={self.id}, code='{self.course_code}', title='{self.title}')>"


class CourseEquivalency(Base):
    """Mapping between a UC course and one or more DVC courses within a category."""
    __tablename__ = "course_equivalencies"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True)
    uc_course_id = Column(Integer, ForeignKey("uc_courses.id", ondelete="CASCADE"), nullable=False, index=True)
    dvc_course_id = Column(Integer, ForeignKey("dvc_courses.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_equivalency_category_id", "category_id"),
        Index("idx_equivalency_uc_course_id", "uc_course_id"),
        Index("idx_equivalency_dvc_course_id", "dvc_course_id"),
    )

    # Relationships
    category = relationship("Category", back_populates="equivalencies")
    uc_course = relationship("UCCourse", back_populates="equivalencies")
    dvc_course = relationship("DVCCourse", back_populates="equivalencies")

    def __repr__(self):
        return f"<CourseEquivalency(id={self.id}, category_id={self.category_id}, uc_course_id={self.uc_course_id}, dvc_course_id={self.dvc_course_id})>"
