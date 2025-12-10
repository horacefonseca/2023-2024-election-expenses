"""
FEC Data Extractor
Downloads bulk data files from Federal Election Commission
"""

import requests
import zipfile
import logging
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


def download_fec_data(cycle_year=2024, file_types=['committee_master']):
    """
    Download specified FEC bulk data files.

    Args:
        cycle_year (int): Election cycle (2024, 2026, etc.)
        file_types (list): List of file types to download

    Returns:
        dict: Paths to downloaded files
    """
    # FEC URL mapping
    year_suffix = cycle_year % 100  # 2024 → 24

    fec_urls = {
        'committee_master': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/cm{year_suffix}.zip',
        'committee_summary': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/webk{year_suffix}.zip',
        'candidate_master': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/cn{year_suffix}.zip',
        'candidate_summary': f'https://www.fec.gov/files/bulk-downloads/{cycle_year}/weball{year_suffix}.zip',
    }

    # Output directory
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    downloaded_files = {}

    for file_type in file_types:
        if file_type not in fec_urls:
            logger.warning(f"Unknown file type: {file_type}")
            continue

        url = fec_urls[file_type]
        zip_filename = f"{file_type}_{cycle_year}.zip"
        zip_path = raw_dir / zip_filename

        logger.info(f"Downloading {file_type} from FEC...")

        try:
            # Download with progress bar
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(zip_path, 'wb') as f, tqdm(
                desc=file_type,
                total=total_size,
                unit='B',
                unit_scale=True
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

            logger.info(f"Downloaded {zip_filename}")

            # Extract zip file
            extract_dir = raw_dir / file_type
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            logger.info(f"Extracted {file_type}")

            # Find extracted .txt file
            txt_files = list(extract_dir.glob("*.txt"))
            if txt_files:
                downloaded_files[file_type] = txt_files[0]
            else:
                logger.warning(f"No .txt file found in {extract_dir}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {file_type}: {str(e)}")
        except zipfile.BadZipFile as e:
            logger.error(f"Failed to extract {file_type}: {str(e)}")

    return downloaded_files


if __name__ == "__main__":
    # Test download
    files = download_fec_data(cycle_year=2024, file_types=['committee_master'])
    print(f"Downloaded files: {files}")
