# GitHub Actions Workflow Guide

## Encrypt Sensitive Data Workflow

### Overview
This workflow automatically encrypts sensitive exam data (correct answers and explanations) when changes are pushed to the `main` branch.

### Smart History Management

The workflow uses intelligent logic to manage git history:

#### First Run (Full History Replacement)
- **Trigger**: When commit count > 2 OR last commit is not "Initial commit"
- **Action**: 
  - Creates orphan branch with no history
  - Creates single "Initial commit"
  - Force-pushes to completely clean history
  - ✅ Results in fresh, single-commit repository

#### Subsequent Runs (Normal Updates)
- **Trigger**: After initial cleanup is complete
- **Action**:
  - If last commit was encryption → Amends it with new changes
  - If last commit was different → Creates new encryption commit
  - Normal push (no force)
  - ✅ Maintains clean history without force-push

### How It Works

```
First Time:
  Multiple commits → Full history replacement → Single "Initial commit"
                                                           ↓
Subsequent Times:
  New changes → Check last commit → Amend or create new → Normal push
```

### Key Features

✅ **Automatic Detection** - No manual intervention needed
✅ **Smart Amending** - Replaces previous encryption commit if it was the last one
✅ **Safe Force-Push** - Only used during initial cleanup
✅ **Clean History** - Prevents commit spam from repeated encryptions
✅ **Collaboration-Safe** - Normal push for subsequent commits

### Encryption Details

**What Gets Encrypted:**
- `correct_option` field in each question
- `explanation` field in each question

**What Stays Public:**
- `question` text (the problem itself)
- `options` (answer choices, not marked as correct)
- All metadata

### File Structure

```
Exam JSON:
├── question (public)
├── options (public)
├── correct_option (encrypted)
├── explanation (encrypted)
└── metadata (public)
```

### Manual History Reset (If Needed)

If you want to manually trigger a full history replacement:

```bash
# Force push the current state as a fresh start
git checkout --orphan clean-slate
git commit -m "Initial commit: Fresh exam database"
git branch -D main
git branch -m main
git push origin main --force
```

### Troubleshooting

**Issue**: Workflow keeps doing full history replacement
- **Cause**: Commit count logic might be too aggressive
- **Fix**: Ensure you have at least one "Initial commit" message

**Issue**: Changes not being encrypted
- **Cause**: File paths might not match `**/*.json`
- **Fix**: Check `.github/workflows/encrypt-sensitive-data.yml` paths

**Issue**: Push rejected with "force-with-lease"
- **Cause**: Remote has commits not in local
- **Fix**: Pull latest changes and retry

### Security Notes

🔐 **RSA Encryption:**
- Uses `encryption.pub` (committed to repo)
- Requires `encryption.key` (never commit this!)
- Answers can only be decrypted with private key

📋 **Access Control:**
- Only those with private key can see answers
- Questions remain public (for practice)
- Answers protected from accidental exposure in git history
