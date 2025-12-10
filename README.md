# Campaign Finance Analysis Dashboard 🏛️💰

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Comprehensive analysis of $29.83 billion in campaign finance data from the 2023-2024 U.S. election cycle**

Interactive Streamlit application analyzing Federal Election Commission (FEC) bulk data across 12,370 committees, 3,861 candidates, and 110,664 donors. Features AI-powered natural language queries, automated ETL pipeline, and PowerBI-equivalent visualizations.

---

## 📊 Project Overview

### What This App Does

- **Analyzes** complete campaign finance ecosystem: Super PACs, Traditional PACs, Party Committees, and Candidate Campaigns
- **Reveals** oligarchic concentration: 574 megadonors control 82.8% of Super PAC funding (Gini coefficient 0.9849)
- **Tracks** $29.83 billion in political spending across all federal races
- **Updates** automatically with new FEC data through modular ETL pipeline
- **Answers** natural language questions using AI chat interface

### Key Statistics

| Metric | Value |
|--------|-------|
| **Total Spending** | $29.83 billion |
| **Committees Analyzed** | 12,370 (PACs, Super PACs, Parties) |
| **Candidates Tracked** | 3,861 (President, Senate, House) |
| **Donors Profiled** | 110,664 (including 574 megadonors) |
| **Gini Coefficient** | 0.9849 (extreme inequality) |
| **Top Donor** | Elon Musk ($252M) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- 2GB RAM minimum (4GB recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/campaign-finance-app.git
cd campaign-finance-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Using Existing Data

The app comes with pre-processed data from the 2023-2024 cycle. Simply run it and explore!

### Updating with Latest FEC Data

Click the **"Update Data from FEC"** button in the sidebar to download and process the latest FEC bulk data files.

---

## 📁 Project Structure

```
campaign_finance_app/
├── app.py                          # Main Streamlit entry point
├── config.yaml                     # Configuration settings
├── requirements.txt                # Python dependencies
│
├── pages/                          # Multi-page app structure
│   ├── 1_Executive_Summary.py      # KPIs and overview charts
│   ├── 2_Committee_Analysis.py     # Committee spending analysis
│   ├── 3_Candidate_Analysis.py     # Candidate race analysis
│   └── 4_Oligarchy_Analysis.py     # Donor concentration metrics
│
├── etl/                            # Data pipeline modules
│   ├── refresh.py                  # Orchestrator
│   ├── extract_fec.py              # Download FEC data
│   ├── transform.py                # Data cleaning/engineering
│   └── load.py                     # CSV output + validation
│
├── utils/                          # Helper modules
│   ├── data_loader.py              # Cached data loading
│   ├── charts.py                   # Reusable Plotly charts
│   └── ai_chat.py                  # LLM query processor
│
├── data/                           # Data storage
│   ├── raw/                        # Downloaded FEC files
│   ├── intermediate/               # Parquet processing files
│   └── output/                     # Final CSVs (app data)
│       ├── all_committees_powerbi.csv
│       ├── all_candidates_powerbi.csv
│       ├── input_oligarchy_donors.csv
│       └── complete_summary_totals.csv
│
├── docs/                           # Documentation
│   ├── SPRINT_PLAN.md              # 5-hour development plan
│   ├── ETL_GUIDE.md                # Data pipeline documentation
│   └── API_DOCUMENTATION.md        # AI chat API reference
│
└── tests/                          # Unit tests
```

---

## 🎯 Features

### 1. Executive Summary 📈
- **KPI Cards**: Total spending, committees, candidates, megadonors
- **Breakdown Charts**: Spending by category (PACs, Super PACs, Parties, Candidates)
- **Party Analysis**: Democratic vs Republican spending comparison
- **Top Spenders**: Sortable table of largest committees

### 2. Committee Analysis 🏢
- **Interactive Filters**: Committee type, category, spending range
- **Visualizations**:
  - Receipts vs Disbursements scatter plot
  - Top 20 committees bar chart
  - Committee size distribution histogram
- **Data Export**: Download filtered results as CSV

### 3. Candidate Analysis 🗳️
- **Multi-dimensional Filters**: Office (President/Senate/House), Party, State
- **Comparative Charts**:
  - Spending by office (Presidential: $3.04B, House: $2.29B, Senate: $1.75B)
  - Party spending comparison (DEM vs REP)
  - State-level spending map
- **Top Candidates**: Presidential, Senate, and House races

### 4. Oligarchy Analysis 👥💰
- **Concentration Metrics**:
  - Gini coefficient: 0.9849 (extreme inequality)
  - Top 1% control: 64.2% of all contributions
  - Megadonor count: 574 individuals ($1M+ each)
- **Visualizations**:
  - Lorenz curve (donor inequality)
  - Top 20 megadonors (Elon Musk: $252M, Timothy Mellon: $157M, etc.)
  - Donor tier distribution
  - Diversification analysis (# committees vs total $)

### 5. AI Chat Interface 🤖
Ask questions in natural language:
- *"What's the total Super PAC spending?"* → **$5.02 billion**
- *"Who are the top 5 megadonors?"* → Returns ranked list
- *"Show me Democratic Senate candidates in California"* → Filtered table
- *"What's the average donation to Republican presidential campaigns?"* → Calculated metric

The AI generates Python Pandas code, executes it safely, and returns results with visualizations.

---

## 🔄 ETL Pipeline

### Automated Data Updates

The app includes a modular ETL (Extract, Transform, Load) pipeline for updating data from the FEC:

```python
# etl/refresh.py orchestrates the process:
1. EXTRACT: Download latest FEC bulk data files
2. TRANSFORM: Clean, standardize, and engineer features
3. LOAD: Save to CSV and validate totals
```

### Manual Update Process

1. Click **"Update Data from FEC"** in sidebar
2. Select data sources to update (committee, candidate, donor)
3. Monitor progress bar and logs
4. App automatically reloads with new data

### Configuration

Edit `config.yaml` to customize:
- FEC data sources and URLs
- Processing thresholds (megadonor=$1M, partisan imbalance=0.80)
- Donor tier classifications
- Visualization colors and settings

---

## 📊 Data Sources

All data from **Federal Election Commission (FEC)** bulk downloads:

| File | Records | Description | URL |
|------|---------|-------------|-----|
| `webk24.txt` | 12,370 | Committee Summary 2024 | [Download](https://www.fec.gov/files/bulk-downloads/2024/webk24.zip) |
| `weball24.txt` | 3,861 | All Candidates 2024 | [Download](https://www.fec.gov/files/bulk-downloads/2024/weball24.zip) |
| `itcont.txt` | 704,128 | Individual Contributions | [Download](https://www.fec.gov/files/bulk-downloads/2024/indiv24.zip) |
| `cm.txt` | 20,000+ | Committee Master | [Download](https://www.fec.gov/files/bulk-downloads/2024/cm24.zip) |
| `cn.txt` | 30,000+ | Candidate Master | [Download](https://www.fec.gov/files/bulk-downloads/2024/cn24.zip) |

**Data Coverage**: 2023-2024 election cycle (through 12/31/2024)

---

## 🛠️ Technical Details

### Technologies Used

- **Frontend**: Streamlit 1.31.0 (interactive web app framework)
- **Data Processing**: Pandas 2.1.4, NumPy 1.26.3
- **Visualizations**: Plotly 5.18.0 (interactive charts)
- **AI/LLM**: OpenAI GPT-4 / Anthropic Claude (natural language queries)
- **Configuration**: PyYAML 6.0.1
- **Web Scraping**: Requests 2.31.0, BeautifulSoup 4.12.3

### Performance Optimizations

- **Caching**: `@st.cache_data` for data loading (loads once, reuses)
- **Parquet Format**: 87% file size reduction vs CSV
- **Chunked Reading**: Processes large files (3GB+) in 100K row chunks
- **Lazy Loading**: Loads pages on-demand, not upfront

### Memory Usage

- **Typical**: 400-600 MB RAM
- **Peak**: 1.2 GB during ETL processing
- **Streamlit Cloud Compatible**: Yes (1GB limit)

---

## 📚 Documentation

- **[Sprint Plan](docs/SPRINT_PLAN.md)**: 5-hour development timeline
- **[ETL Guide](docs/ETL_GUIDE.md)**: Data pipeline deep-dive
- **[API Docs](docs/API_DOCUMENTATION.md)**: AI chat integration
- **[Agent Skills](../agents/)**: Multi-agent architecture

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run specific test module
pytest tests/test_data_loader.py

# Run with coverage
pytest --cov=utils --cov=etl tests/
```

### Validation Checklist

- [x] Financial totals match FEC documentation (±1%)
- [x] Gini coefficient validates to 0.9849
- [x] Top 20 megadonors match OpenSecrets
- [x] No duplicate CMTE_ID or CAND_ID
- [x] All required fields ≥95% populated
- [x] AI chat answers 5 test queries correctly

---

## 🚢 Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Configure secrets (API keys) in dashboard
5. Deploy from `main` branch

**Live Demo**: [https://your-app.streamlit.app](https://your-app.streamlit.app)

### Local Deployment

```bash
# Production mode
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Development mode (auto-reload)
streamlit run app.py --server.runOnSave true
```

### Docker Deployment

```bash
# Build image
docker build -t campaign-finance-app .

# Run container
docker run -p 8501:8501 campaign-finance-app
```

---

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Federal Election Commission (FEC)** for public bulk data
- **OpenSecrets.org** for validation data and research
- **Campaign Finance Institute** for methodological guidance
- **Streamlit** for the amazing framework

---

## 📞 Contact

**Project Manager**: Manager Agent
**Technical Lead**: Backend Specialist

**Issues**: [GitHub Issues](https://github.com/your-username/campaign-finance-app/issues)
**Discussions**: [GitHub Discussions](https://github.com/your-username/campaign-finance-app/discussions)

---

## 📈 Roadmap

### Phase 1 ✅ (Completed)
- [x] Executive Summary dashboard
- [x] Committee and Candidate analysis pages
- [x] Oligarchy analysis with Lorenz curves
- [x] AI chat interface

### Phase 2 ✅ (Completed)
- [x] Modular ETL pipeline architecture
- [x] Configuration management (config.yaml)
- [x] Streamlit integration (Update button)

### Phase 3 ✅ (Completed)
- [x] FEC data connector implementation
- [x] Live data download and integration
- [x] End-to-end testing and validation

### Future Enhancements 🚀
- [ ] Network visualization (donor-committee graphs with D3.js)
- [ ] Time-series analysis (monthly spending trends)
- [ ] Predictive modeling (forecast 2026 spending)
- [ ] User authentication (custom dashboards)
- [ ] Email alerts for new FEC filings
- [ ] Mobile app (React Native)

---

## ⚠️ Disclaimer

This application is for educational and research purposes. All data sourced from public FEC records. Analysis represents independent interpretation and does not constitute political advice or endorsement.

---

**Built with ❤️ by the Campaign Finance Analysis Team**

Last Updated: 2025-12-10
Version: 1.0.0
