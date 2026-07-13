"""
feature_engineering.py

AI-Powered Cybersecurity Data Pipeline

Feature Engineering Module

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config import (
    CLEAN_DATA_FILE,
    SUMMARY_REPORT,
    LOG_FILE,
)

# ---------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Production-grade Feature Engineering Pipeline.

    Responsibilities
    ----------------
    - Time-based feature extraction
    - Business-hour identification
    - Weekend identification
    - Severity scoring
    - Frequency encoding
    - Summary generation
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        logger.info("FeatureEngineer initialized.")

    # -------------------------------------------------------
    # Datetime Features
    # -------------------------------------------------------

    def create_datetime_features(self):
        """
        Create multiple time-based analytical features.
        """

        if "timestamp" not in self.df.columns:

            logger.warning(
                "Timestamp column not found."
            )

            return

        logger.info(
            "Generating datetime features..."
        )

        self.df["year"] = self.df["timestamp"].dt.year

        self.df["month"] = self.df["timestamp"].dt.month

        self.df["day"] = self.df["timestamp"].dt.day

        self.df["hour"] = self.df["timestamp"].dt.hour

        self.df["minute"] = self.df["timestamp"].dt.minute

        self.df["day_of_week"] = (
            self.df["timestamp"]
            .dt.day_name()
        )

        self.df["week_number"] = (
            self.df["timestamp"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        self.df["quarter"] = (
            self.df["timestamp"]
            .dt.quarter
        )

        logger.info(
            "Datetime feature engineering completed."
        )

    # -------------------------------------------------------
    # Weekend Feature
    # -------------------------------------------------------

    def create_weekend_flag(self):
        """
        Create binary weekend indicator.

        1 = Saturday/Sunday
        0 = Weekday
        """

        if "timestamp" not in self.df.columns:
            return

        logger.info(
            "Creating weekend feature..."
        )

        self.df["is_weekend"] = (
            self.df["timestamp"]
            .dt.weekday
            .isin([5, 6])
            .astype(int)
        )

    # -------------------------------------------------------
    # Business Hour Feature
    # -------------------------------------------------------

    def create_business_hour_flag(self):
        """
        Business Hours

        09:00 AM to 06:00 PM
        """

        if "hour" not in self.df.columns:

            self.create_datetime_features()

        logger.info(
            "Creating business hour feature..."
        )

        self.df["business_hours"] = (
            self.df["hour"]
            .between(9, 18)
            .astype(int)
        )

    # -------------------------------------------------------
    # Night Attack Indicator
    # -------------------------------------------------------

    def create_night_attack_flag(self):
        """
        Identify attacks occurring at night.

        Night:
        10 PM - 5 AM
        """

        if "hour" not in self.df.columns:

            self.create_datetime_features()

        logger.info(
            "Creating night attack indicator..."
        )

        self.df["night_attack"] = (
            (
                self.df["hour"] >= 22
            ) |
            (
                self.df["hour"] <= 5
            )
        ).astype(int)

    # -------------------------------------------------------
    # Working Shift Feature
    # -------------------------------------------------------

    def create_shift_feature(self):
        """
        Categorize incidents by shift.

        Morning : 06–13

        Evening : 14–21

        Night : 22–05
        """

        if "hour" not in self.df.columns:

            self.create_datetime_features()

        logger.info(
            "Generating shift categories..."
        )

        def get_shift(hour):

            if 6 <= hour <= 13:
                return "Morning"

            elif 14 <= hour <= 21:
                return "Evening"

            else:
                return "Night"

        self.df["shift"] = (
            self.df["hour"]
            .apply(get_shift)
        )

        logger.info(
            "Shift feature created successfully."
        )
          # -------------------------------------------------------
    # Severity Score Mapping
    # -------------------------------------------------------

    def create_severity_score(self):
        """
        Convert categorical severity into numerical scores.

        Mapping
        -------
        Low       -> 1
        Medium    -> 2
        High      -> 3
        Critical  -> 4
        """

        if "severity" not in self.df.columns:

            logger.warning("Severity column not found.")

            return

        logger.info("Creating severity score...")

        severity_map = {
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "Critical": 4,
        }

        self.df["severity_score"] = (
            self.df["severity"]
            .map(severity_map)
            .fillna(2)
            .astype(int)
        )

        logger.info("Severity score created successfully.")

    # -------------------------------------------------------
    # Attack Frequency Encoding
    # -------------------------------------------------------

    def create_attack_frequency(self):
        """
        Create frequency encoding for attack types.
        """

        if "attack_type" not in self.df.columns:

            logger.warning("Attack type column not found.")

            return

        logger.info("Generating attack frequency...")

        attack_frequency = (
            self.df["attack_type"]
            .value_counts()
            .to_dict()
        )

        self.df["attack_frequency"] = (
            self.df["attack_type"]
            .map(attack_frequency)
            .astype(int)
        )

        logger.info("Attack frequency feature created.")

    # -------------------------------------------------------
    # Country Frequency Encoding
    # -------------------------------------------------------

    def create_country_frequency(self):
        """
        Frequency encoding for country column.
        """

        if "country" not in self.df.columns:

            logger.warning("Country column not found.")

            return

        logger.info("Generating country frequency...")

        country_frequency = (
            self.df["country"]
            .value_counts()
            .to_dict()
        )

        self.df["country_frequency"] = (
            self.df["country"]
            .map(country_frequency)
            .astype(int)
        )

        logger.info("Country frequency feature created.")

    # -------------------------------------------------------
    # Device Frequency Encoding
    # -------------------------------------------------------

    def create_device_frequency(self):
        """
        Frequency encoding for device column.
        """

        if "device" not in self.df.columns:

            logger.warning("Device column not found.")

            return

        logger.info("Generating device frequency...")

        device_frequency = (
            self.df["device"]
            .value_counts()
            .to_dict()
        )

        self.df["device_frequency"] = (
            self.df["device"]
            .map(device_frequency)
            .astype(int)
        )

        logger.info("Device frequency feature created.")

    # -------------------------------------------------------
    # Action Frequency Encoding
    # -------------------------------------------------------

    def create_action_frequency(self):
        """
        Frequency encoding for action column.
        """

        if "action" not in self.df.columns:

            logger.warning("Action column not found.")

            return

        logger.info("Generating action frequency...")

        action_frequency = (
            self.df["action"]
            .value_counts()
            .to_dict()
        )

        self.df["action_frequency"] = (
            self.df["action"]
            .map(action_frequency)
            .astype(int)
        )

        logger.info("Action frequency feature created.")
          # -------------------------------------------------------
    # Protocol Encoding
    # -------------------------------------------------------

    def encode_protocol(self):
        """
        Encode protocol names into integer values.

        Unknown protocols receive code 0.
        """

        if "protocol" not in self.df.columns:

            logger.warning("Protocol column not found.")

            return

        logger.info("Encoding protocol column...")

        protocol_map = {
            "TCP": 1,
            "UDP": 2,
            "ICMP": 3,
            "HTTP": 4,
            "HTTPS": 5,
            "FTP": 6,
            "SSH": 7,
            "SMTP": 8,
            "DNS": 9,
        }

        self.df["protocol"] = (
            self.df["protocol"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

        self.df["protocol_code"] = (
            self.df["protocol"]
            .map(protocol_map)
            .fillna(0)
            .astype(int)
        )

        logger.info("Protocol encoding completed.")

    # -------------------------------------------------------
    # Status Encoding
    # -------------------------------------------------------

    def encode_status(self):
        """
        Encode incident status.
        """

        if "status" not in self.df.columns:

            logger.warning("Status column not found.")

            return

        logger.info("Encoding status column...")

        status_map = {
            "Open": 1,
            "In Progress": 2,
            "Resolved": 3,
            "Closed": 4,
            "Unknown": 0,
        }

        self.df["status"] = (
            self.df["status"]
            .astype(str)
            .str.title()
            .str.strip()
        )

        self.df["status_code"] = (
            self.df["status"]
            .map(status_map)
            .fillna(0)
            .astype(int)
        )

    # -------------------------------------------------------
    # Risk Score
    # -------------------------------------------------------

    def create_risk_score(self):
        """
        Generate a weighted risk score.

        Formula
        -------
        Risk Score =
            Severity Score
            + Night Attack
            + Weekend
            + Business Hour
        """

        logger.info("Calculating risk score...")

        required = [
            "severity_score",
            "night_attack",
            "is_weekend",
            "business_hours",
        ]

        for column in required:

            if column not in self.df.columns:

                logger.warning(
                    "%s missing. Creating default values.",
                    column,
                )

                self.df[column] = 0

        self.df["risk_score"] = (
            self.df["severity_score"] * 2
            + self.df["night_attack"]
            + self.df["is_weekend"]
            + self.df["business_hours"]
        )

        logger.info("Risk score generated.")

    # -------------------------------------------------------
    # High Risk Flag
    # -------------------------------------------------------

    def create_high_risk_flag(self):
        """
        Binary indicator for high-risk incidents.
        """

        if "risk_score" not in self.df.columns:

            self.create_risk_score()

        logger.info("Generating High Risk flag...")

        self.df["high_risk"] = (
            self.df["risk_score"] >= 7
        ).astype(int)

    # -------------------------------------------------------
    # Critical Incident Flag
    # -------------------------------------------------------

    def create_critical_flag(self):
        """
        Identify critical incidents.
        """

        if "severity" not in self.df.columns:

            return

        logger.info("Generating Critical Incident flag...")

        self.df["critical_incident"] = (
            self.df["severity"]
            .eq("Critical")
            .astype(int)
        )

    # -------------------------------------------------------
    # Peak Hour Indicator
    # -------------------------------------------------------

    def create_peak_hour_flag(self):
        """
        Peak attack hours:
        10 AM–12 PM and 6 PM–9 PM
        """

        if "hour" not in self.df.columns:

            self.create_datetime_features()

        logger.info("Generating Peak Hour feature...")

        self.df["peak_hour"] = (
            self.df["hour"].between(10, 12)
            |
            self.df["hour"].between(18, 21)
        ).astype(int)

    # -------------------------------------------------------
    # Business Impact Score
    # -------------------------------------------------------

    def create_business_impact_score(self):
        """
        Estimate business impact score.

        Formula
        -------
        (Severity × 2)
        + Critical Flag
        + High Risk Flag
        """

        logger.info("Calculating Business Impact Score...")

        required = [
            "severity_score",
            "critical_incident",
            "high_risk",
        ]

        for column in required:

            if column not in self.df.columns:

                self.df[column] = 0

        self.df["business_impact_score"] = (
            self.df["severity_score"] * 2
            + self.df["critical_incident"] * 3
            + self.df["high_risk"] * 2
        )

        logger.info("Business Impact Score generated.")
      
