# Encryption System Guide

## Overview

This project uses **RSA-2048 encryption** to protect sensitive exam data (correct answers and explanations) while keeping questions public.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions Workflow (on main branch push)          │
├─────────────────────────────────────────────────────────┤
│  1. Checkout code                                       │
│  2. Run encryption script (encrypt_exam_data.py)        │
│  3. Smart history management:                           │
│     ├─ First run → Full history replacement             │
│     └─ Subsequent runs → Normal commits                 │
│  4. Push encrypted data to main                         │
│  5. Display summary report                              │
└─────────────────────────────────────────────────────────┘
```

## Files

### Scripts
- **`encrypt_exam_data.py`** - Encrypts all exam files
- **`decrypt_exam_data.py`** - Decrypts exam data (for authorized users)
- **`generate-keys.sh`** - Generates RSA key pair
- **`test-encryption.py`** - Tests encryption setup

### Keys
- **`encryption.pub`** - Public key (safe to commit)
- **`encryption.key`** - Private key (NEVER commit)

### Workflow
- **`.github/workflows/encrypt-sensitive-data.yml`** - GitHub Actions automation

## How Encryption Works

### On Push to Main:

1. **Detect Changes** - Check if JSON files changed
2. **Load Public Key** - Read `encryption.pub`
3. **Find Exam Files** - Locate all exam JSON files
4. **Encrypt Sensitive Fields**:
   ```json
   {
     "q_id": "phy-001",
     "text": "Question text here",  // ← PUBLIC
     "options": {...},             // ← PUBLIC
     "correct_option": {           // ← ENCRYPTED
       "__encrypted__": true,
       "data": "base64-encoded-ciphertext..."
     },
     "explanation": {              // ← ENCRYPTED
       "__encrypted__": true,
       "data": "base64-encoded-ciphertext..."
     }
   }
   ```

5. **Smart Commit Logic**:
   ```
   if first run (commit count > 2):
     → Full history replacement
     → Single "Initial commit"
     → Force push
   else:
     → Normal encryption commit
     → Standard push
   ```

### First Run Example:
```
Before: 15 commits with various changes
After:  1 commit with all encrypted data
Result: Clean, fresh repository
```

### Subsequent Runs Example:
```
Before: 1 Initial commit
Push new exams → Encrypt → Amend last commit or create new one
After:  1-2 commits (clean history maintained)
```

## Encryption Details

### Algorithm
- **Type**: RSA-2048
- **Padding**: OAEP with SHA256
- **Encoding**: Base64

### Key Generation
```bash
# Generate private key
openssl genrsa -out encryption.key 2048

# Extract public key
openssl rsa -in encryption.key -pubout -out encryption.pub

# Secure the private key (NEVER commit!)
chmod 600 encryption.key
```

### What Gets Encrypted
✅ `correct_option` - The correct answer
✅ `explanation` - Answer explanation

### What Stays Public
✅ `q_id` - Question ID
✅ `text` - Question text
✅ `options` - Multiple choice options
✅ `marks` - Marks for question
✅ `negative_marks` - Negative marks
✅ All metadata

## Decryption (For Authorized Users)

```bash
# Basic decryption
python .github/scripts/decrypt_exam_data.py path/to/encryption.key

# With password-protected key
python .github/scripts/decrypt_exam_data.py path/to/encryption.key "your-password"
```

## Workflow Reports

After each successful push, the workflow displays:

```
═══════════════════════════════════════════════════════════
  📊 ENCRYPTION WORKFLOW SUMMARY
═══════════════════════════════════════════════════════════

✅ Status: SUCCESS

🔄 Mode: HISTORY REPLACED (Fresh Start)
   - All previous commits removed
   - Single 'Initial commit' created
   - Repository history cleaned

📈 Repository Stats:
   - Total Commits: 1
   - Latest Commit: abc1234 - Initial commit...
   - Timestamp: 2026-04-17T16:31:23Z

🔐 Encryption:
   - Algorithm: RSA-2048
   - Fields Encrypted: correct_option, explanation
   - Public Key: encryption.pub

═══════════════════════════════════════════════════════════
```

## Workflow Modes

### Mode 1: History Replacement (First Run)
**Trigger**: Commit count > 2 OR last commit is not "Initial commit"

**Actions**:
1. Creates orphan branch (no history)
2. Creates "Initial commit" with all encrypted data
3. Force-pushes to replace entire history
4. Results in fresh, clean repository

**When to Use**: During initial setup or when cleanup needed

### Mode 2: Normal Updates (Subsequent Runs)
**Trigger**: After history replacement is complete

**Actions**:
1. Encrypts new/updated exam data
2. Amends last commit if it was encryption commit
3. Creates new commit if last was different
4. Standard push (no force)

**When to Use**: Regular exam updates

## Safety Features

✅ **RSA Encryption** - Industry standard security
✅ **Selective Encryption** - Only sensitive fields encrypted
✅ **Public Key in Repo** - Safe to commit
✅ **Private Key Separation** - Never committed
✅ **Safe Force-Push** - Only during initial cleanup
✅ **Automatic Detection** - No manual configuration needed
✅ **Conditional Commits** - Only when data changes
✅ **Skip CI** - Prevents triggering other workflows

## Troubleshooting

### ❌ "Public key not found"
```bash
# Generate keys if missing
bash .github/scripts/generate-keys.sh
git add encryption.pub
git commit -m "chore: add RSA public key"
git push
```

### ❌ "Invalid PEM format"
- Check `encryption.pub` is valid PEM format
- Regenerate if corrupted

### ❌ Workflow keeps replacing history
- Ensure exactly 1 commit exists after first run
- Check last commit message contains "Initial commit"

### ❌ Decryption fails
- Verify using correct private key
- Check key isn't password-protected (if no pwd provided)
- Ensure data is actually encrypted (`__encrypted__: true`)

## Best Practices

1. **Private Key Management**:
   - Store in secure vault (1Password, LastPass, etc.)
   - Never commit to git
   - Share only with authorized team members
   - Rotate periodically

2. **Public Key Management**:
   - Safe to commit
   - Distribute with repository
   - Only for encryption, not decryption

3. **Workflow Monitoring**:
   - Check GitHub Actions logs after each push
   - Verify encryption summary report
   - Alert on failures

4. **Data Integrity**:
   - Keep backup of decrypted answers
   - Test encryption setup before production
   - Verify encrypted data structure

## Security Considerations

🔐 **Strong Points**:
- RSA-2048 (2048-bit key) is industry standard
- OAEP padding prevents known-plaintext attacks
- SHA256 hashing ensures integrity
- Public key separation from private key

⚠️ **Important Notes**:
- Private key loss = permanent data loss (no recovery)
- Encrypted data is only as secure as private key
- GitHub history after first push contains no unencrypted answers
- Force-push during first run rewrites history (use with caution)

## Integration with Decryption

Authorized users can decrypt locally:

```bash
# Decrypt all files
python .github/scripts/decrypt_exam_data.py /path/to/encryption.key

# Results saved as decrypted JSON files
# ⚠️ Handle decrypted files securely - they contain answers!
```

## References

- Cryptography Library: https://cryptography.io/
- RSA Encryption: https://en.wikipedia.org/wiki/RSA_(cryptosystem)
- GitHub Actions: https://docs.github.com/en/actions
