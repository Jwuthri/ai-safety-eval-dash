"""
Sample scenarios across categories to reduce dataset size.

Reduces scenarios from 300 to 100 by sampling proportionally across categories
to maintain diversity.

WARNING: This will DELETE scenarios from the database. Run with caution!
"""

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.repositories import (
    ScenarioRepository,
    BusinessTypeRepository,
    PreComputedAnswerRepository,
)


def sample_scenarios_by_category(
    business_type_id: str,
    target_count: int = 100,
    dry_run: bool = True
):
    """
    Sample scenarios across categories to reduce total count.
    
    Args:
        business_type_id: Business type ID to sample from
        target_count: Target number of scenarios to keep (default: 100)
        dry_run: If True, only show what would be deleted (default: True)
    """
    db = SessionLocal()
    
    try:
        # Get business type
        biz_type = BusinessTypeRepository.get_by_id(db, business_type_id)
        if not biz_type:
            print(f"❌ Business type {business_type_id} not found")
            return
        
        print(f"📊 Business Type: {biz_type.name}")
        
        # Get all scenarios
        scenarios = ScenarioRepository.get_by_business_type(db, business_type_id)
        total_count = len(scenarios)
        
        if total_count <= target_count:
            print(f"✅ Already at or below target ({total_count} <= {target_count})")
            return
        
        print(f"📈 Current count: {total_count}")
        print(f"🎯 Target count: {target_count}")
        print(f"🗑️  Will remove: {total_count - target_count}\n")
        
        # Group by category
        by_category = defaultdict(list)
        for scenario in scenarios:
            category = scenario.category or "Uncategorized"
            by_category[category].append(scenario)
        
        print(f"📂 Categories found: {len(by_category)}\n")
        
        # Show distribution
        for category, items in sorted(by_category.items()):
            print(f"   • {category}: {len(items)} scenarios")
        
        print()
        
        # Calculate proportional sampling
        # Sample proportionally from each category
        scenarios_to_keep = []
        scenarios_to_delete = []
        
        for category, items in sorted(by_category.items()):
            # Calculate how many to keep from this category (proportional)
            proportion = len(items) / total_count
            keep_count = max(1, int(proportion * target_count))  # At least 1 per category
            
            # Ensure we don't over-sample
            keep_count = min(keep_count, len(items))
            
            # Sample randomly from this category
            import random
            random.shuffle(items)
            
            scenarios_to_keep.extend(items[:keep_count])
            scenarios_to_delete.extend(items[keep_count:])
            
            print(f"   {category}: keeping {keep_count}/{len(items)}")
        
        # Adjust if we're over/under target
        current_keep = len(scenarios_to_keep)
        if current_keep > target_count:
            # Remove excess randomly
            import random
            random.shuffle(scenarios_to_keep)
            excess = scenarios_to_keep[target_count:]
            scenarios_to_keep = scenarios_to_keep[:target_count]
            scenarios_to_delete.extend(excess)
        elif current_keep < target_count:
            # Add more from delete pile
            shortfall = target_count - current_keep
            import random
            random.shuffle(scenarios_to_delete)
            scenarios_to_keep.extend(scenarios_to_delete[:shortfall])
            scenarios_to_delete = scenarios_to_delete[shortfall:]
        
        print(f"\n📊 Final Distribution:")
        print(f"   ✅ Keeping: {len(scenarios_to_keep)}")
        print(f"   ❌ Deleting: {len(scenarios_to_delete)}")
        
        if dry_run:
            print(f"\n🔍 DRY RUN MODE - No changes will be made")
            print(f"\nTo actually delete, run with --execute flag")
        else:
            # First, delete related precomputed_answers to avoid orphaned records
            print(f"\n⚠️  DELETING related precomputed answers...")
            deleted_precomputed = 0
            for scenario in scenarios_to_delete:
                # Get all precomputed answers for this scenario
                from app.database.models.precomputed_answer import PreComputedAnswer
                precomputed_answers = db.query(PreComputedAnswer).filter_by(scenario_id=scenario.id).all()
                for answer in precomputed_answers:
                    db.delete(answer)
                    deleted_precomputed += 1
            
            print(f"   🗑️  Deleted {deleted_precomputed} precomputed answers")
            
            # Now delete scenarios
            print(f"\n⚠️  DELETING {len(scenarios_to_delete)} scenarios...")
            for scenario in scenarios_to_delete:
                db.delete(scenario)
            
            db.commit()
            print(f"✅ Successfully reduced scenarios from {total_count} to {len(scenarios_to_keep)}")
        
        # Show final category breakdown
        if dry_run:
            print(f"\n📂 Category breakdown after sampling:")
            final_by_category = defaultdict(int)
            for scenario in scenarios_to_keep:
                category = scenario.category or "Uncategorized"
                final_by_category[category] += 1
            
            for category, count in sorted(final_by_category.items()):
                print(f"   • {category}: {count} scenarios")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sample scenarios across categories')
    parser.add_argument(
        '--business-type-id',
        default='faa0780e-6ac3-4a4b-a719-720c21c7dbb9',
        help='Business type ID to sample from'
    )
    parser.add_argument(
        '--target',
        type=int,
        default=100,
        help='Target number of scenarios to keep (default: 100)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually delete scenarios (default: dry run only)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🎲 Scenario Sampling Tool")
    print("="*70 + "\n")
    
    sample_scenarios_by_category(
        business_type_id=args.business_type_id,
        target_count=args.target,
        dry_run=not args.execute
    )
    
    print("\n" + "="*70)
    if not args.execute:
        print("💡 Tip: Add --execute flag to actually perform the deletion")
    else:
        print("✨ Sampling Complete!")
    print("="*70 + "\n")
