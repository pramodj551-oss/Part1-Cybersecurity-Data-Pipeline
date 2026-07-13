    # -------------------------------------------------------
    # Missing Value Handling
    # -------------------------------------------------------

    def handle_missing_values(self):
        """
        Handle missing values using column-specific rules.

        Rules
        -----
        - description -> ""
        - status -> "Unknown"
        - action -> "Unknown"
        - protocol -> "Unknown"
        - attack_type -> "Unknown"
        - country -> "Unknown"
        - device -> "Unknown"
        - severity -> "Medium"
        """

        logger.info("Handling missing values...")

        missing_before = int(self.df.isna().sum().sum())

        default_values = {
            "description": "",
            "status": "Unknown",
            "action": "Unknown",
            "protocol": "Unknown",
            "attack_type": "Unknown",
            "country": "Unknown",
            "device": "Unknown",
            "severity": "Medium",
        }

        for column, value in default_values.items():

            if column in self.df.columns:

                self.df[column] = self.df[column].fillna(value)

        if "incident_id" in self.df.columns:

            self.df.dropna(
                subset=["incident_id"],
                inplace=True,
            )

        if "timestamp" in self.df.columns:

            self.df.dropna(
                subset=["timestamp"],
                inplace=True,
            )

        missing_after = int(self.df.isna().sum().sum())

        filled = missing_before - missing_after

        self.report["missing_values_filled"] = filled

        logger.info(
            "Missing values handled. Filled: %d",
            filled,
        )

    # -------------------------------------------------------
    # Duplicate Removal
    # -------------------------------------------------------

    def remove_duplicates(self):
        """
        Remove duplicate rows.

        Priority:
        1. Duplicate incident_id
        2. Complete duplicate rows
        """

        logger.info("Removing duplicates...")

        before = len(self.df)

        if "incident_id" in self.df.columns:

            self.df.drop_duplicates(
                subset=["incident_id"],
                keep="first",
                inplace=True,
            )

        self.df.drop_duplicates(
            inplace=True,
        )

        removed = before - len(self.df)

        self.report["duplicates_removed"] = removed

        logger.info(
            "%d duplicate rows removed.",
            removed,
        )

    # -------------------------------------------------------
    # Timestamp Cleaning
    # -------------------------------------------------------

    def normalize_timestamp(self):
        """
        Convert timestamps into UTC datetime format.

        Invalid timestamps are removed.
        """

        if "timestamp" not in self.df.columns:

            logger.warning(
                "Timestamp column not found."
            )

            return

        logger.info("Normalizing timestamps...")

        self.df["timestamp"] = self._safe_datetime(
            self.df["timestamp"]
        )

        before = len(self.df)

        self.df.dropna(
            subset=["timestamp"],
            inplace=True,
        )

        removed = before - len(self.df)

        logger.info(
            "%d invalid timestamps removed.",
            removed,
        )

        self.df["year"] = self.df["timestamp"].dt.year

        self.df["month"] = self.df["timestamp"].dt.month

        self.df["day"] = self.df["timestamp"].dt.day

        self.df["hour"] = self.df["timestamp"].dt.hour

        logger.info(
            "Timestamp normalization completed."
        )

    # -------------------------------------------------------
    # Dataset Statistics
    # -------------------------------------------------------

    def dataset_statistics(self):
        """
        Log dataset statistics after cleaning.
        """

        logger.info("Generating cleaning statistics...")

        logger.info(
            "Rows: %d",
            len(self.df),
        )

        logger.info(
            "Columns: %d",
            len(self.df.columns),
        )

        logger.info(
            "Remaining Missing Values: %d",
            int(self.df.isna().sum().sum()),
        )

        print("\n" + "=" * 60)
        print("DATA CLEANING SUMMARY")
        print("=" * 60)

        print(f"Rows                : {len(self.df)}")
        print(f"Columns             : {len(self.df.columns)}")
        print(
            f"Duplicates Removed  : {self.report['duplicates_removed']}"
        )
        print(
            f"Missing Values Filled : {self.report['missing_values_filled']}"
        )
        print(
            f"Remaining Missing Values : {int(self.df.isna().sum().sum())}"
        )
        print("=" * 60)
