# 🛡️ AI-Powered Cybersecurity Incident Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Google Colab](https://img.shields.io/badge/Google-Colab-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Project Overview

This repository contains **Part 1** of the End-to-End Applied AI & ML Data Product Capstone Project.

The project demonstrates a production-style **Extract, Transform, Load (ETL) pipeline** for cybersecurity incident data. The pipeline transforms raw incident records into a clean, validated, feature-engineered, and query-ready dataset that can be used for business analytics, machine learning models, dashboards, and AI-powered applications.

The implementation follows software engineering best practices, including modular Python architecture, centralized configuration, structured logging, data validation, automated feature engineering, SQLite database integration, SQL-based analysis, and exploratory data analysis (EDA).

This repository answers the first analytics question:

> **"Descriptive Analytics – What happened in the cybersecurity environment?"**

The processed dataset produced by this pipeline serves as the foundation for the remaining Capstone parts involving predictive analytics, interactive dashboards, and Large Language Model (LLM) applications.

---

## Business Problem

Modern organizations generate thousands of cybersecurity events every day from firewalls, endpoint protection systems, intrusion detection systems, authentication logs, and security monitoring tools.

Raw cybersecurity datasets often contain:

- Missing values
- Duplicate records
- Invalid timestamps
- Inconsistent attack categories
- Incorrect severity labels
- Mixed data types
- Poorly formatted text fields

Such datasets are unreliable for business intelligence, reporting, machine learning, or security investigations.

The objective of this project is to build a robust and reusable ETL pipeline that automatically validates, cleans, standardizes, enriches, and stores cybersecurity incident data in a structured format suitable for analytics.

---

## Analytics Objective

This repository focuses on **Descriptive Analytics** by answering the following business questions:

- What cybersecurity incidents have occurred?
- Which attack types are most common?
- Which sectors experience the highest number of incidents?
- Which regions are most frequently targeted?
- Which incidents have the highest severity?
- How clean and reliable is the collected cybersecurity data?

The cleaned dataset produced in this project becomes the input for predictive analytics and AI-based solutions developed in later stages of the Capstone Project.

---

## Dataset Information

**Dataset Name**
Cybersecurity Incidents Dataset

**Source**
Kaggle

**Dataset Category**
Cybersecurity / Incident Analytics

**Purpose**
The dataset contains cybersecurity incident records describing attack characteristics, severity, affected sectors, geographical regions, financial impact, and operational response information.

Typical attributes include:

- Incident ID
- Incident Date
- Attack Type
- Severity Score
- Industry Sector
- Region
- Threat Actor
- Records Affected
- Downtime Duration
- Financial Impact
- Regulatory Fine
- Response Team Size

The dataset is placed inside the repository at:

```
data/raw/cybersecurity_incidents_reports.csv
```

The pipeline automatically loads this dataset, validates its schema, performs cleaning and feature engineering, and stores the processed output for further analysis.

---

## Project Architecture

The project follows a modular ETL (Extract, Transform, Load) architecture designed using production-style software engineering principles.

```
                    Kaggle Dataset
                          │
                          ▼
                 Data Loading Module
                          │
                          ▼
                Data Validation Module
                          │
                          ▼
                 Data Cleaning Module
                          │
                          ▼
            Feature Engineering Module
                          │
                          ▼
              SQLite Database Storage
                          │
                          ▼
                 SQL Analytical Queries
                          │
                          ▼
             Exploratory Data Analysis
                          │
                          ▼
               Clean Analytics Dataset
```

Each module has a single responsibility, making the pipeline reusable, maintainable, and easy to extend.

---

## Repository Structure

```
AI-Powered-Cybersecurity-Incident-Analytics/
│
├── README.md
├── requirements.txt
├── .gitignore
├── LICENSE
├── CHANGELOG.md
├── .env.example
├── run_pipeline.py
├── queries.sql
├── EDA.ipynb
│
├── data/
│   ├── raw/
│   │   └── cybersecurity_incidents_reports.csv
│   │
│   └── processed/
│       ├── clean_incidents.csv
│       └── engineered_incidents.csv
│
├── outputs/
│   ├── cybersecurity.db
│   ├── summary_report.json
│   ├── quality_report.json
│   └── pipeline.log
│
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
│
├── tests/
│   ├── test_loader.py
│   ├── test_cleaning.py
│   ├── test_feature_engineering.py
│   ├── test_database.py
│   └── test_pipeline.py
│
└── .github/
    └── workflows/
        └── python.yml
```

