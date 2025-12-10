# Campaign Finance Analysis App - Sprint Plan
**Project:** Modular Streamlit Political Analysis Dashboard
**Manager:** Manager Agent
**Sprint Duration:** 5 Hours (3 Phases)
**Target Deployment:** GitHub → Streamlit Cloud
**Data Source:** FEC Bulk Data (2023-2024 Cycle)

---

## PROJECT OVERVIEW

### Objective
Build a production-ready Streamlit application that analyzes $29.83 billion in campaign finance data across 12,370 committees, 3,861 candidates, and 110,664 donors. The app must support:
- Interactive dashboards with real-time filtering
- AI-powered natural language query interface
- Automated ETL pipeline for FEC data updates
- PowerBI-equivalent visualizations in browser

### Success Criteria
- ✅ All 4 dashboard pages functional with <2 second load time
- ✅ AI chat correctly interprets 80%+ natural language queries
- ✅ ETL pipeline successfully processes sample FEC file
- ✅ GitHub repository ready for collaborative development
- ✅ Deployment-ready with requirements.txt and documentation

### Key Datasets (Already Processed)
1. `all_committees_powerbi.csv` - 12,370 committees, $22.75B spending
2. `all_candidates_powerbi.csv` - 3,861 candidates, $7.08B spending
3. `input_oligarchy_donors.csv` - 110,664 donors, Gini 0.9849
4. `complete_campaign_finance_breakdown.csv` - Summary by category
5. `complete_summary_totals.csv` - KPI metrics

---

## PHASE 1: CORE DASHBOARD (Hours 1-3)

### Hour 1: Executive Summary Page + App Foundation
**Assignee:** Frontend Specialist + Backend Specialist
**Deliverables:**

#### 1.1 App Structure (20 min)
- [x] Create `app.py` with Streamlit multi-page architecture
- [x] Implement sidebar navigation (st.sidebar.radio)
- [x] Configure page layout (wide mode, custom theme)
- [x] Add header with project title and data date range

#### 1.2 Data Loading Module (15 min)
- [x] Create `utils/data_loader.py` with caching (@st.cache_data)
- [x] Load all 5 CSV files into memory
- [x] Implement error handling for missing files
- [x] Add data validation checks (row counts, column names)

#### 1.3 Executive Summary Page (25 min)
**Components:**
1. **KPI Cards (4 columns)**
   - Total Spending: $29.83B (from complete_summary_totals.csv)
   - Total Committees: 12,370
   - Total Candidates: 3,861
   - Megadonors: 574 ($1M+ donors from input_oligarchy_donors.csv)

2. **Visualizations (2 charts)**
   - Bar Chart: Spending by Category (Traditional PACs, Super PACs, Parties, Candidates)
   - Pie Chart: Spending by Party (DEM vs REP vs Other)

3. **Interactive Table**
   - Top 10 Committees by Spending (sortable, searchable)
   - Columns: Name, Type, Category, Receipts, Disbursements

**Acceptance Criteria:**
- All KPIs display correct totals (validated against documentation)
- Charts render in <1 second with Plotly
- Table supports sorting by any column

---

### Hour 2: Committee & Candidate Analysis Pages
**Assignee:** Frontend Specialist + Data Analyst
**Deliverables:**

#### 2.1 Committee Analysis Page (30 min)
**Interactive Filters (Sidebar):**
- Committee Type: Multi-select (Super PAC, Traditional PAC, Party, Other)
- Category: Dropdown (all categories)
- Spending Range: Slider ($0 - $377M)

**Visualizations:**
1. Scatter Plot: Receipts vs Disbursements (color by category)
2. Bar Chart: Top 20 Committees by Spending
3. Histogram: Distribution of Committee Sizes (log scale)

**Data Table:**
- Filtered committee list with all financial columns
- Download button (CSV export)

