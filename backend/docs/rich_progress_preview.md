# 🎨 Rich Console Progress - Visual Preview

## What It Looks Like

### 1. Header Panel (Start)
```
┏━━━━━━━━━━━━━━ Starting Evaluation ━━━━━━━━━━━━━━━┓
┃                                                   ┃
┃  🛡️  AI Safety Evaluation - Round 1              ┃
┃  Organization: Demo Company Inc                   ┃
┃  Business Type: API Developer Support             ┃
┃  Test Scenarios: 309                              ┃
┃  Judges: Claude Sonnet 4.5, GPT-5, Grok-4 Fast   ┃
┃                                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 2. Progress Bar (Running)
```
⠋ Evaluating scenarios... ━━━━━━━━━╸━━━━━━━━━━━━━━━━━━ 150/309 • SelfHarm • 0:01:23
```

**Features:**
- 🌀 Animated spinner
- 📊 Visual progress bar with colors
- 🔢 Count display (150/309)
- 🏷️ Current category being tested
- ⏱️ Elapsed time

### 3. Results Summary Table (Complete)
```
              📊 Evaluation Results              
┏━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┓
┃ Grade ┃ Count ┃ Percentage ┃ Emoji ┃
┡━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━┩
│ PASS  │   245 │      79.3% │   ✅  │
│ P4    │    32 │      10.4% │   ⚠️  │
│ P3    │    18 │       5.8% │   🟠  │
│ P2    │    14 │       4.5% │   🔴  │
└───────┴───────┴────────────┴───────┘
```

### 4. Pass Rate Panel (Complete)
```
┏━━━━━━━━━ ✨ Pass Rate ━━━━━━━━━┓
┃                                ┃
┃      79.3% (245/309 tests)     ┃
┃                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Color Coding:**
- 🟢 Green: ≥90% pass rate
- 🟡 Yellow: 70-89% pass rate
- 🔴 Red: <70% pass rate

---

## API Mode vs Notebook Mode

### API Mode (show_progress=False)
```
# FastAPI endpoints - no visual output
orchestrator = EvaluationOrchestrator(db, show_progress=False)
# Runs silently, logs to file
```

### Notebook/CLI Mode (show_progress=True)
```python
# Jupyter notebooks or CLI scripts - rich visual output
orchestrator = EvaluationOrchestrator(db, show_progress=True)

# Output:
# ┏━━━━━━━━━━━━━━ Starting Evaluation ━━━━━━━━━━━━━━┓
# ⠋ Evaluating scenarios... ━━━━╸━━━━━━━━━━ 150/309 • ...
# ┏━━━━━━━━━ Results ━━━━━━━━━┓
```

---

## Examples

### Example 1: High Pass Rate (97.4%)
```
┏━━━━━━━━━ ✨ Pass Rate ━━━━━━━━━┓
┃                                ┃
┃     97.4% (301/309 tests)      ┃  ← Green (excellent!)
┃                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Grade Distribution:
✅ PASS: 301 (97.4%)
⚠️ P4:    8 (2.6%)
```

### Example 2: Low Pass Rate (42.1%)
```
┏━━━━━━━━━ ✨ Pass Rate ━━━━━━━━━┓
┃                                ┃
┃     42.1% (130/309 tests)      ┃  ← Red (needs work!)
┃                                ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Grade Distribution:
✅ PASS: 130 (42.1%)
⚠️ P4:   45 (14.6%)
🟠 P3:   67 (21.7%)
🔴 P2:   42 (13.6%)
🚨 P1:   18 (5.8%)
☢️ P0:    7 (2.3%)
```

---

## Try It Yourself

```bash
# Run demo with rich progress
python backend/examples/rich_progress_demo.py rich

# Run demo in silent mode (API)
python backend/examples/rich_progress_demo.py silent
```

Or in a Jupyter notebook:
```python
from app.services.evaluation_orchestrator import EvaluationOrchestrator

# Enable rich progress for notebooks!
orchestrator = EvaluationOrchestrator(db, show_progress=True)
round_id = await orchestrator.run_evaluation_round(
    organization_id="...",
    round_number=1
)
```
