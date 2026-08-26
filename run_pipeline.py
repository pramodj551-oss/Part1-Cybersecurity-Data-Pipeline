"""Project entry point for Cybersecurity Incident Analytics Pipeline."""

from __future__ import annotations

import logging
import sys
import time

from src.config import LOG_FILE
from src.pipeline import AnalyticsPipeline

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main() -> int:
    """Run the complete analytics pipeline and return an OS exit code."""
    start_time = time.perf_counter()
    logger.info("CYBERSECURITY INCIDENT ANALYTICS APPLICATION STARTED")

    try:
        pipeline = AnalyticsPipeline()
        dataframe = pipeline.run()
        runtime = time.perf_counter() - start_time

        print("\n" + "=" * 70)
        print("PIPELINE EXECUTED SUCCESSFULLY")
        print("=" * 70)
        print(f"Total Records  : {len(dataframe)}")
        print(f"Total Features : {len(dataframe.columns)}")
        print(f"Execution Time : {runtime:.2f} seconds")
        print("Database Status: Updated")
        print("Output Status  : Generated")
        print("=" * 70)

        logger.info("Pipeline completed successfully in %.2f seconds.", runtime)
        return 0

    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        print("\nExecution cancelled.")
        return 130

    except Exception as error:
        logger.exception("Pipeline execution failed.")
        print("\nPipeline Failed")
        print(error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
