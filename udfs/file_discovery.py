"""
File Discovery Module - Automated daily file detection
Sistema AmFi - Descoberta automática de arquivos diários
"""

import os
import re
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

# File patterns for daily data
CSV_PATTERN = r'AcompanhamentoDeOportunidades-(\d{4}-\d{2}-\d{2} \d{2}_\d{2}_\d{2}) -\d{4}\.csv'
XLSX_PATTERN = r'Carteira Global (\d{4}-\d{2}-\d{2} \d{6})\.xlsx'

# Default data directories
DEFAULT_CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'csv')
DEFAULT_XLSX_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'xlsx')


def parse_csv_timestamp(filename: str) -> Optional[datetime]:
    """
    Extract timestamp from CSV filename
    
    Args:
        filename: CSV filename
        
    Returns:
        datetime object or None if pattern doesn't match
    """
    match = re.match(CSV_PATTERN, filename)
    if match:
        timestamp_str = match.group(1)
        try:
            # Parse format: YYYY-MM-DD HH_MM_SS
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H_%M_%S')
        except ValueError:
            logger.error(f"Failed to parse CSV timestamp: {timestamp_str}")
    return None


def parse_xlsx_timestamp(filename: str) -> Optional[datetime]:
    """
    Extract timestamp from XLSX filename
    
    Args:
        filename: XLSX filename
        
    Returns:
        datetime object or None if pattern doesn't match
    """
    match = re.match(XLSX_PATTERN, filename)
    if match:
        timestamp_str = match.group(1)
        try:
            # Parse format: YYYY-MM-DD HHMMSS
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H%M%S')
        except ValueError:
            logger.error(f"Failed to parse XLSX timestamp: {timestamp_str}")
    return None


def get_latest_csv(directory: str = DEFAULT_CSV_DIR, days_back: int = 7) -> Optional[str]:
    """
    Find the most recent CSV file in directory
    
    Args:
        directory: Directory to search
        days_back: Maximum days to look back
        
    Returns:
        Full path to latest CSV file or None
    """
    if not os.path.exists(directory):
        logger.warning(f"CSV directory not found: {directory}")
        return None
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    files_with_dates: List[Tuple[str, datetime]] = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            timestamp = parse_csv_timestamp(filename)
            if timestamp and timestamp >= cutoff_date:
                files_with_dates.append((filename, timestamp))
    
    if not files_with_dates:
        logger.warning(f"No recent CSV files found in {directory}")
        return None
    
    # Sort by timestamp descending and get the latest
    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    latest_file = files_with_dates[0][0]
    
    full_path = os.path.join(directory, latest_file)
    logger.info(f"Found latest CSV: {latest_file} ({files_with_dates[0][1].strftime('%Y-%m-%d %H:%M:%S')})")
    return full_path


def get_latest_xlsx(directory: str = DEFAULT_XLSX_DIR, days_back: int = 7) -> Optional[str]:
    """
    Find the most recent XLSX file in directory
    
    Args:
        directory: Directory to search
        days_back: Maximum days to look back
        
    Returns:
        Full path to latest XLSX file or None
    """
    if not os.path.exists(directory):
        logger.warning(f"XLSX directory not found: {directory}")
        return None
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    files_with_dates: List[Tuple[str, datetime]] = []
    
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx'):
            timestamp = parse_xlsx_timestamp(filename)
            if timestamp and timestamp >= cutoff_date:
                files_with_dates.append((filename, timestamp))
    
    if not files_with_dates:
        logger.warning(f"No recent XLSX files found in {directory}")
        return None
    
    # Sort by timestamp descending and get the latest
    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    latest_file = files_with_dates[0][0]
    
    full_path = os.path.join(directory, latest_file)
    logger.info(f"Found latest XLSX: {latest_file} ({files_with_dates[0][1].strftime('%Y-%m-%d %H:%M:%S')})")
    return full_path


def get_daily_files(date: Optional[datetime] = None) -> Dict[str, Optional[str]]:
    """
    Get both CSV and XLSX files for a specific date or latest available
    
    Args:
        date: Target date (default: today)
        
    Returns:
        Dictionary with 'csv' and 'xlsx' paths
    """
    target_date = date or datetime.now()
    result = {
        'csv': None,
        'xlsx': None,
        'csv_date': None,
        'xlsx_date': None
    }
    
    # Find files matching the target date
    if os.path.exists(DEFAULT_CSV_DIR):
        for filename in os.listdir(DEFAULT_CSV_DIR):
            if filename.endswith('.csv'):
                timestamp = parse_csv_timestamp(filename)
                if timestamp and timestamp.date() == target_date.date():
                    result['csv'] = os.path.join(DEFAULT_CSV_DIR, filename)
                    result['csv_date'] = timestamp
                    break
    
    if os.path.exists(DEFAULT_XLSX_DIR):
        for filename in os.listdir(DEFAULT_XLSX_DIR):
            if filename.endswith('.xlsx'):
                timestamp = parse_xlsx_timestamp(filename)
                if timestamp and timestamp.date() == target_date.date():
                    result['xlsx'] = os.path.join(DEFAULT_XLSX_DIR, filename)
                    result['xlsx_date'] = timestamp
                    break
    
    # If no files found for target date, get latest available
    if not result['csv']:
        result['csv'] = get_latest_csv()
    if not result['xlsx']:
        result['xlsx'] = get_latest_xlsx()
    
    return result


