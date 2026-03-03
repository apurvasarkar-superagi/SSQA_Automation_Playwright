# SSQA Automation Playwright

Playwright-based automation framework for SuperAGI Sales application testing.

---

## Prerequisites

- Python 3.14.0 or higher
- pip (Python package manager)
- Docker (only required for remote execution)

---

## Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd SSQA_Automation_Playwright
```

### Step 2: Create Virtual Environment
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
```bash
cp .env.example .env
```
Edit `.env` and fill in the required values:
- `PLAYWRIGHT_REMOTE_URL` — WebSocket URL of the remote browser server (see [Remote Execution](#remote-execution))

> **Not using a remote machine?** Skip the `.env` setup and add `--local` to all your pytest commands to run the browser locally instead.

The `config.yaml` file contains environment configurations for `prod` and `staging`.

---

## Running Tests

### Basic usage
```bash
# Run by tag (marker)
pytest -m signIn
pytest -m signIn_1
pytest -m settings

# Run for a specific environment
pytest -m signIn --DVR_ENV=staging

# Run with custom domain
pytest -m signIn --DTEST_ENV_DOMAIN=".in.superagi.com"
```

### Local vs Remote execution

| Flag | Description |
|---|---|
| *(no flag)* | Runs on remote browser server defined in `.env` |
| `--local` | Forces local browser, ignores `.env` remote URL |
| `--headless` | Runs browser in headless mode (local only) |

```bash
# Run on remote machine (uses PLAYWRIGHT_REMOTE_URL from .env)
pytest -m signIn

# Run on local machine with visible browser
pytest -m signIn --local

# Run on local machine in headless mode
pytest -m signIn --local --headless
```

### Browser selection
```bash
pytest -m signIn --local --test-browser firefox
pytest -m signIn --local --test-browser webkit
pytest -m signIn --local --test-browser chromium   # default
```

### Parallel execution
```bash
pytest -m signIn -n 2
pytest -m signIn -n 4
pytest -m signIn -n auto
```

### With HTML report
```bash
pytest -m signIn --html=sales/Reports/report.html --self-contained-html
```

---

## Remote Execution

Tests can run against a browser on a remote machine using Docker + ngrok. The remote machine hosts the browser; your local machine runs the test logic.

### Setup

**1. Set up the remote machine** — see [playwright-remote-server](../playwright-remote-server/README.md)

**2. Get the connection URL from the remote machine:**
```bash
./get-url.sh
```
Output:
```
Connection URL:  wss://abc123.ngrok-free.app

Run on your LOCAL machine:
pytest -m signIn --remote-ws-url wss://abc123.ngrok-free.app
```

**3. Save the URL in `.env` on your local machine:**
```
PLAYWRIGHT_REMOTE_URL=wss://abc123.ngrok-free.app
```

**4. Run tests — no flags needed:**
```bash
pytest -m signIn
```

> The ngrok URL changes each time the remote server restarts. Update the one line in `.env` when it does.

### Override URL at runtime
```bash
pytest -m signIn --remote-ws-url wss://different-url.ngrok-free.app
```

---

## Step Logging

Tests print each BDD step and its result in real time:

```
Scenario: Verify user can sign in and access settings
  PASSED  Given User navigates to the login page
  PASSED  When User signs in with qaautomation_main_cred credentials
  PASSED  And User navigates to Settings page
  PASSED  Then User should verify all settings options are present
  PASSED  And User should verify Profile option is available in settings sidebar
```

Failed steps show as `FAILED` and stop the scenario there.

---

## Command Line Options

| Option | Default | Description |
|---|---|---|
| `-m <marker>` | — | Run tests by tag (e.g. `-m signIn`) |
| `--DVR_ENV` | `prod` | Environment: `prod` or `staging` |
| `--DTEST_ENV_DOMAIN` | — | Override domain (e.g. `.in.superagi.com`) |
| `--test-browser` | `chromium` | Browser: `chromium`, `firefox`, `webkit` |
| `--headless` | `False` | Run browser headless (local only) |
| `--local` | `False` | Force local browser, ignore remote URL |
| `--remote-ws-url` | from `.env` | Remote browser server WebSocket URL |

---

## Reports

Reports are saved to `sales/Reports/`:
- Screenshots on failure: `sales/Reports/screenshots/`
- HTML report: `sales/Reports/report.html`

---

## Project Structure

```
SSQA_Automation_Playwright/
├── conftest.py              # Fixtures, hooks, CLI options
├── pytest.ini               # Pytest configuration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── config.yaml              # Test environment config (credentials, URLs)
└── sales/
    ├── scr/
    │   ├── Login/           # Login feature tests
    │   ├── Settings/        # Settings feature tests
    │   └── Common/          # Shared steps
    ├── utility/
    │   └── WebDriverHelper.py
    ├── Reports/             # Test output
    └── runners/
        └── test_runner.py
```

---

## Troubleshooting

**Import errors**
- Ensure virtual environment is activated
- Check that `__init__.py` files are present

**Browser not found**
- Run `playwright install chromium`

**Remote connection timeout**
- Verify the remote server is running: check `docker compose ps` on the remote machine
- Get a fresh URL: run `./get-url.sh` on the remote machine and update `.env`

**Config issues**
- Verify `config.yaml` exists with correct structure
- Check `.env` has the correct values
