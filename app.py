"""
Campaign Finance Analysis Dashboard
Main Streamlit Application Entry Point

Author: Campaign Finance Analysis Team
Date: 2025-12-10
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import yaml
import sys

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.data_loader import load_all_data, get_data_summary
from utils.charts import create_spending_breakdown_chart, create_party_comparison_chart

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Campaign Finance Analysis",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/campaign-finance-app',
        'Report a bug': 'https://github.com/your-username/campaign-finance-app/issues',
        'About': 'Analysis of $29.83 billion in 2023-2024 campaign finance data from FEC'
    }
)

# Load configuration
@st.cache_data
def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# ==============================================================================
# SIDEBAR
# ==============================================================================

with st.sidebar:
    st.title("🏛️ Campaign Finance")
    st.markdown("### 2023-2024 Election Cycle")
    st.divider()

    # Navigation
    st.markdown("### 📊 Navigation")
    page = st.radio(
        "Select Page:",
        ["Executive Summary", "Committee Analysis", "Candidate Analysis", "Oligarchy Analysis", "Hypothesis Testing", "AI Chat"],
        label_visibility="collapsed"
    )

    st.divider()

    # Data Update Section
    st.markdown("### 🔄 Data Management")

    if st.button("🔄 Update Data from FEC", use_container_width=True, type="primary"):
        st.info("🚧 **Coming Soon! Not ready yet.**")
        st.markdown("""
        **Automated FEC data refresh is under development.**

        This feature will enable:
        - ✅ Automatic download of latest FEC bulk data files
        - ✅ Data validation and transformation
        - ✅ Incremental updates to dashboard datasets
        - ✅ Real-time contribution tracking

        **For now**: Data is current as of the 2023-2024 election cycle.

        **Manual Update Instructions**:
        1. Download FEC bulk data from [fec.gov/data/browse-data/?tab=bulk-data](https://www.fec.gov/data/browse-data/?tab=bulk-data)
        2. Run ETL pipeline: `python etl/refresh.py`
        3. Restart the Streamlit app
        """)

    # Last update timestamp
    st.caption("📅 Last Updated: 2024-12-31 | Data covers 2023-2024 election cycle")
    st.caption("📊 Source: FEC Bulk Data (webk24.txt, weball24.txt, itcont.txt)")

    st.divider()

    # Quick Stats
    st.markdown("### 📈 Quick Stats")
    st.metric("Total Spending", "$29.83B")
    st.metric("Committees", "12,370")
    st.metric("Candidates", "3,861")
    st.metric("Megadonors", "574")

    st.divider()

    # Links
    st.markdown("### 🔗 Resources")
    st.markdown("[📄 Documentation](https://github.com)")
    st.markdown("[📊 FEC Data](https://www.fec.gov/data/)")
    st.markdown("[🐛 Report Issue](https://github.com/issues)")

# ==============================================================================
# MAIN CONTENT
# ==============================================================================

# Header
st.title("Campaign Finance Analysis Dashboard")
st.markdown(f"### {page}")
st.markdown("---")

# Load data
try:
    data = load_all_data()
    df_committees = data['committees']
    df_candidates = data['candidates']
    df_donors = data['donors']
    df_breakdown = data['breakdown']
    df_totals = data['totals']
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure all CSV files are in the data/output/ folder.")
    st.stop()

# ==============================================================================
# PAGE ROUTING
# ==============================================================================

if page == "Executive Summary":
    # =========================================================================
    # HOUR 1: EXECUTIVE SUMMARY PAGE
    # =========================================================================

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_spending = df_totals[df_totals['Metric'] == 'Total Disbursements']['Amount'].values[0]
        st.metric(
            "Total Spending",
            f"${total_spending / 1e9:.2f}B",
            delta="2023-2024 Cycle"
        )

    with col2:
        committee_count = len(df_committees)
        st.metric(
            "Total Committees",
            f"{committee_count:,}",
            delta="PACs + Super PACs + Parties"
        )

    with col3:
        candidate_count = len(df_candidates)
        st.metric(
            "Total Candidates",
            f"{candidate_count:,}",
            delta="All Federal Races"
        )

    with col4:
        # Count megadonors ($1M+ contributors)
        if 'DONOR_TIER' in df_donors.columns:
            megadonor_count = len(df_donors[df_donors['DONOR_TIER'] == 'Mega'])
        elif 'IS_MEGADONOR' in df_donors.columns:
            megadonor_count = df_donors['IS_MEGADONOR'].sum()
        elif 'TOTAL_CONTRIB' in df_donors.columns:
            megadonor_count = len(df_donors[df_donors['TOTAL_CONTRIB'] >= 1_000_000])
        else:
            megadonor_count = 0

        st.metric(
            "Megadonors",
            f"{megadonor_count:,}",
            delta="$1M+ Contributors"
        )

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Spending by Category")
        fig1 = create_spending_breakdown_chart(df_breakdown)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("#### Spending by Party")
        fig2 = create_party_comparison_chart(df_candidates)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # Top Committees Table
    st.markdown("#### Top 10 Committees by Spending")

    top_committees = df_committees.nlargest(10, 'TTL_DISB')[
        ['CMTE_NM', 'CATEGORY', 'TTL_RECEIPTS', 'TTL_DISB']
    ].copy()

    top_committees['TTL_RECEIPTS'] = top_committees['TTL_RECEIPTS'].apply(lambda x: f"${x:,.0f}")
    top_committees['TTL_DISB'] = top_committees['TTL_DISB'].apply(lambda x: f"${x:,.0f}")
    top_committees.columns = ['Committee Name', 'Category', 'Total Receipts', 'Total Disbursements']

    st.dataframe(
        top_committees,
        use_container_width=True,
        hide_index=True,
        height=400
    )

elif page in ["Committee Analysis", "Candidate Analysis", "Oligarchy Analysis", "Hypothesis Testing", "AI Chat"]:
    st.info("✅ **All dashboard pages are now available!**")
    st.markdown("### 📄 Navigate using the sidebar:")
    st.markdown("""
    - **2_Committee_Analysis** - Explore 12,370+ PACs and committees with interactive filters
    - **3_Candidate_Analysis** - Analyze 3,861 federal candidates by office, party, and state
    - **4_Oligarchy_Analysis** - Deep dive into donor concentration with Gini coefficients and Lorenz curves
    - **5_AI_Chat** - Ask questions in natural language (Demo mode available)
    - **6_Hypothesis_Testing** - Statistical analysis of oligarchic patterns

    **👉 Click on any page in the sidebar to explore!**
    """)

# ==============================================================================
# FOOTER
# ==============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 20px;'>
    <p>Data Source: Federal Election Commission (FEC) Bulk Data • 2023-2024 Election Cycle</p>
    <p><strong>Created by Horacio Fonseca</strong>, Data Analyst • MDC Undergraduate</p>
    <p>Built with ❤️ using Streamlit • For educational and research purposes only</p>
    <p>Last Updated: 2024-12-31 • Version 1.0.0</p>
    </div>
    """,
    unsafe_allow_html=True
)
