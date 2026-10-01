"""
AgriSmart AI — Database Initialization & Knowledge Base Seeder
================================================================
Run to initialize tables and populate the complete pre-trained
knowledge base (18 crops across Hydroponics, Algaculture, and Fungi
with environmental, water, nutrient, substrate, infrastructure,
nutrition, economics, quality tests, and laboratory data).

Usage:
    python seed.py
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.services.seeder import seed_all_master_data


def main():
    print("\n" + "=" * 65)
    print("[INFO] AgriSmart AI — Pre-trained Knowledge Base Initialization")
    print("=" * 65)

    config_name = os.environ.get("FLASK_ENV", "development")
    app = create_app(config_name)

    with app.app_context():
        db.create_all()
        seed_all_master_data(db.session)
        print("=" * 65)
        print("[SUCCESS] Master Knowledge Base is fully populated and ready!")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
