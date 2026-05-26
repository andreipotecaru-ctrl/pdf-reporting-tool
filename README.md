# Desktop Data Processing & PDF Reporting Tool

A lightweight, production-ready desktop application built with Python and a web-native frontend (Eel, HTML5, Tailwind CSS). The tool is engineered to ingest, parse, filter, and consolidate large operational audit data files (.csv, .xlsx, .xls) and compile them into securely encrypted, professionally formatted PDF reports.

## Core Features

* **Multi-Tab Dataset Processing:** Specialized data parsing pipelines for multiple structural log formats (Account Transactions, Financial Logs, Login Histories, Communications, Self-Exclusion Records, and Deposit Limit Logs).
* **Automated Data Consolidation:** Smart header alignment engine that automatically unifies multi-source data files (e.g., legacy vs. modern structures in Bonus History) into a single unified dataframe.
* **Time-Based Ledger Segmentation:** Capability to parse transactional timestamps on-the-fly and automatically split unified datasets into individual, standalone monthly PDF reports.
* **Enterprise-Grade PDF Generation:** Programmatic PDF assembly utilizing `ReportLab` with active page compression, dynamic scaling font arrays based on layout orientation (Landscape/Portrait), and professional grid layouts.
* **Automated Document Encryption:** Built-in `StandardEncryption` security layer allowing instant auto-locking of generated PDFs using conditional string slicing (e.g., locking via client identification tokens).

---

## Technical Architecture & Tech Stack

The application leverages an asynchronous decoupled architecture, isolating heavy data crunching from UI rendering threads via WebSocket RPC bridges.

* **Backend:** Python 3.x
* **Data Manipulation:** Pandas, OpenPyXL (Vectorized filtering and IO file parsing)
* **Reporting Engine:** ReportLab (Low-level PDF canvas programmatic layout generation)
* **GUI Bridge:** Eel (Python-to-JavaScript bidirectional RPC protocol)
* **Frontend UI:** HTML5, Modern JavaScript (ES6+), Tailwind CSS (Utility-first compilation)

### Repository File Structure

```text
├── web/
│   ├── index.html   # Main application dashboard layout (Tailwind CSS UI)
│   └── script.js    # Asynchronous RPC frontend triggers & UI state controllers
├── main.py          # Exposed backend Python services & vectorized data pipelines
├── .gitignore       # Production runtime exclusion mapping
└── README.md        # Technical documentation
```

---

## Installation & Setup

### Prerequisites
* Python 3.8 or higher installed on your local environment.
* Google Chrome or a Chromium-based web browser (highly recommended for optimal window rendering via Eel).

### 1. Clone the Repository
```bash
git clone [https://github.com/andreipotecaru-ctrl/pdf-reporting-tool.git](https://github.com/andreipotecaru-ctrl/pdf-reporting-tool.git)
cd pdf-reporting-tool
```

### 2. Install Required Dependencies
Initialize your environment and install the verified architectural packages using `pip`:
```bash
pip install eel pandas openpyxl reportlab
```

### 3. Run the Application
Execute the primary entry-point script to spin up the local service bridge and launch the native graphical interface window:
```bash
python main.py
```

---

## Production Security Notes

* **Zero Cloud Footprint:** All data ingestion, structural filtering, and PDF generation operations run 100% locally on the user's host machine. No external APIs are called, ensuring strict alignment with enterprise privacy and data retention compliance.
* **Clean History Lifecycle:** Git tracking files exclude tracking for internal local exports (`PDF_Reports_Export/`), temporary compilation folders (`__pycache__/`), and OS cache artifacts to enforce clean continuous delivery pipelines.
