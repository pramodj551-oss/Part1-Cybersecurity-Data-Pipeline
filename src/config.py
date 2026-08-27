"""
Central configuration for the Cybersecurity Incident Analytics pipeline.

All project paths and validation constants are defined here so that the
pipeline does not depend on the current working directory.
"""

from pathlib import Path

PROJECT_NAME = "Cybersecurity Incident Analytics"
PIPELINE_VERSION = "2.0.0"

# CSV settings
CSV_ENCODING = "utf-8"
CSV_SEPARATOR = ","

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
LOG_DIR = PROJECT_ROOT / "logs"

# Create only directories that are actually used by the pipeline.
for directory in (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    LOG_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# Dataset files
RAW_DATA_FILE = RAW_DATA_DIR / "cybersecurity_incident_reports.csv"
CLEAN_DATA_FILE = PROCESSED_DATA_DIR / "clean_incidents_reports.csv"
ENGINEERED_DATA_FILE = PROCESSED_DATA_DIR / "engineered_incidents.csv"
DATABASE_FILE = OUTPUT_DIR / "incidents.db"
SUMMARY_REPORT_FILE = OUTPUT_DIR / "summary_report.csv"
QUALITY_REPORT_FILE = OUTPUT_DIR / "cleaning_report.json"
LOG_FILE = LOG_DIR / "pipeline.log"

# Expected dataset schema
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

NUMERIC_COLUMNS = [
    "records_affected",
    "downtime_hours",
    "ransom_demand_usd",
    "detection_time_hours",
    "severity_score",
    "response_team_size",
    "regulatory_fine_usd",
]

CATEGORICAL_COLUMNS = [
    "sector",
    "region",
    "attack_type",
    "threat_actor",
]

BOOLEAN_COLUMNS = [
    "resolved_within_7_days",
    "data_exfiltration",
    "zero_day_used",
]

# Missing-value defaults
DEFAULT_CATEGORICAL_VALUE = "Unknown"
DEFAULT_NUMERIC_VALUE = 0
DEFAULT_BOOLEAN_VALUE = False

# Data-quality limits
MAX_DOWNTIME_HOURS = 720
MAX_SEVERITY_SCORE = 10
MAX_RESPONSE_TEAM_SIZE = 100

# Database
DATABASE_TABLE = "cybersecurity_incidents"

# Reproducibility
RANDOM_SEED = 42
# Fixed reference date used by deterministic feature engineering.
# Override deliberately for a new analysis period rather than relying on
# the machine's current date/time.
ANALYSIS_REFERENCE_DATE = "2025-12-31"