---

## Project Features

The repository includes the following production-ready features:

- Automated CSV dataset loading
- Dataset schema validation
- Missing value handling
- Duplicate record detection and removal
- Datatype validation and conversion
- Timestamp standardization
- Attack type normalization
- Severity score validation
- Country and region standardization
- Feature engineering for analytics
- SQLite database integration
- SQL-based reporting
- Automated quality report generation
- Structured logging
- Modular ETL pipeline
- Exploratory Data Analysis (EDA)
- Google Colab compatibility
- GitHub-ready repository structure

---

## Data Validation Rules

Before processing the dataset, the pipeline performs multiple validation checks.

**File Validation**

- Dataset file existence
- CSV readability
- Empty dataset detection

**Schema Validation**

- Required column verification
- Optional column handling
- Unknown column detection

**Data Validation**

- Missing value identification
- Duplicate record detection
- Datatype validation
- Date format validation
- Severity score validation
- Invalid categorical value detection

**Data Quality Report**

After validation, the pipeline generates a structured quality report containing:

- Total records
- Total columns
- Missing values
- Duplicate records
- Invalid dates
- Invalid categories
- Overall data quality score

---

## Feature Engineering

The cleaned dataset is enriched using engineered features that improve analytical capabilities.

Examples include:

- Incident Year
- Incident Month
- Incident Quarter
- Incident Weekday
- High Severity Flag
- Financial Impact
- Total Incident Cost
- Downtime Category
- Response Efficiency
- Risk Score
- Attack Frequency
- Sector Risk Category

These engineered features improve downstream reporting and provide meaningful business insights for future machine learning models.

---

## Pipeline Workflow

The execution flow of the project is illustrated below.

```
Raw Cybersecurity Dataset
          │
          ▼
    Load Dataset
          │
          ▼
   Validate Dataset
          │
          ▼
     Clean Data
          │
          ▼
  Engineer Features
          │
          ▼
  Store into SQLite
          │
          ▼
 Execute SQL Queries
          │
          ▼
  Generate Reports
          │
          ▼
    Perform EDA
          │
          ▼
Final Analytics Dataset
```

The entire workflow can be executed using a single command:

```bash
python run_pipeline.py
```

All intermediate steps are automatically orchestrated by the pipeline module.

---

## Installation

### Prerequisites

Before running the project, ensure the following software is available:

- Python 3.11 or later
- Git
- SQLite (optional, for database inspection)
- Jupyter Notebook or Google Colab

### Clone the Repository

```bash
git clone https://github.com/pramodj551-oss/AI-Powered-Cybersecurity-Incident-Analytics.git
cd AI-Powered-Cybersecurity-Incident-Analytics
```

### Create a Virtual Environment (Optional)

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Required Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running on Google Colab

This repository is fully compatible with Google Colab.

**Step 1 – Clone Repository**

```bash
!git clone https://github.com/pramodj551-oss/AI-Powered-Cybersecurity-Incident-Analytics.git
%cd AI-Powered-Cybersecurity-Incident-Analytics
```

**Step 2 – Install Dependencies**

```bash
!pip install -r requirements.txt
```

**Step 3 – Upload Dataset**

Upload the Kaggle dataset file:

```
cybersecurity_incidents.csv
```

Move the file into:

```
data/raw/
```

**Step 4 – Run the Pipeline**

```bash
!python run_pipeline.py
```

**Step 5 – Execute the Notebook**

Open:

```
EDA.ipynb
```

Then select:

```
Runtime → Run all
```

The notebook will generate all visualizations and business insights automatically.

---

## Running the Pipeline Locally

After installing all dependencies, execute:

```bash
python run_pipeline.py
```

The pipeline automatically performs the following steps:

1. Load the dataset
2. Validate the dataset
3. Clean missing and invalid values
4. Remove duplicate records
5. Engineer analytical features
6. Store processed data in SQLite
7. Generate quality reports
8. Save processed CSV files

---

## Expected Outputs

After successful execution, the following files are generated.

**Processed Dataset**

```
data/processed/
├── clean_incidents.csv
└── engineered_incidents.csv
```

**Database**

```
outputs/
└── cybersecurity.db
```

**Reports**

```
outputs/
├── summary_report.json
├── quality_report.json
└── pipeline.log
```

---

## SQL Queries

The repository contains a dedicated SQL file for exploratory analysis.

