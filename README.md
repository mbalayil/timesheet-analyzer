# 📊  Timesheet Analyzer

A powerful tool designed to help managers and team leads analyze timesheet data efficiently. This application provides comprehensive insights into team productivity and time allocation through an intuitive dashboard interface.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-web_interface-orange.svg)
![UV](https://img.shields.io/badge/uv-package_manager-green.svg)

## ✨ Features

- Import and analyze timesheet CSV files
- Generate detailed productivity reports
- Visualize time allocation across different projects
- Track individual and team performance metrics

## 🛠️ Project Setup

### Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mbalayil/timesheet-analyzer.git
cd timesheet-analyzer
```

2. Set up your Gemini API key:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

Make sure to replace `your_api_key_here` with your actual Gemini API key.

3. Use the Makefile to set up and run the project:
```bash
# Setup and run everything
make all

# Or run individual commands
make setup    # Create virtual environment and install uv
make install  # Install project dependencies
make run      # Run the application
```

## 📖 Usage

The application will open a web-based dashboard where you can:
1. Upload timesheet CSV files
2. View analysis results

To re-run the application after initial setup:
```bash
uv run streamlit run main.py
```

## Project Structure

```
timesheet-analyzer/
├── main.py             # Main application entry point
├── dashboard_helper.py # Dashboard functionality helper
├── samples/            # Sample timesheet data
├── .venv/              # Virtual environment
├── pyproject.toml      # Project configuration
└── README.md           # This file
```
