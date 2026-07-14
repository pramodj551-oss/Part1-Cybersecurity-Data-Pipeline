"""
Feature Engineering Module

Creates analytical and machine learning features
from the cleaned cybersecurity incidents dataset.

Author:
Pramod Prakash Jadhav
"""

from __future__ import annotations

import logging

import pandas as pd

import numpy as np

from src.config import (
    CLEAN_DATA_FILE,
    LOG_FILE,
    SUMMARY_REPORT_FILE,
)

# ==========================================================
# Logger Configuration
# ==========================================================

logger = logging.getLogger(__name__)

if not logger.handlers:

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


class FeatureEngineer:
    """
    Production Feature Engineering Pipeline.

    Responsibilities
    ----------------
    - Date Feature Extraction
    - Financial Feature Engineering
    - Operational Metrics
    - Risk Feature Creation
    - Frequency Encoding
    """

    def __init__(self, dataframe: pd.DataFrame):

        self.df = dataframe.copy()

        logger.info(
            "FeatureEngineer initialized."
        )

    # ======================================================
    # Date Features
    # ======================================================

    def create_date_features(self):
        """
        Extract useful features from incident_date.
        """

        if "incident_date" not in self.df.columns:

            logger.warning(
                "incident_date column not found."
            )

            return

        logger.info(
            "Creating date features..."
        )

        self.df["incident_year"] = (
            self.df["incident_date"].dt.year
        )

        self.df["incident_month"] = (
            self.df["incident_date"].dt.month
        )

        self.df["incident_day"] = (
            self.df["incident_date"].dt.day
        )

        self.df["incident_week"] = (
            self.df["incident_date"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        self.df["incident_quarter"] = (
            self.df["incident_date"].dt.quarter
        )

        self.df["incident_weekday"] = (
            self.df["incident_date"]
            .dt.day_name()
        )

        logger.info(
            "Date features created successfully."
        )

    # ======================================================
    # Weekend Indicator
    # ======================================================

    def create_weekend_flag(self):
        """
        Create weekend indicator.

        Saturday = 1
        Sunday = 1
        Weekday = 0
        """

        if "incident_date" not in self.df.columns:

            return

        logger.info(
            "Creating weekend flag..."
        )

        self.df["is_weekend"] = (
            self.df["incident_date"]
            .dt.weekday
            .isin([5, 6])
            .astype(int)
        )

    # ======================================================
    # Month Name
    # ======================================================

    def create_month_name(self):
        """
        Create month name feature.
        """

        if "incident_date" not in self.df.columns:

            return

        logger.info(
            "Creating month name..."
        )

        self.df["month_name"] = (
            self.df["incident_date"]
            .dt.month_name()
        )

    # ======================================================
    # Incident Age
    # ======================================================

    def create_incident_age(self):
        """
        Calculate age of incident in days
        from latest incident available.
        """

        if "incident_date" not in self.df.columns:

            return

        logger.info(
            "Calculating incident age..."
        )

        latest_date = (
            self.df["incident_date"]
            .max()
        )

        self.df["incident_age_days"] = (
            latest_date
            - self.df["incident_date"]
        ).dt.days

        logger.info(
            "Incident age calculated."
        )

    # ======================================================
    # Quarterly Indicator
    # ======================================================

    def create_quarter_label(self):
        """
        Create quarter labels.

        Example

        Q1
        Q2
        Q3
        Q4
        """

        if "incident_quarter" not in self.df.columns:

            self.create_date_features()

        logger.info(
            "Creating quarter labels..."
        )

        self.df["quarter_label"] = (
            "Q"
            + self.df["incident_quarter"]
            .astype(str)
        )

        logger.info(
            "Quarter labels created."
        )
            # ======================================================
    # Ransom Per Record
    # ======================================================

    def create_ransom_per_record(self):
        """
        Calculate ransom demand per affected record.
        """

        logger.info("Creating ransom_per_record feature...")

        self.df["ransom_per_record"] = (
            self.df["ransom_demand_usd"]
            /
            self.df["records_affected"].replace(0, 1)
        ).round(2)

        logger.info("ransom_per_record created.")

    # ======================================================
    # Regulatory Fine Per Record
    # ======================================================

    def create_fine_per_record(self):
        """
        Calculate regulatory fine per affected record.
        """

        logger.info("Creating fine_per_record feature...")

        self.df["fine_per_record"] = (
            self.df["regulatory_fine_usd"]
            /
            self.df["records_affected"].replace(0, 1)
        ).round(2)

        logger.info("fine_per_record created.")

    # ======================================================
    # Total Financial Impact
    # ======================================================

    def create_total_financial_impact(self):
        """
        Calculate total financial impact.

        Formula:
        ransom + regulatory fine
        """

        logger.info("Creating total_financial_impact...")

        self.df["total_financial_impact"] = (

            self.df["ransom_demand_usd"]

            +

            self.df["regulatory_fine_usd"]

        )

        logger.info(
            "total_financial_impact created."
        )

    # ======================================================
    # Downtime Per Record
    # ======================================================

    def create_downtime_per_record(self):
        """
        Average downtime per affected record.
        """

        logger.info(
            "Creating downtime_per_record..."
        )

        self.df["downtime_per_record"] = (

            self.df["downtime_hours"]

            /

            self.df["records_affected"]
            .replace(0, 1)

        ).round(4)

        logger.info(
            "downtime_per_record created."
        )

    # ======================================================
    # Response Efficiency Score
    # ======================================================

    def create_response_efficiency(self):
        """
        Calculate response efficiency.

        Formula:

        response_team_size
        ------------------
        detection_time_hours
        """

        logger.info(
            "Creating response_efficiency..."
        )

        self.df["response_efficiency"] = (

            self.df["response_team_size"]

            /

            self.df["detection_time_hours"]
            .replace(0, 1)

        ).round(2)

        logger.info(
            "response_efficiency created."
        )

    # ======================================================
    # Detection Speed Category
    # ======================================================

    def create_detection_speed_category(self):
        """
        Categorize incident detection speed.
        """

        logger.info(
            "Creating detection speed category..."
        )

        bins = [

            -1,

            6,

            24,

            72,

            float("inf")

        ]

        labels = [

            "Very Fast",

            "Fast",

            "Moderate",

            "Slow"

        ]

        self.df["detection_speed"] = pd.cut(

            self.df["detection_time_hours"],

            bins=bins,

            labels=labels,

        )

        logger.info(
            "Detection speed category created."
        )

    # ======================================================
    # Incident Cost Category
    # ======================================================

    def create_incident_cost_category(self):
        """
        Categorize incidents
        based on financial impact.
        """

        logger.info(
            "Creating incident cost category..."
        )

        self.df["incident_cost_category"] = pd.qcut(

            self.df["total_financial_impact"],

            q=4,

            labels=[
                "Low",
                "Medium",
                "High",
                "Critical",
            ],

            duplicates="drop",

        )

        logger.info(
            "Incident cost category created."
        )
            # ======================================================
    # High Severity Flag
    # ======================================================

    def create_high_severity_flag(self):
        """
        Create binary flag for high severity incidents.
        """

        logger.info("Creating high severity flag...")

        self.df["high_severity_flag"] = (
            self.df["severity_score"] >= 8
        ).astype(int)

        logger.info("high_severity_flag created.")

    # ======================================================
    # High Ransom Flag
    # ======================================================

    def create_high_ransom_flag(self):
        """
        Flag incidents having ransom demand
        above the dataset median.
        """

        logger.info("Creating high ransom flag...")

        threshold = self.df[
            "ransom_demand_usd"
        ].median()

        self.df["high_ransom_flag"] = (
            self.df["ransom_demand_usd"] >= threshold
        ).astype(int)

        logger.info("high_ransom_flag created.")

    # ======================================================
    # Large Breach Flag
    # ======================================================

    def create_large_breach_flag(self):
        """
        Flag incidents affecting
        unusually high number of records.
        """

        logger.info("Creating large breach flag...")

        threshold = self.df[
            "records_affected"
        ].median()

        self.df["large_breach_flag"] = (
            self.df["records_affected"] >= threshold
        ).astype(int)

        logger.info("large_breach_flag created.")

    # ======================================================
    # Long Downtime Flag
    # ======================================================

    def create_long_downtime_flag(self):
        """
        Flag incidents having long downtime.
        """

        logger.info("Creating long downtime flag...")

        threshold = self.df[
            "downtime_hours"
        ].median()

        self.df["long_downtime_flag"] = (
            self.df["downtime_hours"] >= threshold
        ).astype(int)

        logger.info("long_downtime_flag created.")

    # ======================================================
    # Sector Frequency Encoding
    # ======================================================

    def create_sector_frequency(self):
        """
        Frequency encode sector column.
        """

        logger.info("Creating sector frequency...")

        frequency = (
            self.df["sector"]
            .value_counts()
            .to_dict()
        )

        self.df["sector_frequency"] = (
            self.df["sector"]
            .map(frequency)
        )

    # ======================================================
    # Region Frequency Encoding
    # ======================================================

    def create_region_frequency(self):
        """
        Frequency encode region column.
        """

        logger.info("Creating region frequency...")

        frequency = (
            self.df["region"]
            .value_counts()
            .to_dict()
        )

        self.df["region_frequency"] = (
            self.df["region"]
            .map(frequency)
        )

    # ======================================================
    # Attack Type Frequency
    # ======================================================

    def create_attack_frequency(self):
        """
        Frequency encode attack type.
        """

        logger.info("Creating attack frequency...")

        frequency = (
            self.df["attack_type"]
            .value_counts()
            .to_dict()
        )

        self.df["attack_frequency"] = (
            self.df["attack_type"]
            .map(frequency)
        )

    # ======================================================
    # Threat Actor Frequency
    # ======================================================

    def create_threat_actor_frequency(self):
        """
        Frequency encode threat actor.
        """

        logger.info("Creating threat actor frequency...")

        frequency = (
            self.df["threat_actor"]
            .value_counts()
            .to_dict()
        )

        self.df["threat_actor_frequency"] = (
            self.df["threat_actor"]
            .map(frequency)
        )

    # ======================================================
    # Composite Risk Score
    # ======================================================

    def create_risk_score(self):
        """
        Calculate composite cybersecurity risk score.
        """

        logger.info("Creating risk score...")

        self.df["risk_score"] = (

            self.df["severity_score"] * 3

            +

            self.df["zero_day_used"].astype(int) * 2

            +

            self.df["data_exfiltration"].astype(int) * 2

            +

            self.df["high_ransom_flag"]

            +

            self.df["large_breach_flag"]

        )

        logger.info("risk_score created.")

    # ======================================================
    # Incident Complexity Score
    # ======================================================

    np.log(value)
    
    def create_incident_complexity_score(self):
        """
        Estimate operational complexity of incident.
        """

        logger.info(
            "Creating incident complexity score..."
        )

        self.df["incident_complexity_score"] = (

            self.df["severity_score"]

            +

            (
                self.df["records_affected"] + 1
            ).apply(
                lambda value: pd.np.log(value)
            )

            +

            self.df["downtime_hours"] / 24

            +

            self.df["detection_time_hours"] / 24

        ).round(2)

        logger.info(
            "incident_complexity_score created."
    )
        
