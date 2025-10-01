# 📓 AI Safety Evaluation Notebooks

Interactive Jupyter notebooks for learning and using the AI Safety Evaluation Platform.

## 📚 Available Notebooks

### 🛡️ `ai_safety_evaluation_walkthrough.ipynb`

**Complete end-to-end tutorial** showing:

1. **Setup** - Configure environment & database
2. **Organizations** - Create and manage test subjects
3. **Business Types** - Explore industry templates
4. **Scenarios** - Retrieve test scenarios  
5. **Evaluation** - Run multi-judge LLM evaluations
6. **Results** - Analyze outcomes & statistics
7. **Certification** - Check AIUC-1 eligibility

## 🚀 Getting Started

### Prerequisites

```bash
# Install Jupyter
pip install jupyter notebook

# Or use JupyterLab
pip install jupyterlab
```

### Running Notebooks

```bash
# From backend directory
cd backend

# Start Jupyter
jupyter notebook notebooks/

# Or JupyterLab
jupyter lab notebooks/
```

### Database Setup

Make sure your database is running and seeded:

```bash
# Run migrations
alembic upgrade head

# Seed data
python scripts/seed_evaluation_data.py
```

### Environment Variables

Create `.env` file with OpenRouter keys:

```bash
# For running actual evaluations
CLAUDE_SONNET_4_API_KEY=your_key_here
GPT_5_API_KEY=your_key_here
GROK_4_FAST_API_KEY=your_key_here
```

## ⚠️ Important Notes

### API Costs

- **Demo Mode**: Most cells are safe to run (read-only)
- **Evaluation Cells**: Commented out by default (costs money!)
- Look for `⚠️ COSTS MONEY` warnings before uncommenting

### Clean Output

When running evaluations with `show_progress=True`, logs are automatically suppressed to keep the rich progress display clean. Only WARNING and ERROR logs will appear.

### Evaluation Tips

1. **Start Small**: Test with 3-5 scenarios first
2. **Check API Keys**: Ensure OpenRouter keys are configured
3. **Monitor Costs**: Each scenario = 3 judge API calls
4. **Use Existing Data**: Load previous evaluation results for analysis

## 📊 What You'll Learn

### Workflow Overview

```
Create Org → Select Business Type → Load Scenarios
     ↓
Run 3 Judge Evaluation (Claude, GPT-5, Grok)
     ↓
Analyze Results → Check Certification → Iterate
```

### Key Concepts

- **Multi-Judge System**: 3 parallel LLM evaluations
- **Severity Grading**: PASS, P4, P3, P2, P1, P0
- **Majority Voting**: 2/3 judges must agree
- **AIUC-1 Certification**: 100% pass rate requirement
- **Iterative Improvement**: Track progress across rounds

## 🎯 Use Cases

### 1. Learning the Platform

Run through the walkthrough notebook to understand:
- How evaluations work
- What scenarios look like
- How judges grade responses
- Certification requirements

### 2. Testing Your AI Agent

Integrate your agent by:
1. Modifying `_simulate_system_response()` in orchestrator
2. Calling your actual API/system
3. Running evaluations against real scenarios

### 3. Analyzing Results

Explore evaluation data:
- Pass rate trends across rounds
- Severity distribution by category
- Judge agreement patterns
- Failure analysis

### 4. Achieving Certification

Work towards AIUC-1:
1. Run initial evaluation
2. Identify failure patterns
3. Fix agent issues
4. Iterate until 100% pass rate

## 📖 Additional Resources

- **API Docs**: `backend/docs/api_endpoints.md`
- **Technical Approach**: `backend/docs/backend_llm_approach.md`
- **Orchestrator Guide**: `backend/docs/evaluation_orchestrator.md`
- **Steps Guide**: `backend/docs/steps.md`

## 🤝 Contributing

Have ideas for new notebooks? Create:
- Analysis notebooks (visualizations, trends)
- Integration examples (specific AI platforms)
- Advanced workflows (batch processing, A/B testing)

---

*Built with ❤️ for AI Safety*
