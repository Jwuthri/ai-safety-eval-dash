"""
Cleanup precomputed_answers notes column.

Removes "Grade: " prefix from notes, leaving just the grade value (PASS, P0, P1, etc.)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.models.precomputed_answer import PreComputedAnswer


def cleanup_notes():
    """Remove 'Grade: ' prefix from precomputed_answers notes."""
    db = SessionLocal()
    
    try:
        # Get all precomputed answers
        answers = db.query(PreComputedAnswer).all()
        
        print(f"📊 Found {len(answers)} precomputed answers")
        
        updated_count = 0
        
        for answer in answers:
            if answer.notes and answer.notes.startswith("Grade: "):
                # Remove "Grade: " prefix
                old_note = answer.notes
                answer.notes = answer.notes.replace("Grade: ", "", 1)
                
                if updated_count < 5:  # Show first 5 examples
                    print(f"   '{old_note}' → '{answer.notes}'")
                
                updated_count += 1
        
        if updated_count > 5:
            print(f"   ... and {updated_count - 5} more")
        
        if updated_count == 0:
            print("✅ No notes to clean up!")
        else:
            db.commit()
            print(f"\n✅ Updated {updated_count} notes")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧹 Cleanup Precomputed Answer Notes")
    print("="*70 + "\n")
    
    cleanup_notes()
    
    print("\n" + "="*70)
    print("✨ Cleanup Complete!")
    print("="*70 + "\n")
