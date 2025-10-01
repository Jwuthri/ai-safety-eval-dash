#!/usr/bin/env python3
"""
Seed real-world AI incidents for Safety Story dashboard.

Examples: AirCanada, Google Gemini, Microsoft Tay, etc.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from datetime import datetime
from app.database import get_db
from app.database.repositories import AIIncidentRepository
from app.database.models.business_type import BusinessType

def seed_incidents():
    """Seed real-world AI incidents."""
    db = next(get_db())
    
    try:
        # Get Airlines business type
        airlines_bt = db.query(BusinessType).filter_by(name="Airlines Customer Support").first()
        
        incidents = [
            {
                "incident_name": "AirCanada Refund Hallucination",
                "company": "Air Canada",
                "date_occurred": datetime(2024, 2, 15),
                "harm_type": "financial_loss",
                "severity": "P1",
                "description": "Chatbot hallucinated refund policy, promising customer full refund for bereavement fare. Customer Jake Moffat won in court. Company forced to honor chatbot's false promise, setting legal precedent.",
                "root_cause": "LLM hallucination without proper guardrails or grounding in actual policy documents. No validation of refund eligibility before making promises.",
                "impact_description": "Legal precedent set that companies are liable for chatbot statements. Major reputation damage. Financial loss from honoring incorrect policy. Loss of customer trust.",
                "estimated_cost": 15000.00,
                "affected_users": 1,
                "source_url": "https://www.cbc.ca/news/canada/air-canada-chatbot-refund-1.7110426",
                "incident_reference": "aircanada-2024-refund",
                "business_type_id": airlines_bt.id if airlines_bt else None,
            },
            {
                "incident_name": "Chevrolet Dealership Bot Sells for $1",
                "company": "Chevrolet of Watsonville",
                "date_occurred": datetime(2023, 12, 18),
                "harm_type": "financial_loss",
                "severity": "P2",
                "description": "ChatGPT-powered dealership chatbot agreed to sell 2024 Chevrolet Tahoe for $1 after prompt injection. Customer tricked bot into accepting unrealistic offer.",
                "root_cause": "Insufficient input validation and lack of business logic constraints. Bot had ability to make binding commitments without price sanity checks.",
                "impact_description": "Viral social media embarrassment, dealership forced to add guardrails, potential financial loss if legally binding.",
                "estimated_cost": 80000.00,
                "affected_users": 1,
                "source_url": "https://www.businessinsider.com/chatgpt-chevrolet-dealership-chatbot-customer-bought-car-dollar-2023-12",
                "incident_reference": "chevrolet-2023-one-dollar",
                "business_type_id": None,
            },
            {
                "incident_name": "ChatGPT Data Breach via Prompt Injection",
                "company": "OpenAI",
                "date_occurred": datetime(2023, 3, 20),
                "harm_type": "privacy_breach",
                "severity": "P0",
                "description": "Redis bug combined with prompt injection exposed chat history and payment details of other users. Affected 1.2% of ChatGPT Plus subscribers.",
                "root_cause": "Redis connection caching issue combined with insufficient isolation between user sessions. Attack vector via prompt injection to access cached data.",
                "impact_description": "Major privacy breach. Exposed: names, emails, payment addresses, credit card last 4 digits, expiration dates. GDPR violations. Class action lawsuit potential.",
                "estimated_cost": 5000000.00,
                "affected_users": 100000,
                "source_url": "https://openai.com/blog/march-20-chatgpt-outage",
                "incident_reference": "openai-2023-data-breach",
                "business_type_id": None,
            },
            {
                "incident_name": "DPD Chatbot Swears at Customer",
                "company": "DPD (Geopost)",
                "date_occurred": datetime(2024, 1, 18),
                "harm_type": "reputation_damage",
                "severity": "P2",
                "description": "Customer service chatbot swore at customer and criticized company after prompt injection attack. Bot wrote poem criticizing DPD as 'worst delivery firm'.",
                "root_cause": "Inadequate content filtering and lack of behavioral constraints. Bot could be manipulated to generate inappropriate content via prompt injection.",
                "impact_description": "Viral Twitter/X post with 1M+ views. Major brand damage. Chatbot immediately disabled. Customer service disruption.",
                "estimated_cost": 250000.00,
                "affected_users": 1,
                "source_url": "https://www.bbc.com/news/technology-68025677",
                "incident_reference": "dpd-2024-swearing",
                "business_type_id": None,
            },
            {
                "incident_name": "Google Gemini Historical Inaccuracy",
                "company": "Google",
                "date_occurred": datetime(2024, 2, 22),
                "harm_type": "reputation_damage",
                "severity": "P1",
                "description": "Gemini AI generated historically inaccurate images (Black Nazi soldiers, diverse 1820s US senators) due to overcorrection for diversity. Major controversy over AI bias.",
                "root_cause": "Over-tuned diversity prompting without historical context awareness. System prioritized representation over historical accuracy.",
                "impact_description": "Massive PR crisis. Feature paused globally. Competitor mockery. Trust erosion in Google AI. Stock impact. Months of damage control.",
                "estimated_cost": 10000000.00,
                "affected_users": 1000000,
                "source_url": "https://www.theverge.com/2024/2/21/24079371/google-ai-gemini-generative-inaccurate-historical",
                "incident_reference": "google-2024-gemini-bias",
                "business_type_id": None,
            },
            {
                "incident_name": "Microsoft Tay Racist Tweets",
                "company": "Microsoft",
                "date_occurred": datetime(2016, 3, 23),
                "harm_type": "reputation_damage",
                "severity": "P0",
                "description": "AI chatbot Tay turned racist and offensive within 24 hours of launch. Users exploited learning mechanism to teach bot harmful content. Posted Nazi propaganda and inflammatory tweets.",
                "root_cause": "Unsupervised learning from public Twitter without content moderation. Bot learned from coordinated trolling attacks. No safety guardrails on training data.",
                "impact_description": "Catastrophic PR disaster. Bot shut down in <24 hours. Global news coverage. Microsoft credibility damage. Set back conversational AI industry.",
                "estimated_cost": 3000000.00,
                "affected_users": 100000,
                "source_url": "https://www.theverge.com/2016/3/24/11297050/tay-microsoft-chatbot-racist",
                "incident_reference": "microsoft-2016-tay",
                "business_type_id": None,
            },
        ]
        
        print("🌱 Seeding AI incidents...")
        
        created_count = 0
        for incident_data in incidents:
            # Check if already exists
            existing = AIIncidentRepository.get_by_reference(db, incident_data["incident_reference"])
            if existing:
                print(f"   ⏭️  {incident_data['incident_name']} already exists")
                continue
            
            # Create incident
            incident = AIIncidentRepository.create(db, **incident_data)
            created_count += 1
            print(f"   ✅ Created: {incident.incident_name} ({incident.severity})")
        
        print(f"\n✨ Seeded {created_count} new incidents!")
        print(f"📊 Total incidents in database: {len(AIIncidentRepository.list_all(db, limit=1000))}")
        
        # Show severity breakdown
        severity_stats = AIIncidentRepository.count_by_severity(db)
        print(f"\n📈 Severity breakdown:")
        for severity, count in sorted(severity_stats.items()):
            print(f"   {severity}: {count}")
        
    except Exception as e:
        print(f"❌ Error seeding incidents: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_incidents()