#### 2.2 Candidate Analysis Page (30 min)
**Interactive Filters (Sidebar):**
- Office: Multi-select (President, Senate, House)
- Party: Multi-select (DEM, REP, IND, LIB, etc.)
- State: Dropdown (all 50 states + DC)
- Spending Range: Slider

**Visualizations:**
1. Bar Chart: Spending by Office (President: $3.04B, House: $2.29B, Senate: $1.75B)
2. Bar Chart: Spending by Party (DEM vs REP comparison)
3. Map (Optional): Spending by State (Plotly choropleth)

**Data Table:**
- Filtered candidate list with office, party, state, spending
- Top 20 Candidates by Spending highlighted

**Acceptance Criteria:**
- Filters update charts in real-time (<500ms)
- All visualizations responsive to filter changes
- Data export functional

---

### Hour 3: Oligarchy Analysis + AI Chat Integration
**Assignee:** Data Analyst + Sentiment Analyst + Backend Specialist
**Deliverables:**

#### 3.1 Oligarchy Analysis Page (30 min)
**Data Source:** `input_oligarchy_donors.csv` (110,664 donors)

**KPI Cards:**
- Gini Coefficient: 0.9849
- Megadonors (574): Control 82.8% of $4.29B
- Top 1% Control: 64.2% of total
- Top Donor: Elon Musk ($252M)

