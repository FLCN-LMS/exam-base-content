#!/usr/bin/env python3
"""
Test encryption/decryption setup locally.
Usage: python test-encryption.py <path_to_private_key> [password]
"""

import json
import base64
import sys
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

REPO_ROOT = Path(__file__).parent.parent.parent
PUBLIC_KEY_PATH = REPO_ROOT / "encryption.pub"


def load_keys(private_key_path, password=None):
    """Load both public and private keys."""
    # Load public key
    if not PUBLIC_KEY_PATH.exists():
        raise FileNotFoundError(f"Public key not found at {PUBLIC_KEY_PATH}")

    with open(PUBLIC_KEY_PATH, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(), backend=default_backend()
        )

    # Load private key
    if not Path(private_key_path).exists():
        raise FileNotFoundError(f"Private key not found at {private_key_path}")

    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=password, backend=default_backend()
        )

    return public_key, private_key


def encrypt_value(value, public_key):
    """Encrypt a string value."""
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


def decrypt_value(encrypted_data, private_key):
    """Decrypt a value."""
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


def main():
    """Run encryption/decryption test."""
    if len(sys.argv) < 2:
        print("Usage: python test-encryption.py <path_to_private_key> [password]")
        sys.exit(1)

    private_key_path = sys.argv[1]
    password = sys.argv[2].encode() if len(sys.argv) > 2 else None

    try:
        print("Loading keys...")
        public_key, private_key = load_keys(private_key_path, password)
        print("✓ Keys loaded successfully\n")

        # Test data
        test_answer = "B"
        test_explanation = "Using v² = u² - 2gh → h = u²/2g = 400/20 = 20 m"

        print("=" * 60)
        print("ENCRYPTION/DECRYPTION TEST")
        print("=" * 60)

        # Test 1: Encrypt answer
        print("\n1. Encrypting answer...")
        print(f"   Original: {test_answer}")
        encrypted_answer = encrypt_value(test_answer, public_key)
        print(f"   Encrypted: {encrypted_answer['data'][:50]}...")
        print("   ✓ Encryption successful")

        # Test 2: Decrypt answer
        print("\n2. Decrypting answer...")
        decrypted_answer = decrypt_value(encrypted_answer, private_key)
        print(f"   Decrypted: {decrypted_answer}")
        if decrypted_answer == test_answer:
            print("   ✓ Decryption successful - matches original!")
        else:
            print(f"   ✗ FAILED - Decrypted value doesn't match!")
            return False

        # Test 3: Encrypt explanation
        print("\n3. Encrypting explanation...")
        print(f"   Original: {test_explanation[:50]}...")
        encrypted_explanation = encrypt_value(test_explanation, public_key)
        print(f"   Encrypted: {encrypted_explanation['data'][:50]}...")
        print("   ✓ Encryption successful")

        # Test 4: Decrypt explanation
        print("\n4. Decrypting explanation...")
        decrypted_explanation = decrypt_value(encrypted_explanation, private_key)
        print(f"   Decrypted: {decrypted_explanation[:50]}...")
        if decrypted_explanation == test_explanation:
            print("   ✓ Decryption successful - matches original!")
        else:
            print(f"   ✗ FAILED - Decrypted value doesn't match!")
            return False

        # Test 5: JSON round-trip
        print("\n5. JSON serialization round-trip...")
        test_json = {
            "question": "Test question?",
            "correct_option": encrypted_answer,
            "explanation": encrypted_explanation,
        }
        json_str = json.dumps(test_json, indent=2)
        loaded_json = json.loads(json_str)
        print("   ✓ JSON serialization successful")

        # Test 6: Decrypt from loaded JSON
        print("\n6. Decrypting from loaded JSON...")
        recovered_answer = decrypt_value(loaded_json["correct_option"], private_key)
        recovered_explanation = decrypt_value(
            loaded_json["explanation"], private_key
        )
        if (
            recovered_answer == test_answer
            and recovered_explanation == test_explanation
        ):
            print("   ✓ JSON round-trip successful!")
        else:
            print("   ✗ FAILED - JSON round-trip corruption!")
            return False

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nYour encryption setup is working correctly.")
        print("The GitHub Actions pipeline will use these keys to encrypt")
        print("exam answers automatically on each commit to main.")

        return True

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
