# Scripts Directory

This directory contains utility scripts for managing the AI Safety Evaluation Dashboard.

## 📋 Table of Contents

- [Data Setup Scripts](#data-setup-scripts)
- [Data Management Scripts](#data-management-scripts)
- [Deployment Scripts](#deployment-scripts)

---

## Data Setup Scripts

### 🌱 `seed_evaluation_data.py`

**Purpose:** Initialize the database with foundational data for the evaluation system.

**What it does:**
- Creates 3 business types (Airlines, API Support, E-commerce)
- Creates 2 organizations (AirCanada Corp, Pinterest Inc)
- Imports 314 Pinterest scenarios from CSV
- Generates 5 fake AirCanada scenarios
- Skips records that already exist (safe to re-run)

**Usage:**
```bash
python scripts/seed_evaluation_data.py
```

**When to use:** First-time setup or when you need to reset base data.

---

### 📥 `import_precomputed_answers.py`

**Purpose:** Import precomputed bot responses from CSV files for evaluation.

**What it does:**
- Reads Pinterest CSV file with bot responses
- Maps Input → Scenario
- Imports "Output (Round 1)" and "Output (Round 2)" as precomputed answers
- Stores grades from CSV in notes field

**Usage:**
```bash
# Import for default organization (Pinterest Inc)
python scripts/import_precomputed_answers.py

# Import for specific organization
python scripts/import_precomputed_answers.py --org "Pinterest Inc"
```

**Requirements:**
- CSV file must exist: `docs/Ada_Pinterest_ Evaluations round 1, 2 & 3 [EXAMPLE] - Evaluations - round 1 & 2.csv`
- Organizations must exist in database
- Scenarios must be seeded first

---

### 🛩️ `generate_aircanada_answers.py`

**Purpose:** Generate realistic precomputed answers for AirCanada scenarios.

**What it does:**
- Creates fake bot responses for 5 AirCanada scenarios
- Round 1: Unsafe responses (P0, P1, P2, P3 failures)
- Round 2: Safe, improved responses (mostly PASS)
- Demonstrates iterative improvement

**Usage:**
```bash
python scripts/generate_aircanada_answers.py
```

**Output:**
- 10 precomputed answers (5 scenarios × 2 rounds)
- Shows realistic progression from unsafe to safe

---

## Data Management Scripts

### 🎲 `sample_scenarios.py`

**Purpose:** Reduce scenario count while maintaining category diversity.

**What it does:**
- Samples scenarios proportionally across categories
- Reduces dataset from 300+ to target count (default: 100)
- Ensures at least 1 scenario per category
- **Deletes related precomputed answers** to avoid orphaned records

**Usage:**
```bash
# Dry run (see what would be deleted, no changes made)
python scripts/sample_scenarios.py

# With custom business type
python scripts/sample_scenarios.py --business-type-id <uuid>

# Custom target count
python scripts/sample_scenarios.py --target 50

# Actually execute the deletion (BE CAREFUL!)
python scripts/sample_scenarios.py --execute
```

**⚠️ Warning:** This permanently deletes scenarios and their precomputed answers. Always dry run first!

---

### 🧹 `cleanup_precomputed_notes.py`

**Purpose:** Clean up "Grade: " prefix from precomputed answer notes.

**What it does:**
- Finds all precomputed answers with "Grade: " prefix in notes
- Removes prefix, leaving just the grade value (PASS, P0, P1, etc.)
- Shows examples of changes before committing

**Usage:**
```bash
python scripts/cleanup_precomputed_notes.py
```

**Example transformation:**
- `"Grade: PASS"` → `"PASS"`
- `"Grade: P0"` → `"P0"`

---

## Deployment Scripts

### 🚀 `start.sh`

**Purpose:** Start the FastAPI backend server.

**Usage:**
```bash
./scripts/start.sh
```

**What it does:**
- Starts uvicorn server
- Hot reload enabled for development
- Runs on configured host/port

---

### 👥 `start-with-workers.sh`

**Purpose:** Start backend with Celery workers for background tasks.

**Usage:**
```bash
./scripts/start-with-workers.sh
```

**What it does:**
- Starts FastAPI server
- Starts Celery workers for async tasks
- Useful for production or when testing background jobs

---

### 📊 `status.sh`

**Purpose:** Check the status of running services.

**Usage:**
```bash
./scripts/status.sh
```

**What it shows:**
- Running processes
- Service health
- Active workers

---

### 🛑 `stop.sh`

**Purpose:** Stop all running services.

**Usage:**
```bash
./scripts/stop.sh
```

**What it does:**
- Stops FastAPI server
- Stops Celery workers
- Cleans up processes

---

### 🚢 `deploy.sh`

**Purpose:** Deploy application to production.

**Usage:**
```bash
./scripts/deploy.sh
```

**What it does:**
- Runs database migrations
- Builds production assets
- Deploys to configured environment

---

## 🔄 Common Workflows

### Initial Setup
```bash
# 1. Seed base data
python scripts/seed_evaluation_data.py

# 2. Import Pinterest answers from CSV
python scripts/import_precomputed_answers.py

# 3. Generate AirCanada fake answers
python scripts/generate_aircanada_answers.py

# 4. Clean up notes if needed
python scripts/cleanup_precomputed_notes.py
```

### Reduce Dataset Size
```bash
# 1. Dry run to see what will be deleted
python scripts/sample_scenarios.py --target 100

# 2. Review output, then execute
python scripts/sample_scenarios.py --target 100 --execute
```

### Start Development
```bash
# Simple start
./scripts/start.sh

# Or with background workers
./scripts/start-with-workers.sh
```

---

## 📝 Notes

- **All Python scripts** should be run from the `backend/` directory
- **Shell scripts** can be run from anywhere using relative paths
- **Dry run mode** is available for destructive operations (sample_scenarios.py)
- **Idempotency:** Most data scripts are safe to re-run (they skip existing records)

---

## 🆘 Troubleshooting

### "No scenarios found"
→ Run `seed_evaluation_data.py` first

### "No organizations found"
→ Run `seed_evaluation_data.py` first

### "Orphaned precomputed answers"
→ Run `cleanup_precomputed_notes.py` or check foreign key constraints

### "Module not found"
→ Ensure you're in the `backend/` directory when running Python scripts

---

## 🔗 Related Documentation

- Main README: `../README.md`
- API Documentation: `../docs/`
- Database Migrations: `../alembic/versions/`
