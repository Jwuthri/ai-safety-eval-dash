#!/usr/bin/env python3
"""
Example: Run an AI Safety Evaluation Round

Demonstrates:
1. Creating an evaluation round for an organization
2. Running parallel judge evaluations (Claude Sonnet 4.5, GPT-5, Grok-4 Fast)
3. Viewing results and statistics
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.repositories import OrganizationRepository
from app.services.evaluation_orchestrator import EvaluationOrchestrator


async def run_evaluation_example():
    """Run a sample evaluation round."""
    db = SessionLocal()

    try:
        print("🚀 AI Safety Evaluation Pipeline Demo")
        print("=" * 60)

        # 1. Get an organization to evaluate
        org = OrganizationRepository.get_by_slug(db, "pinterest")
        if not org:
            print("❌ Pinterest organization not found. Run seed script first.")
            return

        print(f"\n📋 Organization: {org.name}")
        print(f"   Business Type ID: {org.business_type_id}")
        print(f"   Slug: {org.slug}")

        # 2. Create orchestrator
        orchestrator = EvaluationOrchestrator(db)

        # 3. Run evaluation round (just first 3 scenarios for demo)
        print("\n🔬 Starting Evaluation Round 1...")
        print("   This will evaluate scenarios using 3 parallel judges:")
        print("   • Judge 1: Claude Sonnet 4.5")
        print("   • Judge 2: GPT-5")
        print("   • Judge 3: Grok-4 Fast")
        print()

        # Note: For demo, we'll manually limit scenarios in the orchestrator
        # In production, this would evaluate ALL scenarios
        round_id = await orchestrator.run_evaluation_round(
            organization_id=org.id,
            round_number=1,
            description="Initial safety evaluation - Demo",
        )

        print(f"\n✅ Evaluation Round Completed!")
        print(f"   Round ID: {round_id}")

        # 4. Get statistics
        stats = orchestrator.get_round_statistics(round_id)
        print(f"\n📊 Evaluation Statistics:")
        print(f"   Total Tests: {stats['total_tests']}")
        print(f"   Pass Rate: {stats['pass_rate']}%")
        print(f"   Pass Count: {stats['pass_count']}")
        print(f"\n   Severity Breakdown:")
        for severity, count in stats["severity_breakdown"].items():
            if count > 0:
                print(f"     • {severity}: {count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    print("⚠️  WARNING: This will call OpenRouter APIs and incur costs!")
    print("   It will run evaluation with 3 LLM judges in parallel.")
    print()

    response = input("Continue? (y/n): ")
    if response.lower() == "y":
        asyncio.run(run_evaluation_example())
    else:
        print("Cancelled.")
