"""
Data Loading Module
Saves transformed data to CSV files with validation and backup
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


def save_to_csv(dataframes, output_dir, create_backup=True):
    """
    Save cleaned DataFrames to CSV files.

    Args:
        dataframes (dict): Dictionary of {name: DataFrame}
        output_dir (Path): Output directory path
        create_backup (bool): Whether to backup existing files

    Returns:
        bool: Success status
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Backup directory
    if create_backup:
        backup_dir = output_dir.parent / "backup"
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # File mapping
    file_mapping = {
        'committees': 'all_committees_powerbi.csv',
        'candidates': 'all_candidates_powerbi.csv',
        'donors': 'input_oligarchy_donors.csv',
        'breakdown': 'complete_campaign_finance_breakdown.csv',
        'totals': 'complete_summary_totals.csv'
    }

    logger.info(f"Saving {len(dataframes)} datasets to {output_dir}")

    for name, df in dataframes.items():
        if name not in file_mapping:
            logger.warning(f"Unknown dataset: {name}")
            continue

        filename = file_mapping[name]
        output_path = output_dir / filename

        # Backup existing file
        if create_backup and output_path.exists():
            backup_path = backup_dir / f"{filename}.{timestamp}.bak"
            shutil.copy2(output_path, backup_path)
            logger.info(f"Backed up {filename} to {backup_path}")

        # Save to CSV
        try:
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Saved {filename} ({len(df)} rows)")

            # Validation
            validate_output(df, name)

        except Exception as e:
            logger.error(f"Failed to save {filename}: {str(e)}")
            return False

    logger.info("All datasets saved successfully")
    return True


def validate_output(df, dataset_name):
    """
    Validate output DataFrame for data quality.

    Args:
        df (pd.DataFrame): DataFrame to validate
        dataset_name (str): Name of dataset

    Returns:
        bool: Validation passed
    """
    # Row count check
    if len(df) == 0:
        logger.warning(f"{dataset_name}: Empty dataset")
        return False

    # Check for required columns
    required_columns = {
        'committees': ['CMTE_ID', 'CMTE_NM', 'TTL_RECEIPTS', 'TTL_DISB'],
        'candidates': ['CAND_ID', 'CAND_NAME', 'TTL_RECEIPTS', 'TTL_DISB'],
        'donors': ['DONOR_KEY', 'TOTAL_CONTRIB', 'DONOR_TIER']
    }

    if dataset_name in required_columns:
        missing_cols = set(required_columns[dataset_name]) - set(df.columns)
        if missing_cols:
            logger.warning(f"{dataset_name}: Missing columns {missing_cols}")
            return False

    # Check for nulls in critical fields
    if dataset_name in ['committees', 'candidates']:
        id_col = 'CMTE_ID' if dataset_name == 'committees' else 'CAND_ID'
        if df[id_col].isnull().any():
            logger.warning(f"{dataset_name}: Null values in {id_col}")
            return False

    logger.info(f"{dataset_name}: Validation passed")
    return True


if __name__ == "__main__":
    # Test save
    test_df = pd.DataFrame({
        'CMTE_ID': ['C001', 'C002'],
        'CMTE_NM': ['Test PAC 1', 'Test PAC 2'],
        'TTL_RECEIPTS': [100000, 200000],
        'TTL_DISB': [95000, 190000]
    })

    output_dir = Path(__file__).parent.parent / "data" / "output" / "test"
    save_to_csv({'committees': test_df}, output_dir)