**Visualizations:**
1. **Lorenz Curve:** Cumulative donor contributions (Plotly line)
2. **Bar Chart:** Top 20 Megadonors (Elon Musk, Timothy Mellon, Miriam Adelson...)
3. **Histogram:** Donor Tier Distribution (Mega, Major, Significant, Small, Nano)
4. **Scatter Plot:** Donor Diversification (Total $ vs # Committees)

**Interactive Table:**
- Megadonors only (574 rows), sortable by total contribution
- Columns: Name, Total, Tier, # Committees, State

#### 3.2 AI Chat Feature (30 min)
**Technology:** OpenAI API / Claude API + Pandas Agent

**Functionality:**
1. Text input box: "Ask a question about the data..."
2. Example queries displayed:
   - "Which Super PAC spent the most in Q4?"
   - "Show me all Democratic Senate candidates in California"
   - "What's the average megadonor contribution?"

3. Backend processing:
   - Parse natural language → Generate Pandas code
   - Execute query on loaded DataFrames
   - Return results as text + optional chart
   - Display generated code (collapsible for transparency)

4. Error handling:
   - Invalid queries → Suggest corrections
   - Ambiguous queries → Request clarification

**Acceptance Criteria:**
- Successfully answers 5 test queries (predefined)
- Handles errors gracefully (no app crashes)
- Response time <5 seconds per query

---

## PHASE 2: ETL ENGINE FOUNDATION (Hour 4)

### Hour 4: Modular ETL Pipeline Architecture
**Assignee:** Backend Specialist + Deployment Analyst
**Deliverables:**

#### 4.1 ETL Module Structure (20 min)
Create `etl/` folder with 5 modules:

**1. `etl/__init__.py`**
```python
# Package initialization
from .refresh import run_full_refresh
from .extract_fec import download_fec_data
from .transform import clean_and_transform
from .load import save_to_csv
```

**2. `etl/refresh.py`**
- Orchestrator function: `run_full_refresh()`
- Calls extract → transform → load in sequence
- Logs progress to console and file
- Returns success/failure status

**3. `etl/extract_fec.py`**
- (Placeholder) Function: `download_fec_data(cycle_year)`
- Currently returns existing file paths
- Hour 5: Implement actual FEC download

**4. `etl/transform.py`**
- Function: `clean_and_transform(raw_files)`
- Applies business rules:
  - Committee type filtering (O/U for Super PACs)
  - Monetary column conversion
  - Donor name standardization
  - Partisan classification logic
- Returns cleaned DataFrames

**5. `etl/load.py`**
- Function: `save_to_csv(dataframes, output_dir)`
- Writes final CSVs to `data/output/`
- Creates backup of previous version (timestamped)
- Validates output (row counts, financial totals)

#### 4.2 Streamlit Integration (20 min)
**Add to Sidebar:**
- Button: "Update Data from FEC"
- Progress bar during ETL execution
- Success/error notification
- Last update timestamp display

**Backend:**
- On button click: call `etl.refresh.run_full_refresh()`
- Stream logs to Streamlit interface (st.text)
- Reload data after successful update (clear cache)

#### 4.3 Configuration File (20 min)
**Create `config.yaml`:**
```yaml
data_sources:
  fec_base_url: "https://www.fec.gov/files/bulk-downloads/2024/"
  files:
    - name: "webk24.zip"
      description: "Committee Summary 2024"
    - name: "weball24.zip"
      description: "All Candidates 2024"
    - name: "indiv24.zip"
      description: "Individual Contributions"

paths:
  raw_data: "data/raw/"
  intermediate: "data/intermediate/"
  output: "data/output/"
  logs: "logs/"

processing:
  chunk_size: 100000
  parquet_compression: "snappy"
  csv_encoding: "utf-8"

thresholds:
  megadonor_amount: 1000000
  late_cycle_threshold: 0.50
  partisan_imbalance: 0.80
```

**Acceptance Criteria:**
- ETL pipeline runs without errors (using existing data)
- Streamlit button triggers refresh successfully
- Logs display in UI during execution
- Config file correctly parsed

---

## PHASE 3: FEC DATA CONNECTOR (Hour 5)

### Hour 5: Live FEC Data Extraction
**Assignee:** Web Scraper + Backend Specialist
**Deliverables:**

#### 5.1 FEC Download Implementation (25 min)
**Implement `etl/extract_fec.py`:**

```python
import requests
import zipfile
from pathlib import Path

def download_fec_data(cycle_year=2024, file_type='committee_master'):
    """
    Downloads specified FEC bulk data file.

    Args:
        cycle_year: Election cycle (2024, 2026, etc.)
        file_type: 'committee_master', 'candidate_master', etc.

    Returns:
        Path to downloaded and extracted file
    """
    # URL mapping
    fec_urls = {
        'committee_master': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/cm{cycle_year % 100}.zip',
        'committee_summary': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/webk{cycle_year % 100}.zip',
    }

    # Download logic
    # Extract logic
    # Validation logic

    return extracted_file_path
```

**Features:**
1. HTTP GET request with retry logic (3 attempts)
2. Progress bar for download (using tqdm)
3. Automatic zip extraction
4. File validation (size check, header verification)
5. Error handling (network errors, corrupted files)

#### 5.2 Integration Testing (20 min)
**Test Scenarios:**
1. Download `cm24.zip` (Committee Master 2024)
2. Extract and parse file
3. Merge with existing data
4. Generate updated CSV
5. Verify in Streamlit app

**Validation:**
- New committee count matches FEC documentation
- No duplicate CMTE_IDs introduced
- Financial totals reconcile with previous version ±5%

#### 5.3 Documentation (15 min)
**Update `README.md`:**
- ETL pipeline usage instructions
- Data update schedule recommendations
- FEC data source attributions
- Known limitations

**Create `docs/ETL_GUIDE.md`:**
- Step-by-step ETL execution
- Troubleshooting common errors
- Adding new data sources
- Custom transformation rules

**Acceptance Criteria:**
- Successfully downloads and processes live FEC file
- Full ETL pipeline (extract → transform → load) executes end-to-end
- Streamlit app displays updated data
- Documentation complete

---

## PROJECT TIMELINE (Gantt Chart)

```
Hour 1: ████████████████████ Executive Summary
        ├─ App Structure (20m)
        ├─ Data Loading (15m)
        └─ KPIs + Charts (25m)

Hour 2: ████████████████████ Committee + Candidate Analysis
        ├─ Committee Page (30m)
        └─ Candidate Page (30m)

Hour 3: ████████████████████ Oligarchy + AI Chat
        ├─ Oligarchy Page (30m)
        └─ AI Chat (30m)

Hour 4: ████████████████████ ETL Pipeline
        ├─ Module Structure (20m)
        ├─ Streamlit Integration (20m)
        └─ Config File (20m)

Hour 5: ████████████████████ FEC Connector
        ├─ Download Implementation (25m)
        ├─ Integration Testing (20m)
        └─ Documentation (15m)
```

---

## FOLDER STRUCTURE (Final)

```
campaign_finance_app/
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions for auto-deploy
├── docs/
│   ├── SPRINT_PLAN.md             # This document
│   ├── ETL_GUIDE.md               # ETL pipeline documentation
│   └── API_DOCUMENTATION.md       # AI chat API reference
├── etl/
│   ├── __init__.py
│   ├── refresh.py                 # Orchestrator
│   ├── extract_fec.py             # FEC data download
│   ├── transform.py               # Data cleaning/feature engineering
│   └── load.py                    # CSV output + validation
├── pages/
│   ├── 1_Executive_Summary.py     # Hour 1 deliverable
│   ├── 2_Committee_Analysis.py    # Hour 2 deliverable
│   ├── 3_Candidate_Analysis.py    # Hour 2 deliverable
│   └── 4_Oligarchy_Analysis.py    # Hour 3 deliverable
├── utils/
│   ├── data_loader.py             # Cached data loading
│   ├── charts.py                  # Reusable Plotly charts
│   └── ai_chat.py                 # LLM query processor
├── data/
│   ├── raw/                       # Downloaded FEC files
│   ├── intermediate/              # Parquet files (processing)
│   └── output/                    # Final CSVs (app data)
├── logs/                          # ETL execution logs
├── tests/                         # Unit tests (optional)
├── app.py                         # Main Streamlit entry point
├── config.yaml                    # Configuration settings
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git exclusions
└── README.md                      # Project documentation
```

---

## DEPENDENCIES (requirements.txt)

```
streamlit==1.31.0
pandas==2.1.4
plotly==5.18.0
numpy==1.26.3
pyyaml==6.0.1
requests==2.31.0
openpyxl==3.1.2
python-dotenv==1.0.0
openai==1.10.0              # For AI chat
anthropic==0.18.0           # Alternative LLM
```

**Optional (for advanced features):**
```
altair==5.2.0               # Alternative charting
folium==0.15.1              # Interactive maps
streamlit-folium==0.16.0
scipy==1.11.4               # Statistical analysis
networkx==3.2.1             # Network visualization
```

---

## RISK MANAGEMENT

### High Risk Items
1. **AI Chat Reliability**
   - *Risk:* LLM generates incorrect Pandas code
   - *Mitigation:* Validate code before execution, sandbox environment
   - *Fallback:* Pre-programmed query templates

2. **FEC API Changes**
   - *Risk:* FEC changes bulk data URLs or formats
   - *Mitigation:* Error handling, fallback to manual upload
   - *Contingency:* Version-lock known working URLs

3. **Performance with Large Datasets**
   - *Risk:* 110K donor table causes lag
   - *Mitigation:* Pagination, lazy loading, Streamlit caching
   - *Optimization:* Convert to DuckDB for faster queries

### Medium Risk Items
1. **Deployment Issues**
   - *Risk:* Streamlit Cloud memory limits (1GB)
   - *Mitigation:* Use Parquet instead of CSV, optimize DataFrames

2. **Data Quality Errors**
   - *Risk:* FEC data contains anomalies (negative amounts, missing IDs)
   - *Mitigation:* Comprehensive validation in `transform.py`

---

## ACCEPTANCE TESTING CHECKLIST

### Phase 1 (Dashboard)
- [ ] Executive Summary displays correct $29.83B total
- [ ] All 4 KPI cards show accurate numbers
- [ ] Committee Analysis filters work (type, category, spending range)
- [ ] Candidate Analysis shows correct party breakdowns
- [ ] Oligarchy page displays Gini 0.9849
- [ ] Top 20 megadonors table includes Elon Musk ($252M)
- [ ] AI chat answers: "What's the total Super PAC spending?" → "$5.02B"
- [ ] AI chat answers: "Top 5 donors?" → Returns correct list

### Phase 2 (ETL)
- [ ] ETL button appears in sidebar
- [ ] Clicking button triggers `run_full_refresh()`
- [ ] Progress bar displays during execution
- [ ] Logs stream to UI in real-time
- [ ] Success message appears on completion
- [ ] Data reload occurs automatically
- [ ] Config.yaml parsed correctly

### Phase 3 (FEC Connector)
- [ ] `download_fec_data()` successfully downloads cm24.zip
- [ ] File extracts without errors
- [ ] Parsed data integrates with existing datasets
- [ ] Updated CSVs written to `data/output/`
- [ ] Streamlit app reflects new data
- [ ] Documentation updated with new instructions

---

## POST-SPRINT ENHANCEMENTS (Future Sprints)

### Sprint 2: Advanced Analytics
- Network visualization (donor-committee graphs)
- Time-series analysis (monthly spending trends)
- Predictive modeling (forecast 2026 spending)
- Geospatial analysis (state-level heatmaps)

### Sprint 3: User Features
- User authentication (for custom dashboards)
- Saved query templates
- Email alerts for new FEC data
- Export to PowerBI/Tableau

### Sprint 4: Performance Optimization
- Database backend (PostgreSQL/DuckDB)
- Incremental data updates (not full refresh)
- Caching layer (Redis)
- Load balancing for high traffic

---

## DEPLOYMENT STRATEGY

### GitHub Repository Setup
1. Initialize repo: `git init`
2. Add remote: `git remote add origin <repo_url>`
3. Create `.gitignore` (exclude data/, logs/, .env)
4. Initial commit with complete codebase
5. Push to main branch

### Streamlit Cloud Deployment
1. Connect GitHub repo to Streamlit Cloud
2. Configure secrets (API keys for AI chat)
3. Set Python version (3.10+)
4. Deploy from main branch
5. Monitor resource usage (RAM, CPU)

### CI/CD Pipeline (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Streamlit
        run: echo "Auto-deploy configured"
```

---

## SUCCESS METRICS

### Technical Metrics
- [ ] App loads in <3 seconds
- [ ] All pages render without errors
- [ ] ETL pipeline completes in <10 minutes
- [ ] AI chat response time <5 seconds
- [ ] Memory usage <1GB (Streamlit Cloud limit)

### User Experience Metrics
- [ ] 80%+ AI queries answered correctly
- [ ] Filters update charts in <500ms
- [ ] Data export downloads successfully
- [ ] Mobile-responsive layout

### Data Quality Metrics
- [ ] Financial totals match documentation (±1%)
- [ ] No duplicate records (CMTE_ID, CAND_ID)
- [ ] All required fields ≥95% populated
- [ ] Gini coefficient validates to 0.9849

---

## TEAM ASSIGNMENTS

| Agent | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|
| **Frontend Specialist** | Dashboard pages | UI for ETL button | Polish & testing |
| **Backend Specialist** | Data loading | ETL modules | FEC connector |
| **Data Analyst** | Filters & metrics | Transform logic | Data validation |
| **Web Scraper** | N/A | N/A | FEC download |
| **Deployment Analyst** | N/A | Config setup | Cloud deployment |
| **Sentiment Analyst** | AI chat prompts | N/A | Query optimization |
| **Manager** | Oversight | Code review | Final QA |

---

## CONTACT & ESCALATION

**Sprint Manager:** Manager Agent
**Technical Lead:** Backend Specialist
**Escalation Path:** Manager → User (for approval of scope changes)

**Daily Standup Questions:**
1. What did you complete in the last hour?
2. What will you work on in the next hour?
3. Any blockers or dependencies?

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Status:** READY FOR EXECUTION ✅
