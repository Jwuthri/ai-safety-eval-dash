"""
AI Incident repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.ai_incident import AIIncident
from ..models.enums import SeverityLevel
from .base_async import AsyncBaseRepository


class AIIncidentRepository(AsyncBaseRepository[AIIncident]):
    """Repository for AI incident operations."""

    def __init__(self):
        super().__init__(AIIncident)

    async def get_by_industry(
        self,
        session: AsyncSession,
        industry: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents filtered by industry."""
        return await self.list_with_filters(
            session,
            filters={"industry": industry},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_by_use_case(
        self,
        session: AsyncSession,
        use_case: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents filtered by use case."""
        return await self.list_with_filters(
            session,
            filters={"use_case": use_case},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_by_industry_and_use_case(
        self,
        session: AsyncSession,
        industry: str,
        use_case: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents filtered by both industry and use case."""
        return await self.list_with_filters(
            session,
            filters={"industry": industry, "use_case": use_case},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_featured_incidents(
        self,
        session: AsyncSession,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get featured incidents (like Air Canada example)."""
        return await self.list_with_filters(
            session,
            filters={"is_featured_example": True},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_by_severity(
        self,
        session: AsyncSession,
        severity: SeverityLevel,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents by severity level."""
        return await self.list_with_filters(
            session,
            filters={"severity": severity},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_by_harm_type(
        self,
        session: AsyncSession,
        harm_type: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents by harm type."""
        return await self.list_with_filters(
            session,
            filters={"harm_type": harm_type},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def get_by_attack_tactic(
        self,
        session: AsyncSession,
        attack_tactic: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents by attack tactic."""
        return await self.list_with_filters(
            session,
            filters={"attack_tactic": attack_tactic},
            order_by="created_at",
            desc=True,
            limit=limit
        )

    async def search_incidents(
        self,
        session: AsyncSession,
        industry: Optional[str] = None,
        use_case: Optional[str] = None,
        harm_type: Optional[str] = None,
        attack_tactic: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        modality: Optional[str] = None,
        verified_only: bool = False,
        featured_only: bool = False,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """
        Search incidents with multiple filter criteria.
        
        Args:
            session: Database session
            industry: Filter by industry
            use_case: Filter by use case
            harm_type: Filter by harm type
            attack_tactic: Filter by attack tactic
            severity: Filter by severity level
            modality: Filter by modality
            verified_only: Only return verified incidents
            featured_only: Only return featured incidents
            limit: Maximum number of results
            
        Returns:
            List of matching incidents
        """
        try:
            query = select(AIIncident)
            
            # Build filter conditions
            conditions = []
            
            if industry:
                conditions.append(AIIncident.industry == industry)
            if use_case:
                conditions.append(AIIncident.use_case == use_case)
            if harm_type:
                conditions.append(AIIncident.harm_type == harm_type)
            if attack_tactic:
                conditions.append(AIIncident.attack_tactic == attack_tactic)
            if severity:
                conditions.append(AIIncident.severity == severity)
            if modality:
                conditions.append(AIIncident.modality == modality)
            if verified_only:
                conditions.append(AIIncident.verified == True)
            if featured_only:
                conditions.append(AIIncident.is_featured_example == True)
            
            # Apply conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Order by creation date (newest first)
            query = query.order_by(AIIncident.created_at.desc())
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise Exception(f"Error searching incidents: {str(e)}")

    async def get_incidents_with_aiuc_safeguards(
        self,
        session: AsyncSession,
        aiuc_safeguard_id: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """Get incidents that are addressed by a specific AIUC-1 safeguard."""
        try:
            query = select(AIIncident).where(
                AIIncident.aiuc_safeguard_ids.op('?')(aiuc_safeguard_id)
            ).order_by(AIIncident.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise Exception(f"Error getting incidents by AIUC safeguard: {str(e)}")

    async def get_base_rate_statistics(
        self,
        session: AsyncSession,
        industry: Optional[str] = None,
        use_case: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get base rate frequency and severity statistics.
        
        Args:
            session: Database session
            industry: Filter by industry
            use_case: Filter by use case
            
        Returns:
            Dictionary with base rate statistics
        """
        try:
            # Build base query
            query = select(AIIncident)
            
            conditions = []
            if industry:
                conditions.append(AIIncident.industry == industry)
            if use_case:
                conditions.append(AIIncident.use_case == use_case)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            result = await session.execute(query)
            incidents = list(result.scalars().all())
            
            if not incidents:
                return {
                    "total_incidents": 0,
                    "frequency_distribution": {},
                    "severity_distribution": {},
                    "average_financial_impact": None
                }
            
            # Calculate statistics
            frequency_counts = {}
            severity_counts = {}
            financial_impacts = []
            
            for incident in incidents:
                # Frequency distribution
                if incident.base_rate_frequency:
                    freq = incident.base_rate_frequency
                    frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
                
                # Severity distribution
                if incident.base_rate_severity:
                    sev = incident.base_rate_severity
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                # Financial impact
                if incident.total_financial_impact:
                    financial_impacts.append(float(incident.total_financial_impact))
            
            # Calculate average financial impact
            avg_financial_impact = None
            if financial_impacts:
                avg_financial_impact = sum(financial_impacts) / len(financial_impacts)
            
            return {
                "total_incidents": len(incidents),
                "frequency_distribution": frequency_counts,
                "severity_distribution": severity_counts,
                "average_financial_impact": avg_financial_impact,
                "financial_impact_range": {
                    "min": min(financial_impacts) if financial_impacts else None,
                    "max": max(financial_impacts) if financial_impacts else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Error calculating base rate statistics: {str(e)}")