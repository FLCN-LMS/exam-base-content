# MongoDB Atlas Setup Guide

## Overview

This project syncs all exam data to MongoDB Atlas automatically via GitHub Actions. Every push to `main` triggers an upsert operation for each exam.

## Quick Setup

### Step 1: Create MongoDB Atlas Account & Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up or log in
3. Create a new cluster (free tier available)
4. Wait for cluster deployment (~10 minutes)

### Step 2: Create Database User

1. In Atlas, go to **Database Access**
2. Click **Add New Database User**
3. Create username and password
4. Grant **Read and Write** permissions
5. **Save credentials securely**

### Step 3: Get Connection String

1. Go to **Database** → **Connect**
2. Select **Drivers** → **Python**
3. Copy the connection string
4. Replace `<username>` and `<password>` with your credentials
5. Example format:
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/exams_db?retryWrites=true&w=majority
   ```

### Step 4: Add to GitHub Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `MONGODB_URI`
5. Value: Your MongoDB connection string (from Step 3)
6. Click **Add secret**

✅ Setup complete! Workflow will run on next push.

## Database Structure

### Collections

#### `categories`
```json
{
  "name": "NEET",
  "title": "National Eligibility cum Entrance Test",
  "description": "Medical entrance examination",
  "is_active": true
}
```

#### `exams`
```json
{
  "exam_id": "neet-2024-mock-1",
  "title": "NEET 2024 Mock Test 1",
  "category": "NEET",
  "year": 2024,
  "sections": [...]
}
```

## Workflow Behavior

### On Every Push

- ✅ Reads all exam JSON files
- ✅ Connects to MongoDB Atlas
- ✅ Performs upsert for each exam (update if exists, create if new)
- ✅ Syncs 7 categories
- ✅ Displays sync summary

### Upsert Operation

- **New exam**: Creates document with all data
- **Existing exam**: Updates all fields with latest data
- **No duplicates**: exam_id is unique key

## Monitoring Sync

### View GitHub Actions Logs

1. Go to **Actions** tab
2. Click **Sync Exams to MongoDB Atlas**
3. View latest run logs
4. Check for ✓ (success) or ✗ (failure)

### View MongoDB Data

1. Go to MongoDB Atlas
2. Click **Database** → **Browse Collections**
3. Navigate to `exams_db` → `exams`
4. View synced exam documents

## Common Issues

### ❌ "MONGODB_URI environment variable not set"
- Verify secret name is exactly `MONGODB_URI`
- Check GitHub Secrets are saved correctly
- Re-run workflow after adding secret

### ❌ "Failed to connect to MongoDB"
- Verify connection string is correct
- Check username and password
- Ensure IP is whitelisted in Atlas (or use 0.0.0.0/0)
- Test connection string locally

### ❌ "Invalid JSON in exam file"
- Check exam JSON files for syntax errors
- Use `python3 -m json.tool filename.json` to validate
- Fix and push again

## Manual Sync

To manually sync exams without pushing:

```bash
# Install pymongo
pip install pymongo

# Set connection string
export MONGODB_URI="mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/exams_db?retryWrites=true&w=majority"

# Run sync script
python .github/scripts/sync-to-mongodb.py
```

## Upsert Strategy

The sync uses MongoDB upsert (update or create):

```python
exams_collection.update_one(
    {"exam_id": exam_id},        # Find by exam_id
    {"$set": exam_data},         # Update all fields
    upsert=True                  # Create if not found
)
```

**Benefits:**
- ✅ No duplicate exams
- ✅ Always synced with latest data
- ✅ Safe to run multiple times
- ✅ No conflicts

## Querying Exams

### Using MongoDB Compass (GUI)

1. Download [MongoDB Compass](https://www.mongodb.com/products/tools/compass)
2. Paste connection string
3. Browse collections and query

### Using Python

```python
from pymongo import MongoClient

client = MongoClient("mongodb+srv://username:password@...")
db = client["exams_db"]
exams = db["exams"].find({"category": "NEET"})

for exam in exams:
    print(exam["title"])
```

### Using Node.js

```javascript
const { MongoClient } = require("mongodb");

const client = new MongoClient("mongodb+srv://username:password@...");
const db = client.db("exams_db");
const exams = db.collection("exams");

exams.find({ category: "NEET" }).forEach(exam => {
  console.log(exam.title);
});
```

## Billing & Limits

### Free Tier (M0)
- ✅ 512 MB storage
- ✅ Shared resources
- ✅ Good for testing
- ✅ Always free

### Paid Tiers
- Start at ~$0.10/month
- More storage and performance
- Dedicated clusters available

## Backup & Recovery

### Enable Automatic Backups

1. Go to **Database** → **Backup**
2. Enable **Automated Backups**
3. Set retention period (default: 7 days)

### Restore from Backup

1. Go to **Backup** → **Restore**
2. Select backup timestamp
3. Choose restore destination
4. MongoDB handles the rest

## Security Best Practices

- ✅ Never commit connection string to git
- ✅ Use GitHub Secrets for credentials
- ✅ Create separate users for different apps
- ✅ Use strong passwords
- ✅ Enable IP whitelisting (if possible)
- ✅ Rotate passwords periodically
- ✅ Use Network Access configuration

## Next Steps

1. ✅ Create MongoDB Atlas cluster
2. ✅ Create database user
3. ✅ Get connection string
4. ✅ Add to GitHub Secrets
5. ✅ Push code to trigger sync
6. ✅ Verify data in MongoDB
7. ✅ Query and use in applications

📖 **MongoDB Docs**: https://docs.mongodb.com/
📖 **Atlas Docs**: https://docs.atlas.mongodb.com/
