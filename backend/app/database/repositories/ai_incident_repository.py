"""
Repository for AI Incident database operations.
"""

from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.ai_incident import AIIncident


class AIIncidentRepository:
    """Repository for AI Incident CRUD operations."""

    model = AIIncident

    @classmethod
    def create(cls, db: Session, **kwargs) -> AIIncident:
        """Create a new AI Incident."""
        incident = AIIncident(**kwargs)
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @classmethod
    def get_by_id(cls, db: Session, incident_id: str) -> Optional[AIIncident]:
        """Get an AI Incident by ID."""
        return db.query(AIIncident).filter(AIIncident.id == incident_id).first()

    @classmethod
    def get_by_reference(cls, db: Session, incident_reference: str) -> Optional[AIIncident]:
        """Get an AI Incident by its unique reference."""
        return db.query(AIIncident).filter(AIIncident.incident_reference == incident_reference).first()

    @classmethod
    def list_all(
        cls,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        harm_type: Optional[str] = None,
        company: Optional[str] = None,
        business_type_id: Optional[str] = None,
    ) -> List[AIIncident]:
        """List AI Incidents with optional filters."""
        query = db.query(AIIncident)

        if severity:
            query = query.filter(AIIncident.severity == severity)
        if harm_type:
            query = query.filter(AIIncident.harm_type == harm_type)
        if company:
            query = query.filter(AIIncident.company.ilike(f"%{company}%"))
        if business_type_id:
            query = query.filter(AIIncident.business_type_id == business_type_id)

        return query.order_by(AIIncident.date_occurred.desc().nullslast()).offset(skip).limit(limit).all()

    @classmethod
    def update(cls, db: Session, incident_id: str, **kwargs) -> Optional[AIIncident]:
        """Update an AI Incident."""
        incident = cls.get_by_id(db, incident_id)
        if not incident:
            return None

        for key, value in kwargs.items():
            if value is not None:
                setattr(incident, key, value)

        db.commit()
        db.refresh(incident)
        return incident

    @classmethod
    def delete(cls, db: Session, incident_id: str) -> bool:
        """Delete an AI Incident."""
        incident = cls.get_by_id(db, incident_id)
        if not incident:
            return False

        db.delete(incident)
        db.commit()
        return True

    @classmethod
    def count_by_severity(cls, db: Session, business_type_id: Optional[str] = None) -> dict:
        """Count incidents by severity level."""
        query = db.query(AIIncident.severity, func.count(AIIncident.id))

        if business_type_id:
            query = query.filter(AIIncident.business_type_id == business_type_id)

        results = query.group_by(AIIncident.severity).all()
        return {severity: count for severity, count in results}

    @classmethod
    def count_by_harm_type(cls, db: Session, business_type_id: Optional[str] = None) -> dict:
        """Count incidents by harm type."""
        query = db.query(AIIncident.harm_type, func.count(AIIncident.id))

        if business_type_id:
            query = query.filter(AIIncident.business_type_id == business_type_id)

        results = query.group_by(AIIncident.harm_type).all()
        return {harm_type: count for harm_type, count in results}

