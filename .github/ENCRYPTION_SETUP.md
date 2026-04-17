# Exam Data Encryption Setup

This repository uses RSA encryption to protect sensitive exam data (correct answers and explanations) while keeping questions public.

## How It Works

- **Public Repository**: Questions are visible to everyone
- **Encrypted Answers**: Correct answers and explanations are encrypted with an RSA public key
- **GitHub Actions**: On each merge to `main`, the pipeline automatically encrypts sensitive data
- **Private Key**: Only those with the private key can decrypt answers

## Initial Setup

### 1. Generate RSA Key Pair

Generate a 2048-bit RSA key pair:

```bash
# Generate private key
openssl genrsa -out encryption.key 2048

# Extract public key from private key
openssl rsa -in encryption.key -pubout -out encryption.pub
```

### 2. Add Public Key to Repository

```bash
# The public key (encryption.pub) should be committed to the repo
git add encryption.pub
git commit -m "chore: add RSA public key for exam data encryption"
git push
```

### 3. Secure the Private Key

**IMPORTANT**: Never commit the private key to the repository!

Store `encryption.key` securely:
- Keep it in a secure location (password manager, secure vault)
- Only authorized team members should have access
- Never share or expose it publicly

## Usage

### Automatic Encryption (via GitHub Actions)

When you merge changes to `main`, the GitHub Actions workflow automatically:
1. Reads all exam JSON files
2. Encrypts `correct_option` and `explanation` fields using the public key
3. Commits encrypted files back to the repository

No manual action needed!

### Manual Decryption (For Authorized Users)

To decrypt exam data locally, use the decryption script:

```bash
# Basic usage
python .github/scripts/decrypt_exam_data.py path/to/encryption.key

# If private key is password-protected
python .github/scripts/decrypt_exam_data.py path/to/encryption.key "your-password"
```

This will:
1. Find all encrypted exam files
2. Decrypt sensitive fields using your private key
3. Save decrypted files (overwriting encrypted versions)

**⚠️ WARNING**: Decrypted files contain answers. Only run this with proper authorization and secure your decrypted files!

### Manual Encryption (For Re-encryption)

If you need to re-encrypt files:

```bash
python .github/scripts/encrypt_exam_data.py
```

This script:
1. Reads the public key from `encryption.pub`
2. Finds all exam JSON files
3. Encrypts unencrypted sensitive fields
4. Skips already-encrypted data

## File Structure

Encrypted data in JSON files looks like:

```json
{
  "q_id": "phy-001",
  "text": "A ball is thrown vertically upward...",
  "correct_option": {
    "__encrypted__": true,
    "data": "base64-encoded-ciphertext..."
  },
  "explanation": {
    "__encrypted__": true,
    "data": "base64-encoded-ciphertext..."
  }
}
```

Public questions remain unchanged and visible to everyone.

## Security Considerations

1. **Public Key**: Safe to commit. Used only for encryption.
2. **Private Key**: Never commit. Keep it secure.
3. **Encrypted Data**: Can be decrypted only with the private key.
4. **Git History**: If sensitive data was committed unencrypted, it stays in history (use `git filter-branch` or GitHub's secret scanning if this happens).

## Troubleshooting

### GitHub Actions Workflow Failed

Check the workflow logs for:
- `FileNotFoundError: Public key not found` → Ensure `encryption.pub` is in the repo root
- `Invalid PEM format` → Public key file is corrupted

### Decryption Failed

- Ensure you're using the correct private key
- Verify the private key password (if protected)
- Check if the data is actually encrypted (has `__encrypted__` field)

### Re-generate Keys

If you need to change keys:

```bash
# Generate new key pair
openssl genrsa -out encryption.key 2048
openssl rsa -in encryption.key -pubout -out encryption.pub

# Decrypt all files with old key (if you still have it)
python .github/scripts/decrypt_exam_data.py old_encryption.key

# Encrypt with new key
python .github/scripts/encrypt_exam_data.py
```

## API Reference

### Environment Variables

The GitHub Actions workflow uses standard GITHUB_TOKEN for commits.

### File Discovery

The scripts automatically find exam files in:
- `NEET/`
- `JEE/`
- `UPSC/`
- `SSC/`
- `Banking/`
- `Railways/`
- `State-PSC/`

Files like `index.json` and config files are skipped.

## Questions?

For issues or questions about the encryption setup, check:
1. This guide
2. GitHub Actions workflow logs
3. The script comments in `.github/scripts/`
