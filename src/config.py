"""
Configuration file for AI-Powered Cybersecurity Data Pipeline
Author: Pramod Prakash Jadhav
"""

from pathlib import Path

# ------------------------------------------------------------------
# Project Paths
# ------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

SQL_DIR = PROJECT_ROOT / "sql"

NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

# ------------------------------------------------------------------
# Input File
# ------------------------------------------------------------------

RAW_DATA_FILE = RAW_DATA_DIR / "cybersecurity_incidents.csv"

# ------------------------------------------------------------------
# Output Files
# ------------------------------------------------------------------

CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "clean_incidents.csv"

DATABASE_FILE = OUTPUT_DIR / "incidents.db"

SUMMARY_REPORT = OUTPUT_DIR / "summary_report.csv"

QUALITY_REPORT = OUTPUT_DIR / "cleaning_report.json"

LOG_DIR = PROJECT_ROOT / "logs"

LOG_FILE = LOG_DIR / "pipeline.log"

# ------------------------------------------------------------------
# Expected Columns
# ------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "incident_id",
    "timestamp",
    "source_ip",
    "destination_ip",
    "protocol",
    "attack_type",
    "severity",
    "country",
    "device",
    "action",
    "status",
    "description",
]

# ------------------------------------------------------------------
# Valid Severity Levels
# ------------------------------------------------------------------

VALID_SEVERITY = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

# ------------------------------------------------------------------
# Create Required Directories
# ------------------------------------------------------------------

for directory in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    LOG_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)
