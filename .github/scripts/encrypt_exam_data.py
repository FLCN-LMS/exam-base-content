#!/usr/bin/env python3
"""
Encrypt sensitive exam data (correct answers and explanations) using RSA public key.
This script processes all exam JSON files and encrypts sensitive fields.
"""

import json
import base64
import glob
import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

REPO_ROOT = Path(__file__).parent.parent.parent
PUBLIC_KEY_PATH = REPO_ROOT / "encryption.pub"
EXAM_GLOB_PATTERN = str(REPO_ROOT / "**" / "*.json")

# Skip files that should not be processed
SKIP_FILES = {
    "encryption.pub",
    ".mcp.json",
    "settings.json",
    "settings.local.json",
}


def load_public_key():
    """Load the RSA public key from the repo."""
    if not PUBLIC_KEY_PATH.exists():
        raise FileNotFoundError(
            f"Public key not found at {PUBLIC_KEY_PATH}. "
            "Please generate RSA keys and place encryption.pub in the repo root."
        )

    with open(PUBLIC_KEY_PATH, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(), backend=default_backend()
        )
    return public_key


def encrypt_value(value, public_key):
    """Encrypt a string value using RSA public key."""
    if not value or not isinstance(value, str):
        return value

    plaintext = value.encode("utf-8")
    ciphertext = public_key.encrypt(
        plaintext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return {"__encrypted__": True, "data": base64.b64encode(ciphertext).decode("utf-8")}


def is_encrypted(value):
    """Check if a value is already encrypted."""
    return isinstance(value, dict) and value.get("__encrypted__") is True


def process_exam_file(filepath, public_key):
    """Process a single exam file and encrypt sensitive fields."""
    with open(filepath, "r") as f:
        data = json.load(f)

    modified = False

    # Process sections and questions
    if "sections" in data and isinstance(data["sections"], list):
        for section in data["sections"]:
            if "questions" in section and isinstance(section["questions"], list):
                for question in section["questions"]:
                    # Encrypt correct_option
                    if "correct_option" in question:
                        correct_option = question["correct_option"]
                        if not is_encrypted(correct_option):
                            question["correct_option"] = encrypt_value(
                                correct_option, public_key
                            )
                            modified = True

                    # Encrypt explanation
                    if "explanation" in question:
                        explanation = question["explanation"]
                        if not is_encrypted(explanation):
                            question["explanation"] = encrypt_value(
                                explanation, public_key
                            )
                            modified = True

    if modified:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False


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
    categories = {"NEET", "JEE", "UPSC", "SSC", "Banking", "Railways", "State-PSC"}

    return parent_dir in categories


def main():
    """Main function to encrypt all exam files."""
    print("Loading public key...")
    public_key = load_public_key()

    print("Finding exam files...")
    exam_files = glob.glob(EXAM_GLOB_PATTERN, recursive=True)
    exam_files = [f for f in exam_files if should_process_file(f)]

    if not exam_files:
        print("No exam files found to process.")
        return

    print(f"Found {len(exam_files)} exam files to process.")

    encrypted_count = 0
    for filepath in exam_files:
        try:
            if process_exam_file(filepath, public_key):
                encrypted_count += 1
                print(f"✓ Encrypted: {filepath}")
            else:
                print(f"- Already encrypted: {filepath}")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in {filepath}: {e}")
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}")

    print(f"\nEncryption complete. {encrypted_count} files updated.")


if __name__ == "__main__":
    main()
