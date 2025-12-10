"""
Data Loading Utilities
Handles cached loading of all CSV datasets with validation
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Data directory (relative to project root)
DATA_DIR = Path(__file__).parent.parent / "data" / "output"

# Fallback to parent directory's output folder if local doesn't exist
if not DATA_DIR.exists():
    DATA_DIR = Path(__file__).parent.parent.parent / "output"


def _add_donor_tiers(df):
    """
    Add DONOR_TIER column to donors DataFrame based on TOTAL_CONTRIB amounts.

    Tiers:
    - Mega: $1M+
    - Major: $100K-$1M
    - Significant: $10K-$100K
    - Small: $400-$10K
    - Nano: <$400

    Args:
        df (pd.DataFrame): Donors DataFrame with TOTAL_CONTRIB column

    Returns:
        pd.DataFrame: DataFrame with DONOR_TIER column added
    """
    if df.empty or 'TOTAL_CONTRIB' not in df.columns:
        return df

    def classify_tier(amount):
        """Classify donor tier based on total contribution amount."""
        if pd.isna(amount):
            return 'Unknown'
        if amount >= 1_000_000:
            return 'Mega'
        elif amount >= 100_000:
            return 'Major'
        elif amount >= 10_000:
            return 'Significant'
        elif amount >= 400:
            return 'Small'
        else:
            return 'Nano'

    df['DONOR_TIER'] = df['TOTAL_CONTRIB'].apply(classify_tier)
    return df


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """
    Load all campaign finance datasets with caching.

    Returns:
        dict: Dictionary with keys: 'committees', 'candidates', 'donors', 'breakdown', 'totals'
    """
    logger.info("Loading campaign finance datasets...")

    data = {}

    try:
        # Committee data
        committees_path = DATA_DIR / "all_committees_powerbi.csv"
        if committees_path.exists():
            data['committees'] = pd.read_csv(committees_path)
            logger.info(f"Loaded {len(data['committees'])} committees")
        else:
            logger.warning(f"Committees file not found: {committees_path}")
            data['committees'] = pd.DataFrame()

        # Candidate data
        candidates_path = DATA_DIR / "all_candidates_powerbi.csv"
        if candidates_path.exists():
            data['candidates'] = pd.read_csv(candidates_path)
            logger.info(f"Loaded {len(data['candidates'])} candidates")
        else:
            logger.warning(f"Candidates file not found: {candidates_path}")
            data['candidates'] = pd.DataFrame()

        # Donor data
        donors_path = DATA_DIR / "input_oligarchy_donors.csv"
        if donors_path.exists():
            data['donors'] = pd.read_csv(donors_path)
            # Add DONOR_TIER column based on TOTAL_CONTRIB
            data['donors'] = _add_donor_tiers(data['donors'])
            logger.info(f"Loaded {len(data['donors'])} donors")
        else:
            logger.warning(f"Donors file not found: {donors_path}")
            data['donors'] = pd.DataFrame()

        # Breakdown summary
        breakdown_path = DATA_DIR / "complete_campaign_finance_breakdown.csv"
        if breakdown_path.exists():
            data['breakdown'] = pd.read_csv(breakdown_path)
            logger.info(f"Loaded breakdown with {len(data['breakdown'])} categories")
        else:
            logger.warning(f"Breakdown file not found: {breakdown_path}")
            data['breakdown'] = pd.DataFrame()

        # Totals summary
        totals_path = DATA_DIR / "complete_summary_totals.csv"
        if totals_path.exists():
            data['totals'] = pd.read_csv(totals_path)
            logger.info(f"Loaded {len(data['totals'])} summary metrics")
        else:
            logger.warning(f"Totals file not found: {totals_path}")
            data['totals'] = pd.DataFrame()

        logger.info("All datasets loaded successfully")
        return data

    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise


def get_data_summary(data):
    """
    Generate summary statistics for loaded data.

    Args:
        data (dict): Dictionary from load_all_data()

    Returns:
        dict: Summary statistics
    """
    summary = {
        'committee_count': len(data['committees']) if 'committees' in data else 0,
        'candidate_count': len(data['candidates']) if 'candidates' in data else 0,
        'donor_count': len(data['donors']) if 'donors' in data else 0,
        'total_spending': 0,
        'megadonor_count': 0
    }

    # Calculate total spending
    if 'totals' in data and not data['totals'].empty:
        total_row = data['totals'][data['totals']['Metric'] == 'Total Disbursements']
        if not total_row.empty:
            summary['total_spending'] = total_row['Amount'].values[0]

    # Count megadonors
    if 'donors' in data and not data['donors'].empty:
        summary['megadonor_count'] = len(data['donors'][data['donors']['DONOR_TIER'] == 'Mega'])

    return summary


@st.cache_data
def load_committee_data():
    """Load only committee data (for faster partial loading)."""
    committees_path = DATA_DIR / "all_committees_powerbi.csv"
    return pd.read_csv(committees_path)


@st.cache_data
def load_candidate_data():
    """Load only candidate data (for faster partial loading)."""
    candidates_path = DATA_DIR / "all_candidates_powerbi.csv"
    return pd.read_csv(candidates_path)


@st.cache_data
def load_donor_data():
    """Load only donor data (for faster partial loading)."""
    donors_path = DATA_DIR / "input_oligarchy_donors.csv"
    df = pd.read_csv(donors_path)
    return _add_donor_tiers(df)
