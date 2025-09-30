# AI Safety Evaluation Dashboard - Frontend Specification

## 🎯 User Story

**As an enterprise Head of Customer Support** (not an AI expert), **I want to know that the Customer Support AI agent I'm considering buying won't create an AirCanada disaster** so I can convince my security team to unblock the purchase and sleep comfortably at night.

**Reference**: [AirCanada incident](https://www.bbc.com/travel/article/20240222-air-canada-chatbot-misinformation-what-travellers-should-know)

---

## 📋 Product Vision

### Core Value Proposition
Build confidence infrastructure for AI agent adoption through:
1. **Incident Mapping** - Ground truth from real-world failures
2. **Prevention Standards** - AIUC-1 compliance framework
3. **Comprehensive Testing** - Multi-round red-teaming evaluations
4. **Confidence Visualization** - Progress dashboards for buyers

### Target User Journey (from `visualization_eval.md`)

**User**: Head of Customer Experience at Fortune 1000 company

**Journey Flow**:
1. 🔗 Receives link to `evals.ada.cx` from vendor
2. 🛡️ Sees AIUC-1 SOC 2 framework - builds trust
3. 🏢 Sees tests run on similar company (e.g., large retailer)
4. 📊 Sees 10,000+ evaluations with real examples
5. 🔍 Understands methodology: Incident → Harm → Tactic → Use Case → Context
6. 📈 Sees improvement trajectory: 77.9% → 94.1% → 97.4%
7. 🎯 Explores interactive test taxonomy
8. ✅ Feels comprehensive, cohesive, and relevant
9. 📥 Requests detailed results for security team

---

## 🏗️ Architecture Overview

### Tech Stack
- **Framework**: Next.js 14 (App Router)
- **UI Components**: shadcn/ui + Tailwind CSS
- **Charts**: Recharts + Plotly.js (for interactive visualizations)
- **State Management**: React Context + TanStack Query (React Query)
- **API Client**: Axios with custom hooks
- **Authentication**: Clerk (optional for admin access)
- **TypeScript**: Strict mode for type safety

### Project Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx           # Landing page
│   │   ├── dashboard/         # Main dashboard
│   │   ├── evaluations/       # Evaluation runs
│   │   ├── taxonomy/          # Test taxonomy explorer
│   │   └── reports/           # Exportable reports
│   ├── components/
│   │   ├── evaluation/        # Evaluation-specific components
│   │   ├── charts/            # Reusable chart components
│   │   ├── ui/                # shadcn/ui components
│   │   └── layout/            # Layout components
│   ├── lib/
│   │   ├── api/               # API client & hooks
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utilities
│   └── hooks/                 # Custom React hooks
└── public/                    # Static assets
```

---

## 🎨 Key Features & Pages

### 1. Landing Page (`/`)
**Purpose**: Public-facing trust center

**Sections**:
- **Hero**: AIUC-1 Certified badge, key metrics (pass rate, tests run)
- **Social Proof**: "Trusted by Fortune 1000 companies"
- **Methodology**: Visual flow (Incident → Prevention → Testing → Confidence)
- **Live Demo**: Interactive mini-dashboard
- **CTA**: "Request Full Report" for enterprise buyers

**Key Elements**:
```typescript
interface LandingPageMetrics {
  totalTests: number;           // e.g., 10,000+
  passRate: number;              // e.g., 97.4%
  aiucCertified: boolean;        // AIUC-1 badge
  incidentsCovered: number;      // e.g., 50+ real incidents
  businessTypes: string[];       // ["Retail", "Airlines", "Tech"]
}
```

---

### 2. Main Dashboard (`/dashboard`)
**Purpose**: Interactive evaluation visualization

**Layout**:
```
┌─────────────────────────────────────────────┐
│  Header: Organization | Business Type       │
├─────────────────────────────────────────────┤
│  KPI Cards:                                 │
│  [Pass Rate] [Total Tests] [Severity P0-P4] │
├─────────────────────────────────────────────┤
│  Round Selector: [Round 1 ▼] [Round 2 ▼]   │
├─────────────────────────────────────────────┤
│  ┌──────────────┐  ┌───────────────────┐   │
│  │ Pass Rate    │  │ Severity Heatmap  │   │
│  │ Comparison   │  │                   │   │
│  │ (Bar Chart)  │  │  (Stacked Bars)   │   │
│  └──────────────┘  └───────────────────┘   │
├─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐  │
│  │ Improvement Trajectory (Line Chart)   │  │
│  │ 77.9% → 94.1% → 97.4%                │  │
│  └──────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│  Failed Tests Table (P0-P4)                 │
│  [Category] [Severity] [Judge Consensus]    │
└─────────────────────────────────────────────┘
```

**Key Components**:
- `<RoundSelector>` - Dropdown to select evaluation rounds
- `<PassRateChart>` - Bar chart comparing rounds
- `<SeverityHeatmap>` - Stacked bar chart (P0-P4)
- `<ImprovementTrajectory>` - Line chart with target line at 100%
- `<FailedTestsTable>` - Filterable table of issues

---

### 3. Evaluation Runner (`/evaluations/run`)
**Purpose**: Start new evaluation rounds

**Flow**:
```
1. Select Organization → Select Business Type
2. Configure Round:
   - Round Number (auto-incremented)
   - Description (optional)
   - Use Fake Judges (toggle for demo)
3. Click "Start Evaluation"
4. Real-time Progress:
   ┌─────────────────────────────────┐
   │ 🛡️ Running Safety Evaluation... │
   │ Progress: ████████░░ 78/100     │
   │ Current: SelfHarm category      │
   │ Time Elapsed: 00:02:34          │
   └─────────────────────────────────┘
5. Show Results → Redirect to Dashboard
```

**API Integration**:
```typescript
// POST /api/v1/evaluations/run
interface StartEvaluationRequest {
  organization_id: string;
  round_number: number;
  description?: string;
  use_fake_judges?: boolean;
}

interface StartEvaluationResponse {
  round_id: string;
  status: "running" | "completed";
  total_scenarios: number;
}

// GET /api/v1/evaluations/{round_id}/progress (SSE or polling)
interface EvaluationProgress {
  round_id: string;
  completed: number;
  total: number;
  current_category: string;
  status: "running" | "completed" | "failed";
}
```

---

### 4. Test Taxonomy Explorer (`/taxonomy`)
**Purpose**: Interactive exploration of test coverage

**Features**:
- **Tag Cloud**: Click tags to filter (e.g., "Jailbreaks", "Hallucinations", "Data Leakage")
- **Category Tree**: Expandable hierarchy
  ```
  📁 SelfHarm (50 tests)
    ├── 📄 General self-harm (30)
    ├── 📄 Suicide ideation (15)
    └── 📄 Self-injury (5)
  📁 Fraud (80 tests)
    ├── 📄 Refund fraud (40)
    └── 📄 Identity theft (40)
  ```
- **Sample Prompts**: Show real test examples
- **Incident Mapping**: Link to real-world incidents (e.g., AirCanada)
- **Research Links**: Papers and methodologies

**Data Structure**:
```typescript
interface TaxonomyCategory {
  category: string;
  sub_categories: {
    name: string;
    count: number;
    sample_prompts: string[];
    incident_reference?: string;
  }[];
  total_tests: number;
  tactics: string[];
  research_links?: string[];
}
```

---

### 5. Round Comparison View (`/dashboard/compare`)
**Purpose**: Side-by-side round analysis

**Layout**:
```
┌─────────────────────────────────────────────┐
│  Round Comparison: Round 1 vs Round 2      │
├─────────────────────────────────────────────┤
│  Metric          Round 1    Round 2    Δ   │
│  ─────────────────────────────────────────  │
│  Pass Rate       77.9%      94.1%     +16.2%│
│  P0 Errors       1           0         -1   │
│  P1 Errors       2           0         -2   │
│  P2 Errors       5           2         -3   │
│  Total Failed    45          18        -27  │
├─────────────────────────────────────────────┤
│  🔍 Improvements Breakdown:                 │
│  ✅ Fixed SelfHarm issues (P0 → PASS)      │
│  ✅ Improved Refund Fraud (P2 → P4)        │
│  ⚠️  Still 2 P2 issues in Data Leakage      │
├─────────────────────────────────────────────┤
│  [Export Comparison Report (PDF)]           │
└─────────────────────────────────────────────┘
```

---

### 6. Certification Status (`/certification`)
**Purpose**: AIUC-1 eligibility check

**Visual Design**:
```
┌─────────────────────────────────────────────┐
│  🏆 AIUC-1 Certification Status             │
├─────────────────────────────────────────────┤
│  ✅ ELIGIBLE for AIUC-1                     │
│                                             │
│  Requirements:                              │
│  ✅ Zero P0 Errors ✓                        │
│  ✅ Zero P1 Errors ✓                        │
│  ✅ Zero P2 Errors ✓                        │
│  ✅ Zero P3 Errors ✓                        │
│  ✅ Zero P4 Errors ✓                        │
│  ✅ Pass Rate: 100%                         │
│                                             │
│  [Download Certificate] [Share Badge]       │
└─────────────────────────────────────────────┘
```

**If NOT eligible**:
```
❌ NOT ELIGIBLE for AIUC-1

Remaining Issues:
• 2 P2 Errors (Data Leakage)
• 5 P3 Errors (Policy Violation)

📋 Next Steps:
1. Review failed test details
2. Update agent safety guardrails
3. Run Round 3 evaluation
4. Verify improvements
```

---

## 📊 Chart Components

### 1. Pass Rate Comparison Chart
**Library**: Recharts (Bar Chart)
```typescript
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={[
    { round: 'Round 1', passRate: 77.9, color: '#ef4444' },
    { round: 'Round 2', passRate: 94.1, color: '#10b981' }
  ]}>
    <Bar dataKey="passRate" fill="color" />
    <ReferenceLine y={100} stroke="#6366f1" strokeDasharray="3 3" />
  </BarChart>
</ResponsiveContainer>
```

### 2. Severity Distribution (Stacked Bar)
```typescript
<BarChart data={rounds}>
  <Bar dataKey="P0" stackId="a" fill="#7f1d1d" />
  <Bar dataKey="P1" stackId="a" fill="#dc2626" />
  <Bar dataKey="P2" stackId="a" fill="#f59e0b" />
  <Bar dataKey="P3" stackId="a" fill="#f97316" />
  <Bar dataKey="P4" stackId="a" fill="#fbbf24" />
  <Bar dataKey="PASS" stackId="a" fill="#10b981" />
</BarChart>
```

### 3. Improvement Trajectory (Line)
```typescript
<LineChart data={allRounds}>
  <Line 
    type="monotone" 
    dataKey="passRate" 
    stroke="#10b981" 
    strokeWidth={3}
    dot={{ r: 6 }}
  />
  <ReferenceLine y={100} label="Target" stroke="#6366f1" />
</LineChart>
```

### 4. Interactive Plotly Charts (Advanced)
For more complex visualizations, use Plotly.js:
- 3D severity heatmaps
- Sankey diagrams (Incident → Category → Severity)
- Parallel coordinates for multi-dimensional analysis

---

## 🔌 API Integration

### Backend Endpoints (from FastAPI)
```typescript
// Evaluation Endpoints
GET    /api/v1/evaluations/rounds/{round_id}
GET    /api/v1/evaluations/rounds/{round_id}/statistics
POST   /api/v1/evaluations/run
GET    /api/v1/evaluations/organizations/{org_id}/rounds

// Results Endpoints
GET    /api/v1/results/{round_id}
GET    /api/v1/results/{round_id}/failed
GET    /api/v1/results/compare?round1={id}&round2={id}

// Taxonomy Endpoints
GET    /api/v1/taxonomy/categories
GET    /api/v1/taxonomy/scenarios?category={cat}

// Certification Endpoints
GET    /api/v1/certification/check/{round_id}
POST   /api/v1/certification/issue
```

### Custom Hooks
```typescript
// useEvaluationRound.ts
export function useEvaluationRound(roundId: string) {
  return useQuery({
    queryKey: ['evaluation', roundId],
    queryFn: () => api.getEvaluationRound(roundId)
  });
}

// useRoundComparison.ts
export function useRoundComparison(round1: string, round2: string) {
  return useQuery({
    queryKey: ['comparison', round1, round2],
    queryFn: () => api.compareRounds(round1, round2)
  });
}

// useRunEvaluation.ts
export function useRunEvaluation() {
  return useMutation({
    mutationFn: (params: StartEvaluationRequest) => 
      api.startEvaluation(params),
    onSuccess: (data) => {
      queryClient.invalidateQueries(['evaluations']);
    }
  });
}
```

---

## 🎨 Design System

### Color Palette (Severity-based)
```css
--pass: #10b981;      /* Green */
--p4-trivial: #fbbf24; /* Yellow */
--p3-moderate: #f97316; /* Orange */
--p2-serious: #f59e0b;  /* Amber */
--p1-critical: #dc2626; /* Red */
--p0-catastrophic: #7f1d1d; /* Dark Red */
--aiuc-brand: #6366f1;  /* Indigo */
```

### Typography
- **Headings**: Inter (system-ui fallback)
- **Body**: Inter
- **Mono**: JetBrains Mono (for code samples)

### Key UI Patterns
- **Security-first Design**: Professional, technical feel
- **Trust Signals**: Badges, certifications, third-party logos
- **Data Density**: Information-rich but scannable
- **Progressive Disclosure**: Simple → Detailed on demand

---

## 🚀 Implementation Roadmap

### Phase 1: Core Dashboard (Week 1-2)
- [ ] Setup Next.js 14 + TypeScript + Tailwind
- [ ] API client with React Query
- [ ] Basic dashboard layout
- [ ] Pass rate comparison chart
- [ ] Round selector component

### Phase 2: Evaluation Runner (Week 2-3)
- [ ] Evaluation configuration UI
- [ ] Real-time progress tracking
- [ ] Results display
- [ ] Error handling

### Phase 3: Advanced Visualizations (Week 3-4)
- [ ] Plotly integration
- [ ] Severity heatmaps
- [ ] Improvement trajectory charts
- [ ] Interactive filtering

### Phase 4: Taxonomy Explorer (Week 4-5)
- [ ] Category tree component
- [ ] Tag cloud with filtering
- [ ] Sample prompt viewer
- [ ] Incident mapping

### Phase 5: Reports & Certification (Week 5-6)
- [ ] PDF export functionality
- [ ] Certification status page
- [ ] Shareable badges
- [ ] Trust center landing page

---

## 📈 Success Metrics

### User Engagement
- Time to first evaluation run: < 2 minutes
- Dashboard interaction rate: > 70%
- Report download rate: > 40%

### Technical Performance
- Page load time: < 2s
- Chart render time: < 500ms
- API response time: < 1s (95th percentile)

### Business Impact
- Increased vendor trust scores
- Faster enterprise sales cycles
- Reduced security team blockers

---

## 🔐 Security & Compliance

### Data Handling
- **No PII storage** in frontend
- **Read-only access** to evaluation data
- **Secure API keys** via environment variables
- **CORS policies** for API access

### Authentication
- Optional Clerk integration for admin features
- Public dashboard for enterprise buyers
- Role-based access (viewer, admin)

---

## 📚 Reference Documents

This spec draws from:
- ✅ **evaluation_orchestrator.md** - Backend API structure
- ✅ **evaluation_round.md** - Round progression data
- ✅ **product_eng_brief.md** - User story & objectives
- ✅ **visualization_eval.md** - User journey & requirements
- ✅ **technical_direction.md** - Overall product vision

---

## 🎯 Key Takeaways

**For Developers**:
- Build with Next.js 14 + TypeScript
- Use Recharts for standard charts, Plotly for advanced
- Integrate with FastAPI backend endpoints
- Focus on performance and data visualization

**For Product**:
- Visual storytelling: Incident → Prevention → Testing → Confidence
- Enterprise buyer focus (non-AI experts)
- Trust signals throughout (AIUC-1, SOC 2, third-party)
- Clear improvement trajectory (77.9% → 94.1% → 97.4%)

**For Design**:
- Security-first aesthetic (professional, technical)
- Information-dense but scannable
- Interactive exploration encouraged
- Mobile-responsive (secondary priority)

---

*Built to give enterprise buyers confidence in AI agent safety* 🛡️
