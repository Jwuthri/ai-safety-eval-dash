"""
Import precomputed answers from CSV file.

Reads the CSV and imports Output (Round 1), Output (Round 2), etc.
into the precomputed_answers table.
"""

import csv
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.repositories import (
    OrganizationRepository,
    PreComputedAnswerRepository,
    ScenarioRepository,
)


def import_precomputed_answers(organization_name: str = "Pinterest Inc"):
    """
    Import precomputed answers from CSV for a given organization.
    
    Args:
        organization_name: Name of the organization (default: Pinterest Inc)
    """
    db = SessionLocal()
    
    try:
        # Get the organization
        orgs = OrganizationRepository.get_all(db)
        org = next((o for o in orgs if organization_name.lower() in o.name.lower()), None)
        
        if not org:
            print(f"❌ Organization '{organization_name}' not found.")
            print(f"Available organizations: {[o.name for o in orgs]}")
            return
        
        print(f"✅ Found organization: {org.name} (ID: {org.id})")
        
        # Load CSV
        csv_path = Path(__file__).parent.parent / "docs" / "Ada_Pinterest_ Evaluations round 1, 2 & 3 [EXAMPLE] - Evaluations - round 1 & 2.csv"
        
        if not csv_path.exists():
            print(f"❌ CSV file not found: {csv_path}")
            return
        
        print(f"📂 Reading CSV: {csv_path.name}")
        
        # Get all scenarios for this org's business type
        scenarios = ScenarioRepository.get_by_business_type(db, org.business_type_id)
        
        # Create mapping: input_prompt -> scenario_id
        scenario_map = {s.input_prompt.strip(): s.id for s in scenarios}
        
        print(f"📊 Found {len(scenarios)} scenarios for {org.business_type.name}")
        
        imported_count = 0
        skipped_count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                input_text = row.get('Input', '').strip()
                
                # Find matching scenario
                scenario_id = scenario_map.get(input_text)
                
                if not scenario_id:
                    skipped_count += 1
                    continue
                
                # Import Round 1 if exists
                output_round_1 = row.get('Output (Round 1)', '').strip()
                if output_round_1:
                    # Check if already exists
                    existing = PreComputedAnswerRepository.get_by_scenario_and_round(
                        db, scenario_id, round_number=1, organization_id=org.id
                    )
                    
                    if not existing:
                        grade_round_1 = row.get('Grade (Round 1)', '').strip()
                        notes = grade_round_1 if grade_round_1 else None
                        
                        PreComputedAnswerRepository.create(
                            db,
                            organization_id=org.id,
                            scenario_id=scenario_id,
                            round_number=1,
                            assistant_output=output_round_1,
                            notes=notes
                        )
                        imported_count += 1
                
                # Import Round 2 if exists
                output_round_2 = row.get('Output (Round 2)', '').strip()
                if output_round_2:
                    # Check if already exists
                    existing = PreComputedAnswerRepository.get_by_scenario_and_round(
                        db, scenario_id, round_number=2, organization_id=org.id
                    )
                    
                    if not existing:
                        grade_round_2 = row.get('Grade (Round 2)', '').strip()
                        notes = grade_round_2 if grade_round_2 else None
                        
                        PreComputedAnswerRepository.create(
                            db,
                            organization_id=org.id,
                            scenario_id=scenario_id,
                            round_number=2,
                            assistant_output=output_round_2,
                            notes=notes
                        )
                        imported_count += 1
        
        print(f"\n✅ Imported {imported_count} precomputed answers")
        print(f"⏭️  Skipped {skipped_count} rows (no matching scenario)")
        
        # Show summary
        total_round_1 = len(PreComputedAnswerRepository.get_by_round(db, org.id, 1))
        total_round_2 = len(PreComputedAnswerRepository.get_by_round(db, org.id, 2))
        
        print(f"\n📊 Summary for {org.name}:")
        print(f"   • Round 1 answers: {total_round_1}")
        print(f"   • Round 2 answers: {total_round_2}")
        
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Import precomputed answers from CSV')
    parser.add_argument(
        '--org',
        default='Pinterest Inc',
        help='Organization name (default: Pinterest Inc)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📥 Importing Precomputed Answers")
    print("="*70 + "\n")
    
    import_precomputed_answers(args.org)
    
    print("\n" + "="*70)
    print("✨ Import Complete!")
    print("="*70 + "\n")
