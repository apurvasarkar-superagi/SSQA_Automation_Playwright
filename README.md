# SSQA Automation Playwright

Playwright-based automation framework for SuperAGI Sales application testing.

## Installation Guide

Follow these steps to set up and run the project successfully:

### Prerequisites
- Python 3.14.0 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd SSQA_Automation_Playwright
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers
```bash
playwright install chromium
```

### Step 5: Configure Environment
- The `config.yaml` file contains environment configurations for `prod` and `staging`
- Credentials are stored in the config file in the format: `email___password___user_name___workspace_id___user_id`

### Step 6: Run Tests

#### Run all tests:
```bash
pytest
```

#### Run tests with specific tag:
```bash
pytest -m signIn
```

#### Run tests for specific environment:
```bash
pytest --DVR_ENV=staging
```

#### Run tests with custom domain:
```bash
pytest --DTEST_ENV_DOMAIN=".in.superagi.com"
```

#### Run tests in headless mode:
Modify `conftest.py` to set `headless=True` in browser launch options.

#### Run with HTML report:
```bash
pytest --html=sales/Reports/report.html --self-contained-html
```

#### Run tests in parallel:
```bash
# Using test_runner.py with 4 parallel workers
python sales/runners/test_runner.py --workers 4

# Using test_runner.py with auto-detected workers (based on CPU cores)
python sales/runners/test_runner.py --workers auto

# Using test_runner.py with 10 workers in headless mode
python sales/runners/test_runner.py --workers 10 --headless

# Or directly with pytest
pytest sales/scr -n 4
pytest sales/scr -n auto
```

**Note**: Parallel execution requires `pytest-xdist`. If not installed, run `pip install -r requirements.txt` to install all dependencies.

### Configuration

#### Environment Variables
- `DVR_ENV`: Environment to use (`prod` or `staging`, default: `prod`)
- `TEST_ENV_DOMAIN`: Override domain (e.g., `.in.superagi.com`)

#### Command Line Options
- `--DVR_ENV`: Set environment (prod/staging)
- `--DTEST_ENV_DOMAIN`: Override test domain
- `--workers`: Number of parallel workers for test_runner.py (e.g., `4`, `auto`, or omit for sequential)

### Debugging

#### Run with verbose output:
```bash
pytest -v -s
```

#### Run specific test:
```bash
pytest sales/test_signIn.py::test_signIn
```

#### Run with pdb debugger:
```bash
pytest --pdb
```

### Reports

Test reports are generated in `sales/Reports/`:
- HTML report: `report.html`
- JUnit XML: `junit.xml`

### Best Practices

1. **Page Object Model**: All page interactions should be in page object classes
2. **Step Definitions**: Map Gherkin steps to Python functions
3. **Fixtures**: Use pytest fixtures for setup/teardown
4. **Configuration**: Store credentials and URLs in `config.yaml`
5. **Tags**: Use tags to organize and filter tests

### Troubleshooting

#### Import Errors
- Ensure all `__init__.py` files are present
- Check that virtual environment is activated
- Verify Python path includes project root

#### Local Browser 
- Run `playwright install` to ensure browsers are installed
- Check browser launch options in `conftest.py`

#### Configuration Issues
- Verify `config.yaml` exists and has correct structure
- Check environment variable settings

### Contributing

When adding new tests:
1. Create feature file in appropriate `feature/` directory
2. Add step definitions in `step_def/` directory
3. Create page objects in `pageObject/` if needed
4. Follow existing naming conventions
