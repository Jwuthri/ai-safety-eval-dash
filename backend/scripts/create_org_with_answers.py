#!/usr/bin/env python3
"""
Helper script to create a new organization with auto-copied precomputed answers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.services import OrganizationService


def main():
    """Create a new organization with precomputed answers."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("🏢 Create Organization with Precomputed Answers")
        print("="*70 + "\n")
        
        # Example usage - modify these values
        business_type_id = input("Business Type ID: ").strip()
        name = input("Organization Name: ").strip()
        slug = input("Organization Slug: ").strip()
        contact_email = input("Contact Email (optional): ").strip() or None
        
        print("\n⏳ Creating organization and copying precomputed answers...")
        
        org = OrganizationService.create_organization_with_precomputed_answers(
            db=db,
            business_type_id=business_type_id,
            name=name,
            slug=slug,
            contact_email=contact_email,
            copy_answers=True
        )
        
        print(f"\n✅ Success!")
        print(f"   Organization ID: {org.id}")
        print(f"   Name: {org.name}")
        print(f"   Business Type ID: {org.business_type_id}")
        print(f"\n🎯 Precomputed answers have been automatically copied!")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

