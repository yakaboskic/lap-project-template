"""
File utility functions for LAP workflows
Common file I/O operations and validations
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

def validate_input_file(file_path: str, required_columns: Optional[List[str]] = None) -> None:
    """
    Validate that input file exists and has expected structure

    Args:
        file_path: Path to input file
        required_columns: List of required column names (for tabular data)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is empty or missing required columns
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if path.stat().st_size == 0:
        raise ValueError(f"Input file is empty: {file_path}")

    # Additional validation for tabular data
    if required_columns and file_path.endswith(('.tsv', '.csv')):
        sep = '\t' if file_path.endswith('.tsv') else ','
        try:
            df = pd.read_csv(file_path, sep=sep, nrows=1)  # Just read header
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
        except Exception as e:
            raise ValueError(f"Error reading tabular file {file_path}: {e}")

    logging.info(f"Input validation passed: {file_path}")

def safe_read_json(file_path: str) -> Dict[str, Any]:
    """
    Safely read JSON file with error handling

    Args:
        file_path: Path to JSON file

    Returns:
        Dictionary containing JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is malformed
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logging.info(f"Successfully loaded JSON: {file_path}")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in {file_path}: {e}")

def safe_write_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Safely write JSON file with directory creation

    Args:
        data: Dictionary to write as JSON
        file_path: Output file path
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    logging.info(f"JSON written to: {file_path}")

def safe_read_table(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Safely read tabular data with automatic delimiter detection

    Args:
        file_path: Path to tabular file
        **kwargs: Additional arguments passed to pd.read_csv

    Returns:
        DataFrame containing the data
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Table file not found: {file_path}")

    # Auto-detect separator
    sep = '\t' if file_path.endswith('.tsv') else ','
    if 'sep' not in kwargs:
        kwargs['sep'] = sep

    try:
        df = pd.read_csv(file_path, **kwargs)
        logging.info(f"Successfully loaded table: {file_path} ({len(df)} rows, {len(df.columns)} columns)")
        return df
    except Exception as e:
        raise ValueError(f"Error reading table {file_path}: {e}")

def safe_write_table(df: pd.DataFrame, file_path: str, **kwargs) -> None:
    """
    Safely write tabular data with directory creation

    Args:
        df: DataFrame to write
        file_path: Output file path
        **kwargs: Additional arguments passed to df.to_csv
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Auto-detect separator
    sep = '\t' if file_path.endswith('.tsv') else ','
    if 'sep' not in kwargs:
        kwargs['sep'] = sep

    if 'index' not in kwargs:
        kwargs['index'] = False

    df.to_csv(file_path, **kwargs)
    logging.info(f"Table written to: {file_path} ({len(df)} rows, {len(df.columns)} columns)")

def create_output_directory(file_path: str) -> Path:
    """
    Create output directory for a file if it doesn't exist

    Args:
        file_path: Path to output file

    Returns:
        Path object for the created directory
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.parent

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get basic information about a file

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file information
    """
    path = Path(file_path)

    if not path.exists():
        return {'exists': False}

    info = {
        'exists': True,
        'size_bytes': path.stat().st_size,
        'is_empty': path.stat().st_size == 0,
        'extension': path.suffix,
        'name': path.name,
        'parent': str(path.parent)
    }

    # Add row/column info for tabular files
    if path.suffix in ['.tsv', '.csv'] and not info['is_empty']:
        try:
            sep = '\t' if path.suffix == '.tsv' else ','
            df = pd.read_csv(file_path, sep=sep)
            info['n_rows'] = len(df)
            info['n_columns'] = len(df.columns)
            info['columns'] = list(df.columns)
        except Exception:
            info['table_read_error'] = True

    return info

def ensure_executable(script_path: str) -> None:
    """
    Ensure a script file is executable

    Args:
        script_path: Path to script file
    """
    path = Path(script_path)
    if path.exists():
        # Add execute permission for user
        current_mode = path.stat().st_mode
        path.chmod(current_mode | 0o100)
        logging.info(f"Made executable: {script_path}")