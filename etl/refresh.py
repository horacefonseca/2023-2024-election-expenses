"""
ETL Refresh Orchestrator
Coordinates full data refresh pipeline: extract → transform → load
"""

import logging
from pathlib import Path
from datetime import datetime
from .extract_fec import download_fec_data
from .transform import clean_and_transform
from .load import save_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_full_refresh(cycle_year=2024):
    """
    Execute complete ETL pipeline to refresh campaign finance data.

    Args:
        cycle_year (int): Election cycle year (2024, 2026, etc.)

    Returns:
        tuple: (success: bool, message: str)
    """
    start_time = datetime.now()
    logger.info(f"Starting full data refresh for {cycle_year} cycle...")

    try:
        # =====================================================================
        # PHASE 1: EXTRACT
        # =====================================================================
        logger.info("Phase 1: Extracting data from FEC...")

        raw_files = download_fec_data(cycle_year)

        if not raw_files:
            return False, "Failed to download FEC data"

        logger.info(f"Successfully downloaded {len(raw_files)} files")

        # =====================================================================
        # PHASE 2: TRANSFORM
        # =====================================================================
        logger.info("Phase 2: Transforming and cleaning data...")

        cleaned_data = clean_and_transform(raw_files)

        if not cleaned_data:
            return False, "Failed to transform data"

        logger.info(f"Successfully transformed {len(cleaned_data)} datasets")

        # =====================================================================
        # PHASE 3: LOAD
        # =====================================================================
        logger.info("Phase 3: Loading to output CSV files...")

        output_dir = Path(__file__).parent.parent / "data" / "output"
        save_to_csv(cleaned_data, output_dir)

        logger.info("Successfully saved all output files")

        # =====================================================================
        # COMPLETION
        # =====================================================================
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Full refresh completed in {duration:.2f} seconds")

        return True, f"Data refreshed successfully in {duration:.2f}s"

    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return False, f"Error: {str(e)}"


if __name__ == "__main__":
    # For testing
    success, message = run_full_refresh()
    print(message)
