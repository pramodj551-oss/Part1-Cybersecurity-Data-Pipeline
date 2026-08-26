# 🛡️ AI-Powered Cybersecurity Incident Analytics Pipeline

**Part 1 — End-to-End Applied AI & ML Data Product Capstone**

A production-style Python ETL pipeline that transforms raw cybersecurity incident data into a clean, validated, feature-engineered and query-ready dataset for analytics and future ML/AI applications.

## Quick Start

### 1. Clone
```bash
git clone https://github.com/pramodj551-oss/Part1-Cybersecurity-Data-Pipeline.git
cd Part1-Cybersecurity-Data-Pipeline
```

### 2. Create environment
```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

### 3. Install dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Add the raw dataset
Place the dataset at exactly:
```text
data/raw/cybersecurity_incident_reports.csv
```

The pipeline validates the required schema before processing.

### 5. Run
```bash
python run_pipeline.py
```

## Pipeline

```text
Raw CSV
  ↓
DataLoader + Schema Validation
  ↓
Data Cleaning + Quality Validation
  ↓
Feature Engineering
  ↓
Processed CSV
  ↓
SQLite Database
  ↓
SQL Analytics / EDA
```

## Repository Structure

```text
Part1-Cybersecurity-Data-Pipeline/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run_pipeline.py
├── queries.sql
├── EDA.ipynb
├── data/
│   ├── raw/
│   │   └── cybersecurity_incident_reports.csv
│   └── processed/
│       └── .gitkeep
├── outputs/
│   └── .gitkeep
├── logs/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── utils.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── database.py
│   └── pipeline.py
├── tests/
└── .github/
    └── workflows/
        └── python.yml
```

## Outputs

The paths are controlled centrally by `src/config.py`:

```text
data/processed/clean_incidents_reports.csv
data/processed/engineered_incidents.csv
outputs/incidents.db
outputs/summary_report.csv
outputs/cleaning_report.json
logs/pipeline.log
```

These are runtime-generated artifacts. They are intentionally excluded from Git tracking; CI verifies their creation during the end-to-end run.

## Main Features

- CSV loading and schema validation
- Missing-value handling
- Duplicate detection/removal
- Data type conversion
- Date normalization
- Categorical normalization
- Range validation
- Feature engineering
- Risk and incident-complexity features
- SQLite storage
- SQL analytical queries
- Data-quality reporting
- Structured logging
- Automated CI with GitHub Actions

## Validation

The pipeline validates file existence, required columns, empty datasets, duplicate incident IDs, data types and key data-quality rules before the data is used downstream.

## Analytics

`queries.sql` contains analytical queries for incident volume, sectors, regions, attack types, threat actors, severity, downtime, financial impact, risk and other descriptive metrics. The automated integration suite validates all 29 configured SQL queries against the generated dataset/database during CI.

`EDA.ipynb` provides exploratory analysis of the cleaned data, including data-quality summaries, numeric/categorical distributions, incident trends, severity, financial indicators, boolean security indicators and correlations. CI validates the notebook JSON, executes it with a bounded timeout, validates the executed notebook and verifies the generated runtime artifacts.

## Testing

Run the regression and integration suite with:

```bash
python -m pytest -q
```

The suite covers data loading, cleaning, feature engineering, schema behavior and important edge cases. SQL integration is executed after the end-to-end pipeline has generated the required runtime dataset in CI.

## CI

GitHub Actions runs on pushes and pull requests targeting `main`.

The current CI workflow executes these gates in order:

1. Checks out the repository using `actions/checkout@v5`.
2. Sets up Python 3.11 using `actions/setup-python@v6` with pip caching.
3. Installs dependencies from `requirements.txt`.
4. Compiles Python sources.
5. Runs the pytest regression/unit suite.
6. Executes the complete end-to-end pipeline.
7. Executes and validates all 29 SQL integration queries against the generated data.
8. Validates `EDA.ipynb` as a Jupyter notebook.
9. Executes the EDA notebook with a bounded timeout.
10. Validates the executed notebook has no execution errors.
11. Verifies all expected generated artifacts are non-empty.
12. Uploads the EDA and pipeline artifacts for CI inspection.

A CI run must complete successfully before the corresponding change is considered runtime-verified.

## API Status

This Part 1 repository is currently a batch ETL/data-pipeline application and does **not** include a REST API. A FastAPI service can be added in a future enhancement without changing the core ETL modules.

## Security

Do not commit secrets or local databases. `.env`, database files, logs and generated outputs are excluded through `.gitignore` where appropriate.

## Reproducibility

Use Python 3.11 and install dependencies from `requirements.txt`. Project paths and validation constants are centralized in `src/config.py`; a central random seed is defined there for deterministic operations.

## Technology

Python • Pandas • NumPy • SQLAlchemy • SQLite • Jupyter • Pytest • GitHub Actions

## License

MIT License — see `LICENSE`.

## Author

**Pramod Prakash Jadhav**
