"""QUALITY Models — FieldOps V4.0

Constitutional: Every model MUST include org_id unless in System Table Registry.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func

from app.core.database import Base


# TODO: Implement quality models in respective sprints
