#!/usr/bin/env python3
"""
Sync exam data to MongoDB Atlas.
Performs upsert operations for each exam to ensure no sync issues.
"""

import json
import glob
import os
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import certifi

REPO_ROOT = Path(__file__).parent.parent.parent
EXAM_GLOB_PATTERN = str(REPO_ROOT / "**" / "*.json")

# Skip files that should not be processed
SKIP_FILES = {
    "encryption.pub",
    ".mcp.json",
    "settings.json",
    "settings.local.json",
}

CATEGORIES = {"NEET", "JEE", "UPSC", "SSC", "Banking", "Railways", "State-PSC"}


def get_mongodb_client():
    """Create MongoDB client from connection string."""
    connection_string = os.getenv("MONGODB_URI")
    if not connection_string:
        raise ValueError("MONGODB_URI environment variable not set")

    try:
        # Connection options for GitHub Actions compatibility
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            retryWrites=True,
            maxPoolSize=50,
            tlsCAFile=certifi.where()
        )
        # Verify connection
        client.admin.command("ping")
        print("✓ Connected to MongoDB Atlas")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {e}")


def should_process_file(filepath):
    """Check if a file should be processed."""
    filename = os.path.basename(filepath)

    # Skip if filename is in skip list
    if filename in SKIP_FILES:
        return False

    # Skip files in .github, .claude directories
    if "/.github/" in filepath or "/.claude/" in filepath:
        return False

    # Skip index.json files (category indexes)
    if filename == "index.json":
        return False

    # Only process exam-like JSON files (in category folders with exam data)
    parts = filepath.split(os.sep)
    if len(parts) < 2:
        return False

    parent_dir = parts[-2]
    return parent_dir in CATEGORIES


def load_exam_file(filepath):
    """Load and parse exam JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def sync_exam_to_db(db, exam_data):
    """Upsert exam document to MongoDB."""
    exam_id = exam_data.get("exam_id")
    if not exam_id:
        print(f"✗ Skipping exam without exam_id")
        return False

    try:
        exams_collection = db["exams"]

        # Upsert operation: update if exists, insert if not
        result = exams_collection.update_one(
            {"exam_id": exam_id},
            {"$set": exam_data},
            upsert=True
        )

        if result.upserted_id:
            print(f"✓ Created exam: {exam_id}")
        elif result.modified_count > 0:
            print(f"✓ Updated exam: {exam_id}")
        else:
            print(f"- No changes needed for: {exam_id}")

        return True
    except Exception as e:
        print(f"✗ Error syncing {exam_id}: {e}")
        return False


def sync_categories_to_db(db):
    """Sync category metadata to MongoDB."""
    try:
        categories_collection = db["categories"]

        category_docs = [
            {
                "name": "NEET",
                "title": "National Eligibility cum Entrance Test",
                "description": "Medical entrance examination",
                "is_active": True
            },
            {
                "name": "JEE",
                "title": "Joint Entrance Examination",
                "description": "Engineering entrance examination",
                "is_active": True
            },
            {
                "name": "UPSC",
                "title": "Union Public Service Commission",
                "description": "Civil services examination",
                "is_active": True
            },
            {
                "name": "SSC",
                "title": "Staff Selection Commission",
                "description": "Government recruitment examination",
                "is_active": True
            },
            {
                "name": "Banking",
                "title": "Banking Sector Exams",
                "description": "Banking and financial sector examinations",
                "is_active": True
            },
            {
                "name": "Railways",
                "title": "Railway Recruitment Board",
                "description": "Railway recruitment examinations",
                "is_active": True
            },
            {
                "name": "State-PSC",
                "title": "State Public Service Commissions",
                "description": "State-level civil service examinations",
                "is_active": True
            }
        ]

        for category in category_docs:
            result = categories_collection.update_one(
                {"name": category["name"]},
                {"$set": category},
                upsert=True
            )
            if result.upserted_id:
                print(f"✓ Created category: {category['name']}")
            elif result.modified_count > 0:
                print(f"✓ Updated category: {category['name']}")

        return True
    except Exception as e:
        print(f"✗ Error syncing categories: {e}")
        return False


def main():
    """Main function to sync all exams to MongoDB."""
    print("Starting MongoDB sync...")

    try:
        # Connect to MongoDB
        client = get_mongodb_client()
        db = client["exams_db"]

        # Sync categories first
        print("\nSyncing categories...")
        sync_categories_to_db(db)

        # Find and sync all exam files
        print("\nSyncing exams...")
        exam_files = glob.glob(EXAM_GLOB_PATTERN, recursive=True)
        exam_files = [f for f in exam_files if should_process_file(f)]

        if not exam_files:
            print("No exam files found to process.")
            return

        print(f"Found {len(exam_files)} exam files to process.")

        synced_count = 0
        for filepath in exam_files:
            try:
                exam_data = load_exam_file(filepath)
                if sync_exam_to_db(db, exam_data):
                    synced_count += 1
            except json.JSONDecodeError as e:
                print(f"✗ Invalid JSON in {filepath}: {e}")
            except Exception as e:
                print(f"✗ Error processing {filepath}: {e}")

        print(f"\n✓ Sync complete. {synced_count} exams processed.")
        client.close()

    except Exception as e:
        print(f"✗ Critical error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