def check_data_freshness(max_age_hours: int = 24) -> Dict[str, bool]:
    """
    Check if latest data files are fresh enough
    
    Args:
        max_age_hours: Maximum acceptable age in hours
        
    Returns:
        Dictionary with freshness status for each file type
    """
    files = get_daily_files()
    current_time = datetime.now()
    max_age = timedelta(hours=max_age_hours)
    
    result = {
        'csv_fresh': False,
        'xlsx_fresh': False,
        'csv_age': None,
        'xlsx_age': None
    }
    
    # Check CSV freshness
    if files['csv']:
        csv_file = os.path.basename(files['csv'])
        csv_timestamp = parse_csv_timestamp(csv_file)
        if csv_timestamp:
            age = current_time - csv_timestamp
            result['csv_age'] = age
            result['csv_fresh'] = age <= max_age
    
    # Check XLSX freshness
    if files['xlsx']:
        xlsx_file = os.path.basename(files['xlsx'])
        xlsx_timestamp = parse_xlsx_timestamp(xlsx_file)
        if xlsx_timestamp:
            age = current_time - xlsx_timestamp
            result['xlsx_age'] = age
            result['xlsx_fresh'] = age <= max_age
    
    return result


def list_available_dates(days_back: int = 30) -> Dict[str, List[datetime]]:
    """
    List all available data dates within the specified period
    
    Args:
        days_back: Number of days to look back
        
    Returns:
        Dictionary with lists of available dates for CSV and XLSX
    """
    cutoff_date = datetime.now() - timedelta(days=days_back)
    result = {
        'csv_dates': [],
        'xlsx_dates': []
    }
    
    # Scan CSV files
    if os.path.exists(DEFAULT_CSV_DIR):
        for filename in os.listdir(DEFAULT_CSV_DIR):
            if filename.endswith('.csv'):
                timestamp = parse_csv_timestamp(filename)
                if timestamp and timestamp >= cutoff_date:
                    result['csv_dates'].append(timestamp)
    
    # Scan XLSX files
    if os.path.exists(DEFAULT_XLSX_DIR):
        for filename in os.listdir(DEFAULT_XLSX_DIR):
            if filename.endswith('.xlsx'):
                timestamp = parse_xlsx_timestamp(filename)
                if timestamp and timestamp >= cutoff_date:
                    result['xlsx_dates'].append(timestamp)
    
    # Sort dates
    result['csv_dates'].sort(reverse=True)
    result['xlsx_dates'].sort(reverse=True)
    
    return result


# Excel-exposed functions for direct use in formulas
def get_latest_csv_path() -> str:
    """Excel UDF: Returns path to latest CSV file"""
    path = get_latest_csv()
    return path if path else "No CSV file found"


def get_latest_xlsx_path() -> str:
    """Excel UDF: Returns path to latest XLSX file"""
    path = get_latest_xlsx()
    return path if path else "No XLSX file found"


def get_xlsx_by_date(target_date: str, directory: str = DEFAULT_XLSX_DIR) -> Optional[str]:
    """
    Find XLSX file for specific date
    
    Args:
        target_date: Date string in format 'YYYY-MM-DD' or datetime object
        directory: Directory to search
        
    Returns:
        Full path to XLSX file for that date or None
    """
    if not os.path.exists(directory):
        logger.warning(f"XLSX directory not found: {directory}")
        return None
    
    # Parse target date
    try:
        if isinstance(target_date, str):
            target_dt = datetime.strptime(target_date, '%Y-%m-%d')
        else:
            target_dt = target_date
    except ValueError:
        logger.error(f"Invalid date format: {target_date}. Expected YYYY-MM-DD")
        return None
    
    # Search for files matching the date
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx'):
            timestamp = parse_xlsx_timestamp(filename)
            if timestamp and timestamp.date() == target_dt.date():
                full_path = os.path.join(directory, filename)
                logger.info(f"Found XLSX for date {target_date}: {filename}")
                return full_path
    
    logger.warning(f"No XLSX file found for date: {target_date}")
    return None


def extract_file_date(file_path: str) -> Optional[datetime]:
    """
    Extract date from filename
    
    Args:
        file_path: Full path to file
        
    Returns:
        datetime object or None
    """
    filename = os.path.basename(file_path)
    
    # Try XLSX pattern first
    timestamp = parse_xlsx_timestamp(filename)
    if timestamp:
        return timestamp
    
    # Try CSV pattern
    timestamp = parse_csv_timestamp(filename)
    if timestamp:
        return timestamp
    
    return None


def check_data_status() -> str:
    """Excel UDF: Returns data freshness status"""
    freshness = check_data_freshness()
    
    status_parts = []
    if freshness['csv_fresh']:
        status_parts.append("CSV: Fresh")
    else:
        age = freshness['csv_age']
        if age:
            hours = int(age.total_seconds() / 3600)
            status_parts.append(f"CSV: {hours}h old")
        else:
            status_parts.append("CSV: Not found")
    
    if freshness['xlsx_fresh']:
        status_parts.append("XLSX: Fresh")
    else:
        age = freshness['xlsx_age']
        if age:
            hours = int(age.total_seconds() / 3600)
            status_parts.append(f"XLSX: {hours}h old")
        else:
            status_parts.append("XLSX: Not found")
    
    return " | ".join(status_parts)