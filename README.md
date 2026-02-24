# Automation Testing - Airbnb Search Workflow

A comprehensive Playwright-based automation testing framework for Airbnb property search workflows with Django integration, database result tracking, and admin dashboard.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Test Workflow](#test-workflow)
- [Viewing Results](#viewing-results)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project automates the complete Airbnb property search workflow, from landing page navigation through property detail extraction. Each test step is independently tracked with pass/fail status, screenshots, detailed comments, and page URLs—all stored in a Django database for easy access and analysis.

**Key Technologies:**
- **Playwright** - Browser automation
- **Django** - Web framework & database
- **Python 3.10+** - Language
- **SQLite/PostgreSQL** - Database

---

## ✨ Features

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

## 📁 Project Structure

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

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Django 4.2+
- pip (Python package manager)
- Git

### Step 1: Clone Repository

```bash
cd /home/w3e101/Desktop/W3_Internship/automation_testing
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
```
Django>=4.2
Playwright>=1.40
python-dateutil>=2.8
```

### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 5: Setup Django Database

```bash
cd automation_testing  # Django project folder

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
# Follow prompts to enter username, email, password
```

### Step 6: Create Media Directory

```bash
mkdir -p media/automation/screenshots
```

---

## ⚙️ Configuration

### Django Settings (`automation_testing/settings.py`)

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media files (screenshots)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'automation',  # Your app
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'automation.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

---

## ▶️ Running Tests

### Option 1: Django Management Command (Recommended)

```bash
python manage.py run_automation
```

This executes the complete `UserWorkflow` and stores all results in the database.

### Option 2: Using WorkflowRunner Service

```bash
python manage.py shell
```

Then in the shell:
```python
from automation.service.workflow_runner import WorkFlowRunner

runner = WorkFlowRunner()
result = runner.run_user_workflow()
print(f"Status: {result['status']}")
print(f"Error: {result['error']}")
```

### Option 3: Direct Script Execution

Create a script `run_test.py` in the project root:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automation_testing.settings')
django.setup()

from automation.service.workflow_runner import WorkFlowRunner

if __name__ == '__main__':
    runner = WorkFlowRunner()
    result = runner.run_user_workflow()
    
    if result['status'] == 'PASS':
        print("✓ All tests passed!")
    else:
        print(f"✗ Tests failed: {result['error']}")
```

Run it:
```bash
python run_test.py
```

### Browser Modes

**Headless Mode (Faster):**
```python
# Default - browser runs in background
with BrowserManager(headless=True) as page:
    workflow = UserWorkflow(page)
    result = workflow.run()
```

**Headed Mode (Debugging):**
```python
# Browser window visible - good for debugging
with BrowserManager(headless=False) as page:
    workflow = UserWorkflow(page)
    result = workflow.run()
```

---

## 🧪 Test Workflow

The automation executes 27+ test steps organized in 5 phases:

### Phase 1: Landing Page (Steps 1-8)
| Step | Action | Verification |
|------|--------|--------------|
| 1 | Open Airbnb.com | Page loads correctly |
| 2 | Clear cookies & storage | Browser data cleared |
| 3 | Handle popups | Popups dismissed |
| 4 | Click location input | Input field focused |
| 5 | Type location | Country entered |
| 6 | Check auto-suggestions | Suggestions list appears |
| 7 | Extract suggestions | All items captured |
| 8 | Select random location | Location selected |

### Phase 2: Date Selection (Steps 9-13)
| Step | Action | Verification |
|------|--------|--------------|
| 9 | Verify date picker opens | Calendar visible |
| 10 | Navigate months | Month advanced |
| 11 | Select dates | Check-in & check-out picked |
| 12 | Verify date display | Dates shown in UI |
| 13 | Validate date logic | Valid date range |

### Phase 3: Guest Selection (Steps 14-17)
| Step | Action | Verification |
|------|--------|--------------|
| 14 | Verify guest field clickable | Field interactive |
| 15 | Open guest popup | Selection menu appears |
| 16 | Set guest counts | Adults, children, infants, pets set |
| 17 | Verify guest display | Count shown correctly |

### Phase 4: Search & Results (Steps 18-24)
| Step | Action | Verification |
|------|--------|--------------|
| 18 | Submit search | Search button clicked |
| 19 | Handle popups | Results page popups dismissed |
| 20 | Verify page loads | Results page rendered |
| 21 | Verify search criteria UI | Location, dates, guests displayed |
| 22 | Verify URL parameters | Search params in URL |
| 23 | Extract properties | Listings extracted & saved |
| 24 | Click random property | Detail page navigated to |

### Phase 5: Property Details (Steps 25-27)
| Step | Action | Verification |
|------|--------|--------------|
| 25 | Verify page loads | Property page rendered |
| 26 | Handle popups | Detail page popups dismissed |
| 27 | Extract property data | Title, subtitle, images captured |

---

## 📊 Viewing Results

### Start Django Development Server

```bash
python manage.py runserver
```

### Access Admin Dashboard

Open browser: **http://localhost:8000/admin/**

Login with your superuser credentials

Navigate to: **Automation > Results**

### Result Page Features

**Columns Displayed:**
- 🔵 **ID** - Result identifier
- 📝 **Test Case** - Step name
- ✅/❌ **Status** - PASS (green ✓) or FAIL (red ✗)
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
| Screenshot | `automation/screenshots/Type_location_Japan.png` |
| Created At | `2026-02-24 06:58:20` |

### Programmatic Access

```python
from automation.models import Result

# Get all results
all_results = Result.objects.all()

# Get only passed tests
passed = Result.objects.filter(passed=True)

# Get only failed tests
failed = Result.objects.filter(passed=False)

# Get latest 10 results
latest = Result.objects.all()[:10]

# Filter by test name
location_tests = Result.objects.filter(test_case__icontains="location")

# Count by status
pass_count = Result.objects.filter(passed=True).count()
fail_count = Result.objects.filter(passed=False).count()
```

---

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

### Key Classes

**BaseWorkflow**
```python
class BaseWorkflow:
    def run_step(name, fn, *args, comment_fn=None, locator=None):
        # Execute function
        # Capture screenshot
        # Save result to DB
        # Return value for next step
```

**BrowserManager**
```python
class BrowserManager:
    def __enter__():
        # Launch browser
        # Create context
        # Return page
    
    def __exit__():
        # Close browser
        # Cleanup
```

**UserWorkflow**
```python
class UserWorkflow(BaseWorkflow):
    def run():
        # Execute 27+ steps
        # Track each step
        # Return final status
```

---

## 🔍 Understanding the Code

### Running a Single Step

```python
self.run_step(
    test_case_name="Type location 'Japan' in search field",
    fn=landing.type_location,
    text="Japan",
    delay=200,
    locator=landing.locationInput,
    comment_fn=lambda _: f"country typed successfully: Japan"
)
```

**What happens:**
1. ▶️ Logs step start
2. 🎬 Executes `landing.type_location("Japan", delay=200)`
3. 📸 Takes full-page screenshot
4. 💬 Generates comment: `"country typed successfully: Japan"`
5. 💾 Saves to database with PASS status
6. ✔️ Logs step completion

### Screenshot Capture

Automatic for every step:
- **Pass**: `Type_location_Japan_in_search_field.png`
- **Fail**: Same file + error in comment

Location: `media/automation/screenshots/`

### Database Result Entry

```python
Result(
    test_case="Type location 'Japan' in search field",
    passed=True,
    comment="country typed successfully: Japan",
    url="https://www.airbnb.com/",
    screenshot="automation/screenshots/Type_location_Japan_in_search_field.png",
    created_at="2026-02-24 06:58:20"
)
```

---

## 🐛 Troubleshooting

### Issue: "No such file or directory: media/automation/screenshots"

**Solution:**
```bash
mkdir -p media/automation/screenshots
```

### Issue: "Migrations not applied"

**Solution:**
```bash
python manage.py makemigrations automation
python manage.py migrate
```

### Issue: "Database is locked"

**Solution:**
```bash
# Remove and recreate database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Issue: "Playwright browser timeout"

**Solution:** Increase timeout in `landing_page.py`:
```python
self.page.wait_for_selector(selector, timeout=15000)  # 15 seconds
```

### Issue: "Screenshot not saving - Unsupported mime type"

**Solution:** Ensure filename has `.png` extension in `screenshot_manager.py`

### Issue: "Element not found"

**Solution:** 
1. Check selectors are correct
2. Add wait before interaction: `locator.wait_for(state="visible")`
3. Increase timeout if page loads slowly

### Issue: "Test hangs on popup"

**Solution:** Ensure `handle_popups()` runs with `reraise=False`:
```python
self.run_step("Handle popups", landing.handle_popups, reraise=False)
```

---

## 📈 Example Output

```
2026-02-24 06:58:20,100 | INFO | UserWorkflow | ▶ Step: Open Airbnb landing page
2026-02-24 06:58:25,200 | INFO | UserWorkflow | Screenshot saved: automation/screenshots/Open_Airbnb_landing_page.png
2026-02-24 06:58:25,300 | INFO | UserWorkflow | Created DB result → [PASS] Open Airbnb landing page
2026-02-24 06:58:25,400 | INFO | UserWorkflow | ✔ Open Airbnb landing page
2026-02-24 06:58:25,500 | INFO | UserWorkflow | ▶ Step: Handle landing page popups
2026-02-24 06:58:26,100 | WARNING | UserWorkflow | Failed to handle popup (expected for some runs)
2026-02-24 06:58:26,200 | INFO | UserWorkflow | ✔ Handle landing page popups
2026-02-24 06:58:26,300 | INFO | UserWorkflow | ▶ Step: Type location 'Japan' in search field
2026-02-24 06:58:28,100 | INFO | UserWorkflow | Screenshot saved: automation/screenshots/Type_location_Japan_in_search_field.png
2026-02-24 06:58:28,200 | INFO | UserWorkflow | Created DB result → [PASS] Type location 'Japan' in search field
2026-02-24 06:58:28,300 | INFO | UserWorkflow | ✔ Type location 'Japan' in search field
...
✓ Workflow completed successfully!
```

---

## 📚 Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Airbnb Website](https://www.airbnb.com/)

---

## 🤝 Contributing

1. Create a new branch for features
2. Write tests for new functionality
3. Update this README if changes affect usage
4. Submit pull request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 💬 Support

For issues, questions, or suggestions:
- Create an issue in the repository
- Check existing documentation
- Review test logs for error details

---

**Happy Testing! 🚀**