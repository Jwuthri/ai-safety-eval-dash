"""
Demo script showing the rich console progress display.

Run this to see what the evaluation progress looks like with rich formatting.

Usage:
    python backend/examples/rich_progress_demo.py rich    # With progress bars (logs suppressed)
    python backend/examples/rich_progress_demo.py silent  # API mode (logs visible)
"""

import asyncio

from app.database import SessionLocal
from app.services.evaluation_orchestrator import EvaluationOrchestrator
from app.database.repositories import OrganizationRepository


async def demo_rich_progress():
    """Demo the rich progress display with fake judges (no API costs)."""
    db = SessionLocal()
    
    try:
        # Get an organization
        orgs = OrganizationRepository.get_all(db)
        if not orgs:
            print("❌ No organizations found. Run seed script first:")
            print("   python scripts/seed_evaluation_data.py")
            return
        
        org = orgs[0]
        
        print(f"\n🎯 Running evaluation with RICH PROGRESS for: {org.name}")
        print("=" * 70)
        print("✨ Using FAKE judges (no API costs)")
        
        # Create orchestrator with progress enabled and fake judges
        orchestrator = EvaluationOrchestrator(db, show_progress=True, use_fake_judges=True)
        
        # Run evaluation
        round_id = await orchestrator.run_evaluation_round(
            organization_id=org.id,
            round_number=99  # Demo round
        )
        
        print(f"\n✅ Evaluation complete! Round ID: {round_id}")
        
    finally:
        db.close()


async def demo_no_progress():
    """Demo without progress display (API mode) with fake judges."""
    db = SessionLocal()
    
    try:
        # Get an organization
        orgs = OrganizationRepository.get_all(db)
        if not orgs:
            print("❌ No organizations found. Run seed script first:")
            print("   python scripts/seed_evaluation_data.py")
            return
        
        org = orgs[0]
        
        print(f"\n🎯 Running evaluation WITHOUT progress (API mode) for: {org.name}")
        print("=" * 70)
        print("✨ Using FAKE judges (no API costs)")
        
        # Create orchestrator without progress but with fake judges
        orchestrator = EvaluationOrchestrator(db, show_progress=False, use_fake_judges=True)
        
        # Run evaluation
        round_id = await orchestrator.run_evaluation_round(
            organization_id=org.id,
            round_number=98  # Demo round
        )
        
        print(f"\n✅ Evaluation complete! Round ID: {round_id}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "rich"
    
    if mode == "rich":
        print("\n" + "="*70)
        print("🎨 RICH PROGRESS MODE (for CLI/Notebooks)")
        print("="*70)
        asyncio.run(demo_rich_progress())
    else:
        print("\n" + "="*70)
        print("🤫 SILENT MODE (for FastAPI)")
        print("="*70)
        asyncio.run(demo_no_progress())
