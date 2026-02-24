# Automation Testing - Airbnb Search Workflow

A comprehensive Playwright-based automation testing framework for Airbnb property search workflows with Django integration, database result tracking, and admin dashboard.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Viewing Results](#viewing-results)
- [Architecture](#architecture)

---

## Overview

This project automates the complete Airbnb property search workflow, from landing page navigation through property detail extraction. Each test step is independently tracked with pass/fail status, screenshots, detailed comments, and page URLs—all stored in a Django database for easy access and analysis.

**Key Technologies:**
- **Playwright** - Browser automation
- **Django** - Web framework & database
- **Python 3.10+** - Language
- **SQLite/PostgreSQL** - Database

---

## Features

✅ Automated Test Steps**
- Location search with auto-suggestions
- Date picker interaction and validation
- Guest count selection
- Search results verification
- Property details extraction

✅ **Comprehensive Tracking**
- Full-page screenshots for each step
- Pass/Fail status with visual badges
- Step-by-step comments and data
- Current page URLs captured
- Timestamps for all operations

✅ **Django Admin Interface**
- View all test results in one dashboard
- Filter by status, date, or test name
- Search across test cases and comments
- Download and export results

✅ **Robust Error Handling**
- Detailed error messages and tracebacks
- Graceful popup dismissal
- Browser data clearing between tests
- Screenshot capture even on failure

---

## Project Structure

```
automation/
│
├── __init__.py
├── admin.py                    # Django admin configuration
├── models.py                   # Result model definition
├── apps.py                     # Django app settings
├── views.py                    # Django views
├── tests.py                    # Django unit tests
│
├── 📁 logging/
│   ├── __init__.py
│   └── logger.py               # Custom logger setup
│
├── 📁 management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── run_automation.py   # Django management command
│
├── 📁 playwright/
│   │
│   ├── 📁 core/
│   │   ├── base_workflow.py         # Base workflow class
│   │   ├── browser_manager.py       # Browser initialization
│   │   └── __pycache__/
│   │
│   ├── 📁 pages/
│   │   ├── landing_page.py          # Landing page interactions
│   │   ├── result_page.py           # Results page interactions
│   │   └── propertyDetails.py       # Property details page
│   │
│   ├── 📁 utils/
│   │   ├── helper.py                # Utility functions
│   │   └── screenshot_manager.py    # Screenshot handling
│   │
│   ├── 📁 workflow/
│   │   └── user_workflow.py         # Main workflow
│
├── 📁 service/
      └── workflow_runner.py       # Service layer

```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Django 4.2+
- pip (Python package manager)
- Git

### Step 1: Clone Repository and navigate

```bash
git clone https://github.com/Rai321han/automation_testing.git
cd automation_testing
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt** should contain:


### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 5: Setup Django Database

```bash
# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
# Follow prompts to enter username, email, password
```

## Running Tests

### Option 1: Django Management Command (Recommended)

```bash
python manage.py run_automation
```

## Viewing Results

### Start Django Development Server

```bash
python manage.py runserver
```

### Access Admin Dashboard

Open browser: **http://127.0.0.1:8000/admin/**

Login with your superuser credentials

Navigate to: **Automation > Results**

### Result Page Features

**Columns Displayed:**
- 🔵 **ID** - Result identifier
- 📝 **Test Case** - Step name
- ✅    **Status** - PASS or FAIL
- 🌐 **URL** - Current page (clickable link)
- 💬 **Comment** - Step details and extracted data
- 📅 **Created At** - Timestamp

**Filter Options:**
- By Status (Pass/Fail)
- By Date Range
- By Search Term

**Search:**
Type in any field to filter results

### Example Result Entry

| Field | Value |
|-------|-------|
| Test Case | `Type location 'Japan' in search field` |
| Status | ✓ PASS |
| Comment | `country typed successfully: Japan` |
| URL | `https://www.airbnb.com/` |
| Created At | `2026-02-24 06:58:20` |


## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────┐
│             Django Admin Dashboard                  │
│         (View & Manage Test Results)                │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│           Result Model (Database)                   │
│      (test_case, passed, comment, url, ...)        │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│        BaseWorkflow (run_step orchestration)        │
│    (Executes steps, captures screenshots, saves)    │
└────────────────┬────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
┌─────▼──┐ ┌────▼────┐ ┌──▼──────────┐
│ Page   │ │Screenshot│ │ Logger      │
│Objects │ │ Manager  │ │             │
└─────┬──┘ └────┬────┘ └──┬──────────┘
      │         │          │
      └─────────┼──────────┘
                │
         ┌──────▼──────┐
         │  Playwright │
         │   Browser   │
         └─────────────┘
```
