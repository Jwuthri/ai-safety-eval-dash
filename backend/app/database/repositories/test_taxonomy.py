"""
Test Taxonomy repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.test_taxonomy import TestTaxonomy
from .base_async import AsyncBaseRepository


class TestTaxonomyRepository(AsyncBaseRepository[TestTaxonomy]):
    """Repository for test taxonomy operations."""

    def __init__(self):
        super().__init__(TestTaxonomy)

    async def get_by_category(
        self,
        session: AsyncSession,
        category: str,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """Get tests by category (e.g., jailbreaks, hallucinations)."""
        return await self.list_with_filters(
            session,
            filters={"category": category},
            order_by="created_at",
            limit=limit
        )

    async def get_by_modality(
        self,
        session: AsyncSession,
        modality: str,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """Get tests by modality (text, voice, multimodal)."""
        return await self.list_with_filters(
            session,
            filters={"modality": modality},
            order_by="category",
            limit=limit
        )

    async def get_by_aiuc_requirement(
        self,
        session: AsyncSession,
        aiuc_requirement: str,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """Get tests by AIUC-1 requirement."""
        return await self.list_with_filters(
            session,
            filters={"aiuc_requirement": aiuc_requirement},
            order_by="category",
            limit=limit
        )

    async def get_tests_for_incident(
        self,
        session: AsyncSession,
        incident_id: str,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """Get tests that address a specific incident."""
        try:
            query = select(TestTaxonomy).where(
                TestTaxonomy.related_incident_ids.op('?')(incident_id)
            ).order_by(TestTaxonomy.category)
            
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise Exception(f"Error getting tests for incident: {str(e)}")

    async def get_tests_for_harm_type(
        self,
        session: AsyncSession,
        harm_type: str,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """Get tests that address a specific harm type."""
        try:
            query = select(TestTaxonomy).where(
                TestTaxonomy.harm_types_addressed.op('?')(harm_type)
            ).order_by(TestTaxonomy.category)
            
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise Exception(f"Error getting tests for harm type: {str(e)}")

    async def search_tests(
        self,
        session: AsyncSession,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        modality: Optional[str] = None,
        aiuc_requirement: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        incident_id: Optional[str] = None,
        harm_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TestTaxonomy]:
        """
        Search tests with multiple filter criteria.
        
        Args:
            session: Database session
            category: Filter by test category
            subcategory: Filter by subcategory
            modality: Filter by modality
            aiuc_requirement: Filter by AIUC requirement
            difficulty_level: Filter by difficulty level
            incident_id: Filter by related incident ID
            harm_type: Filter by harm type addressed
            limit: Maximum number of results
            
        Returns:
            List of matching test taxonomy entries
        """
        try:
            query = select(TestTaxonomy)
            
            # Build filter conditions
            conditions = []
            
            if category:
                conditions.append(TestTaxonomy.category == category)
            if subcategory:
                conditions.append(TestTaxonomy.subcategory == subcategory)
            if modality:
                conditions.append(TestTaxonomy.modality == modality)
            if aiuc_requirement:
                conditions.append(TestTaxonomy.aiuc_requirement == aiuc_requirement)
            if difficulty_level:
                conditions.append(TestTaxonomy.difficulty_level == difficulty_level)
            if incident_id:
                conditions.append(TestTaxonomy.related_incident_ids.op('?')(incident_id))
            if harm_type:
                conditions.append(TestTaxonomy.harm_types_addressed.op('?')(harm_type))
            
            # Apply conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Order by category, then subcategory
            query = query.order_by(TestTaxonomy.category, TestTaxonomy.subcategory)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            raise Exception(f"Error searching tests: {str(e)}")

    async def get_category_statistics(
        self,
        session: AsyncSession,
        modality: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about test categories.
        
        Args:
            session: Database session
            modality: Filter by modality
            
        Returns:
            Dictionary with category statistics
        """
        try:
            query = select(TestTaxonomy)
            
            if modality:
                query = query.where(TestTaxonomy.modality == modality)
            
            result = await session.execute(query)
            tests = list(result.scalars().all())
            
            if not tests:
                return {
                    "total_tests": 0,
                    "categories": {},
                    "modalities": {},
                    "difficulty_levels": {}
                }
            
            # Calculate statistics
            category_counts = {}
            modality_counts = {}
            difficulty_counts = {}
            
            for test in tests:
                # Category distribution
                cat = test.category
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
                # Modality distribution
                mod = test.modality
                modality_counts[mod] = modality_counts.get(mod, 0) + 1
                
                # Difficulty distribution
                if test.difficulty_level:
                    diff = test.difficulty_level
                    difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
            
            return {
                "total_tests": len(tests),
                "categories": category_counts,
                "modalities": modality_counts,
                "difficulty_levels": difficulty_counts
            }
            
        except Exception as e:
            raise Exception(f"Error calculating category statistics: {str(e)}")

    async def get_aiuc_coverage_mapping(
        self,
        session: AsyncSession
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get mapping of AIUC-1 requirements to test categories.
        
        Returns:
            Dictionary mapping AIUC requirements to test information
        """
        try:
            result = await session.execute(select(TestTaxonomy))
            tests = list(result.scalars().all())
            
            aiuc_mapping = {}
            
            for test in tests:
                req = test.aiuc_requirement
                if req not in aiuc_mapping:
                    aiuc_mapping[req] = []
                
                aiuc_mapping[req].append({
                    "id": str(test.id),
                    "category": test.category,
                    "subcategory": test.subcategory,
                    "tactic_type": test.tactic_type,
                    "modality": test.modality,
                    "difficulty_level": test.difficulty_level,
                    "framework_section": test.framework_section
                })
            
            return aiuc_mapping
            
        except Exception as e:
            raise Exception(f"Error getting AIUC coverage mapping: {str(e)}")