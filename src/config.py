"""
Project Configuration

AI-Powered Cybersecurity Data Pipeline
Part 1 - Capstone Project

Author: Pramod Prakash Jadhav
"""

from pathlib import Path

# ==========================================================
# Project Metadata
# ==========================================================

PROJECT_NAME = "Cybersecurity Incident Analytics"

PIPELINE_VERSION = "2.0.0"

# ==========================================================
# CSV Settings
# ==========================================================

CSV_ENCODING = "utf-8"

CSV_SEPARATOR = ","

# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "outputs"

LOG_DIR = PROJECT_ROOT / "logs"

SQL_DIR = PROJECT_ROOT / "sql"

NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

# ==========================================================
# Create Required Directories
# ==========================================================

for directory in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    LOG_DIR,
    SQL_DIR,
    NOTEBOOK_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# ==========================================================
# Dataset Files
# ==========================================================

RAW_DATA_FILE = RAW_DATA_DIR / "cybersecurity_incident_reports.csv"

CLEAN_DATA_FILE = (
    PROCESSED_DATA_DIR / "clean_incidents.csv"
)

ENGINEERED_DATA_FILE = (
    PROCESSED_DATA_DIR / "engineered_incidents.csv"
)

DATABASE_FILE = OUTPUT_DIR / "incidents.db"

SUMMARY_REPORT_FILE = OUTPUT_DIR / "summary_report.csv"

QUALITY_REPORT_FILE = OUTPUT_DIR / "cleaning_report.json"

LOG_FILE = LOG_DIR / "pipeline.log"

# ==========================================================
# Expected Dataset Schema
# ==========================================================

EXPECTED_COLUMNS = [

    "incident_id",

    "incident_date",

    "sector",

    "region",

    "attack_type",

    "threat_actor",

    "records_affected",

    "downtime_hours",

    "ransom_demand_usd",

    "detection_time_hours",

    "severity_score",

    "response_team_size",

    "regulatory_fine_usd",

    "resolved_within_7_days",

    "data_exfiltration",

    "zero_day_used",
]

# ==========================================================
# Numeric Columns
# ==========================================================

NUMERIC_COLUMNS = [

    "records_affected",

    "downtime_hours",

    "ransom_demand_usd",

    "detection_time_hours",

    "severity_score",

    "response_team_size",

    "regulatory_fine_usd",
]

# ==========================================================
# Categorical Columns
# ==========================================================

CATEGORICAL_COLUMNS = [

    "sector",

    "region",

    "attack_type",

    "threat_actor",
]

# ==========================================================
# Boolean Columns
# ==========================================================

BOOLEAN_COLUMNS = [

    "resolved_within_7_days",

    "data_exfiltration",

    "zero_day_used",
]

# ==========================================================
# Missing Value Defaults
# ==========================================================

DEFAULT_CATEGORICAL_VALUE = "Unknown"

DEFAULT_NUMERIC_VALUE = 0

DEFAULT_BOOLEAN_VALUE = False

# ==========================================================
# Outlier Thresholds
# ==========================================================

MAX_DOWNTIME_HOURS = 720

MAX_SEVERITY_SCORE = 10

MAX_RESPONSE_TEAM_SIZE = 100

# ==========================================================
# Database
# ==========================================================

DATABASE_TABLE = "cybersecurity_incidents"

# ==========================================================
# Random Seed
# ==========================================================

RANDOM_SEED = 42
