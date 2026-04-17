# Quick Start: Encryption System Setup

## 5-Minute Setup

### Step 1: Generate RSA Keys
```bash
bash .github/scripts/generate-keys.sh
```

This creates:
- `encryption.key` - Private key (KEEP SECURE!)
- `encryption.pub` - Public key (safe to commit)

### Step 2: Add Public Key to Repository
```bash
git add encryption.pub
git commit -m "chore: add RSA public key for exam encryption"
git push
```

### Step 3: Secure Private Key
```bash
# Store safely (never commit!)
# Options:
# - 1Password / LastPass vault
# - Environment variable (for CI/CD)
# - Secure hardware device
# - Team secure storage

# Make sure it's not accidentally committed
echo "encryption.key" >> .gitignore
```

### Step 4: Test the Setup (Optional)
```bash
python .github/scripts/test-encryption.py
```

✅ Setup Complete!

## How It Works

### On First Push:
1. Push exam JSON files to `main`
2. GitHub Actions automatically triggers
3. Encryption workflow:
   - ✅ Reads `encryption.pub`
   - ✅ Encrypts all answers & explanations
   - ✅ Replaces entire git history (first run only)
   - ✅ Creates fresh "Initial commit"

### On Future Pushes:
1. Push new exam files
2. Workflow automatically:
   - ✅ Encrypts new data
   - ✅ Uses normal commits (no force push)
   - ✅ Keeps history clean

## File Locations

```
project-root/
├── encryption.pub ← PUBLIC (commit this)
├── encryption.key ← PRIVATE (never commit)
├── .github/
│   ├── scripts/
│   │   ├── encrypt_exam_data.py
│   │   ├── decrypt_exam_data.py
│   │   └── generate-keys.sh
│   └── workflows/
│       └── encrypt-sensitive-data.yml
└── [exam folders]/
    ├── NEET/
    ├── JEE/
    ├── UPSC/
    └── ...
```

## Common Tasks

### ✅ Add New Exams
```bash
# 1. Create exam JSON file
# 2. Include plain-text answers
# 3. Push to main
# 4. Workflow auto-encrypts
# 5. Answers encrypted automatically ✓
```

### 🔓 Decrypt Answers (Authorized Only)
```bash
python .github/scripts/decrypt_exam_data.py /path/to/encryption.key

# All exams now have decrypted answers
# ⚠️ Keep secure!
```

### 🔄 Regenerate Keys
```bash
# If keys are compromised:
bash .github/scripts/generate-keys.sh  # New keys
git add encryption.pub
git commit -m "chore: rotate encryption keys"
git push

# Old encrypted data becomes unreadable with old key
# Re-encrypt with new key by pushing exams again
```

### 🧪 Test Encryption
```bash
python .github/scripts/test-encryption.py

# Output:
# ✓ Public key valid
# ✓ Encryption working
# ✓ Sample data encrypted successfully
```

## Workflow Triggers

The encryption workflow automatically runs when:
- ✅ JSON files pushed to `main` branch
- ✅ Workflow file itself is modified

The workflow:
- ⏭️ Skips if no JSON changes detected
- ⏸️ Runs parallel with other CI/CD
- ⚡ Completes in < 30 seconds

## First Run: History Replacement

On first push with exams:

```
Before:
  - Multiple commits with various changes
  - Some commits might have unencrypted data

After:
  - Single "Initial commit" with everything encrypted
  - All previous history removed
  - Git log: clean and fresh
  - No unencrypted answers in history ✓
```

This is safe because:
- ✅ Only happens once (automatically detected)
- ✅ Uses `--force` only on first run
- ✅ All data preserved in new commit
- ✅ No data loss

## Subsequent Runs: Normal Updates

After first run:

```
New exams → Encrypt → Normal commit → Push
            ↓
     Workflow auto-amends if last commit was encryption
     Otherwise creates new commit
```

## Security Checklist

- [ ] Generated RSA key pair
- [ ] `encryption.pub` committed to git
- [ ] `encryption.key` NOT in git (check .gitignore)
- [ ] Private key stored securely
- [ ] Team members informed of encryption setup
- [ ] Test decryption with authorized key
- [ ] Backup of private key created
- [ ] Workflow runs without errors

## Troubleshooting

### Q: "Public key not found" error
**A**: Public key missing from repo
```bash
bash .github/scripts/generate-keys.sh
git add encryption.pub
git push
```

### Q: Workflow keeps replacing history
**A**: Workflow still detecting old commits
```bash
# Manually verify:
git log --oneline
# Should show: 1 "Initial commit: Exam base content..."
```

### Q: Can't decrypt old exams
**A**: Using wrong private key
```bash
# Verify key:
openssl rsa -in encryption.key -text -noout

# Test with test script:
python .github/scripts/test-encryption.py
```

### Q: Want to disable encryption temporarily
**A**: Rename or disable workflow file
```bash
# Temporarily:
mv .github/workflows/encrypt-sensitive-data.yml \
   .github/workflows/encrypt-sensitive-data.yml.bak

# Re-enable:
mv .github/workflows/encrypt-sensitive-data.yml.bak \
   .github/workflows/encrypt-sensitive-data.yml
```

## What Gets Encrypted?

✅ **Encrypted** (Hidden):
- Correct answers
- Explanations

✅ **Public** (Visible):
- Question text
- Multiple choice options
- Marks awarded
- Negative marks
- Question metadata
- All category/exam info

## Performance

- ⚡ Encryption: < 10 seconds
- ⚡ Workflow total: < 30 seconds
- 💾 Storage impact: Minimal (base64 encoding ~33% overhead)
- 🚀 No performance impact on users

## Next Steps

1. ✅ Set up keys
2. ✅ Add public key to repo
3. ✅ Secure private key
4. ✅ Push exam files
5. ✅ Watch workflow run automatically
6. ✅ Verify encryption in GitHub

📖 **Detailed Docs**: See [ENCRYPTION_GUIDE.md](./ENCRYPTION_GUIDE.md)
📖 **Workflow Info**: See [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md)

Questions? Check the detailed guides above! 🚀