```
queries.sql
```

Example analyses include:

- Total incidents
- Attack type distribution
- Sector-wise incidents
- Region-wise incidents
- Average severity score
- High-risk incidents
- Financial impact analysis
- Monthly incident trends

---

## Exploratory Data Analysis (EDA)

The notebook `EDA.ipynb` provides a comprehensive exploratory analysis of the processed dataset.

It includes:

- Dataset overview
- Missing value analysis
- Duplicate analysis
- Statistical summary
- Attack type distribution
- Sector analysis
- Regional analysis
- Severity distribution
- Correlation analysis
- Outlier detection
- Financial impact analysis
- Business insights
- Recommendations

All visualizations are generated directly from Python code using Pandas and Matplotlib.

---

## Technologies Used

**Programming Languages**

- Python 3.11

**Libraries**

- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- SQLAlchemy
- SQLite3
- Logging
- Pathlib

**Development Tools**

- Google Colab
- Git
- GitHub
- Jupyter Notebook

---

## Business Insights

The processed cybersecurity dataset enables organizations to answer important operational and business questions such as:

- Which attack types occur most frequently?
- Which industries experience the highest number of incidents?
- Which geographical regions are most affected?
- How are incidents distributed over time?
- What percentage of incidents are classified as high severity?
- Which incidents result in the highest financial impact?
- How complete and reliable is the collected cybersecurity data?

These insights help security teams prioritize investigations, improve reporting, and support data-driven decision-making.

---

## Project Outputs

After successful execution, the repository produces the following deliverables:

**Processed Data**

- Clean cybersecurity dataset
- Feature-engineered dataset

**Database**

- SQLite database containing processed incident records

**Reports**

- Data quality report
- Pipeline execution log
- Summary report

**Analytics**

- SQL queries for business analysis
- Exploratory Data Analysis notebook

---

## Future Roadmap

This repository represents **Part 1** of the Capstone Project.

The following enhancements are planned in subsequent repositories:

**Part 2 — Predictive Analytics**

- Machine Learning model development
- Model evaluation
- Feature importance analysis
- Prediction pipeline

**Part 3 — Interactive Dashboard**

- Streamlit dashboard
- Interactive charts
- Business KPI monitoring
- Search and filtering

**Part 4 — AI-Powered Document Intelligence**

- Large Language Model (LLM) integration
- Retrieval-Augmented Generation (RAG)
- Natural language question answering
- Document-based knowledge retrieval

---

## Repository Highlights

This project demonstrates:

- Modular Python architecture
- Production-style ETL pipeline
- Automated data validation
- Robust data cleaning
- Feature engineering
- SQLite database integration
- SQL analytics
- Structured logging
- Google Colab compatibility
- Reproducible project structure
- GitHub-ready documentation

---

## Reproducibility

To reproduce the project from a clean environment:

1. Clone the repository.
2. Install all dependencies listed in `requirements.txt`.
3. Place the dataset inside `data/raw/`.
4. Run:

```bash
python run_pipeline.py
```

5. Open `EDA.ipynb` and execute all cells.

The project should generate the processed datasets, SQLite database, reports, and notebook outputs without requiring any manual code modifications.

---

## Contributing

Contributions are welcome.

If you would like to improve the project:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

Please ensure that new code follows the existing project structure and coding standards.

---

## License

This project is distributed under the MIT License.

See the `LICENSE` file for complete license information.

---

## Acknowledgements

This project was developed as part of the End-to-End Applied AI & ML Data Product Capstone Project.

The implementation makes use of open-source Python libraries including:

- Pandas
- NumPy
- SQLite
- SQLAlchemy
- Matplotlib
- Jupyter Notebook

The cybersecurity dataset used in this repository was obtained from Kaggle for educational and analytical purposes.

---

## Author

**Pramod Prakash Jadhav**
AI/ML Developer | Cybersecurity Enthusiast

**Connect**

- GitHub: [https://github.com/pramodj551-oss](https://github.com/pramodj551-oss)
- LinkedIn: [https://www.linkedin.com/in/pramod-prakash-jadhav-42ba228](https://www.linkedin.com/in/pramod-prakash-jadhav-42ba2281)

---

## Repository Status

- **Project Status:** Completed (Part 1)
- **Version:** 2.1
- **Repository Type:** Production-Ready Academic Capstone Project
- **Primary Analytics Type:** Descriptive Analytics
- **Last Updated:** July 2026
