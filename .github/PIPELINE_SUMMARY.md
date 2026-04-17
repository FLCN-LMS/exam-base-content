# GitHub Pipeline: Exam Data Encryption

## Overview

This setup creates an automated GitHub Actions pipeline that encrypts sensitive exam data (correct answers and explanations) on every merge to `main`, keeping questions public while protecting answers.

## What Was Created

### 1. **GitHub Actions Workflow** (`.github/workflows/encrypt-sensitive-data.yml`)
   - Triggers on: Push to `main` with JSON file changes
   - Runs: Python encryption script
   - Commits: Encrypted files back to repo (with `[skip ci]` tag to avoid loops)
   - Prerequisites: Python 3.11 + cryptography library

### 2. **Encryption Script** (`.github/scripts/encrypt_exam_data.py`)
   - Reads all exam JSON files in category folders
   - Encrypts `correct_option` and `explanation` fields using RSA public key
   - Skips already-encrypted data
   - Uses OAEP padding for security
   - Marks encrypted fields with `"__encrypted__": true`

### 3. **Decryption Script** (`.github/scripts/decrypt_exam_data.py`)
   - For authorized users who have the private key
   - Decrypts exam answers locally
   - Usage: `python decrypt_exam_data.py path/to/encryption.key [password]`
   - Useful for testing or viewing answers with authorization

### 4. **Key Generation Script** (`.github/scripts/generate-keys.sh`)
   - One-command setup: `bash .github/scripts/generate-keys.sh`
   - Generates RSA 2048-bit key pair
   - Creates `encryption.pub` (commit this) and `encryption.key` (never commit)

### 5. **Setup Documentation** (`.github/ENCRYPTION_SETUP.md`)
   - Complete guide to encryption setup
   - Key generation instructions
   - Usage examples
   - Troubleshooting

### 6. **Updated .gitignore**
   - Prevents accidental commit of private key
   - Blocks: `*.key`, `*.pem`, `encryption.key`

## Quick Start

### Step 1: Generate RSA Keys
```bash
bash .github/scripts/generate-keys.sh
```

This creates:
- `encryption.key` - Keep secure, never commit
- `encryption.pub` - Commit to repo

### Step 2: Commit Public Key
```bash
git add encryption.pub
git commit -m "chore: add RSA public key for exam encryption"
git push origin main
```

### Step 3: GitHub Actions Runs Automatically
Once the public key is in the repo, the pipeline will:
1. Trigger on next commit/PR merge to `main`
2. Encrypt all answers and explanations
3. Commit encrypted files back

## Encryption Details

### Encrypted Data Format
```json
{
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

### Encryption Algorithm
- **Algorithm**: RSA 2048-bit
- **Padding**: OAEP (Optimal Asymmetric Encryption Padding)
- **Encoding**: Base64 for JSON compatibility

### Security Features
- ✅ Public key safe to share/commit
- ✅ Private key never exposed
- ✅ Questions remain public
- ✅ Answers protected with strong encryption
- ✅ Automated on every merge
- ✅ Idempotent (safe to run multiple times)

## Supported Categories

The pipeline automatically processes exam files in:
- `NEET/`
- `JEE/`
- `UPSC/`
- `SSC/`
- `Banking/`
- `Railways/`
- `State-PSC/`

Files are discovered recursively within these folders.

## Important Notes

1. **Private Key Security**: Store `encryption.key` securely
   - Use a password manager
   - Never commit to repo
   - Don't share publicly
   - Backup safely

2. **GitHub Actions**: Make sure Settings > Actions > Workflows > Read and Write are enabled

3. **First Run**: The workflow may fail until `encryption.pub` is committed

4. **Manual Usage**: Both scripts can be run locally:
   ```bash
   python .github/scripts/encrypt_exam_data.py
   python .github/scripts/decrypt_exam_data.py path/to/encryption.key
   ```

## Troubleshooting

### "Public key not found"
- Ensure `encryption.pub` is in repo root
- Run `bash .github/scripts/generate-keys.sh`
- Commit and push the public key

### "Permission denied" on scripts
- Run: `chmod +x .github/scripts/*.sh .github/scripts/*.py`

### Decryption not working
- Verify you have the correct private key
- Check if key is password-protected (add password as argument)
- Ensure data is actually encrypted (check for `__encrypted__` field)

### Workflow not triggering
- Check GitHub Actions are enabled in repo settings
- Verify the `.github/workflows/encrypt-sensitive-data.yml` file exists
- Check workflow has correct permissions (read/write)

## File Locations

```
repo/
├── .github/
│   ├── workflows/
│   │   └── encrypt-sensitive-data.yml    (Main workflow)
│   ├── scripts/
│   │   ├── encrypt_exam_data.py          (Encryption)
│   │   ├── decrypt_exam_data.py          (Decryption)
│   │   └── generate-keys.sh              (Key generation)
│   ├── ENCRYPTION_SETUP.md               (Detailed guide)
│   └── PIPELINE_SUMMARY.md               (This file)
├── encryption.pub                         (Public key - COMMIT THIS)
├── encryption.key                         (Private key - NEVER COMMIT)
└── NEET/, JEE/, UPSC/, etc.              (Exam files - auto-processed)
```

## Next Steps

1. ✅ Run key generation script
2. ✅ Commit `encryption.pub` to repo
3. ✅ Push to main branch
4. ✅ GitHub Actions automatically encrypts answers
5. ✅ Store `encryption.key` securely
6. ✅ Share only with authorized team members

Enjoy your secure exam repository! 🔐
