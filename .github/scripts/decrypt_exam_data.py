#!/usr/bin/env python3
"""
Decrypt sensitive exam data (correct answers and explanations) using RSA private key.
This script processes all exam JSON files and decrypts sensitive fields.
Usage: python decrypt_exam_data.py <path_to_private_key>
"""

import json
import base64
import glob
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

REPO_ROOT = Path(__file__).parent.parent.parent
EXAM_GLOB_PATTERN = str(REPO_ROOT / "**" / "*.json")

# Skip files that should not be processed
SKIP_FILES = {
    "encryption.pub",
    ".mcp.json",
    "settings.json",
    "settings.local.json",
}


def load_private_key(private_key_path, password=None):
    """Load the RSA private key."""
    if not os.path.exists(private_key_path):
        raise FileNotFoundError(f"Private key not found at {private_key_path}")

    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=password, backend=default_backend()
        )
    return private_key


def decrypt_value(encrypted_data, private_key):
    """Decrypt a value using RSA private key."""
    if not isinstance(encrypted_data, dict) or not encrypted_data.get("__encrypted__"):
        return encrypted_data

    try:
        ciphertext = base64.b64decode(encrypted_data["data"])
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return plaintext.decode("utf-8")
    except Exception as e:
        print(f"Failed to decrypt value: {e}")
        return encrypted_data


def process_exam_file(filepath, private_key):
    """Process a single exam file and decrypt sensitive fields."""
    with open(filepath, "r") as f:
        data = json.load(f)

    modified = False

    # Process sections and questions
    if "sections" in data and isinstance(data["sections"], list):
        for section in data["sections"]:
            if "questions" in section and isinstance(section["questions"], list):
                for question in section["questions"]:
                    # Decrypt correct_option
                    if "correct_option" in question:
                        correct_option = question["correct_option"]
                        if isinstance(correct_option, dict) and correct_option.get(
                            "__encrypted__"
                        ):
                            question["correct_option"] = decrypt_value(
                                correct_option, private_key
                            )
                            modified = True

                    # Decrypt explanation
                    if "explanation" in question:
                        explanation = question["explanation"]
                        if isinstance(explanation, dict) and explanation.get(
                            "__encrypted__"
                        ):
                            question["explanation"] = decrypt_value(
                                explanation, private_key
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

    if filename in SKIP_FILES:
        return False

    if "/.github/" in filepath or "/.claude/" in filepath:
        return False

    if filename == "index.json":
        return False

    parts = filepath.split(os.sep)
    if len(parts) < 2:
        return False

    parent_dir = parts[-2]
    categories = {"NEET", "JEE", "UPSC", "SSC", "Banking", "Railways", "State-PSC"}

    return parent_dir in categories


def main():
    """Main function to decrypt all exam files."""
    if len(sys.argv) < 2:
        print("Usage: python decrypt_exam_data.py <path_to_private_key> [password]")
        sys.exit(1)

    private_key_path = sys.argv[1]
    password = sys.argv[2].encode() if len(sys.argv) > 2 else None

    print(f"Loading private key from {private_key_path}...")
    private_key = load_private_key(private_key_path, password)

    print("Finding encrypted exam files...")
    exam_files = glob.glob(EXAM_GLOB_PATTERN, recursive=True)
    exam_files = [f for f in exam_files if should_process_file(f)]

    if not exam_files:
        print("No exam files found to process.")
        return

    print(f"Found {len(exam_files)} exam files to process.")

    decrypted_count = 0
    for filepath in exam_files:
        try:
            if process_exam_file(filepath, private_key):
                decrypted_count += 1
                print(f"✓ Decrypted: {filepath}")
            else:
                print(f"- No encrypted data: {filepath}")
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in {filepath}: {e}")
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}")

    print(f"\nDecryption complete. {decrypted_count} files updated.")


if __name__ == "__main__":
    main()
