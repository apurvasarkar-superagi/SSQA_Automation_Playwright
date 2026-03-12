# SSQA Automation Playwright — Codebase Instructions

## Project Overview
BDD test automation framework using **pytest-bdd + Playwright + Page Object Model**.

---

## Directory Structure
```
SSQA_Automation_Playwright/
├── conftest.py                     # Fixtures, hooks, browser setup, dashboard integration
├── pytest.ini                      # Markers, logging config
├── config.yaml                     # Credentials & URLs for prod/staging/uat
├── .env                            # PLAYWRIGHT_REMOTE_URL, DASHBOARD_URL
└── sales/
    ├── scr/
    │   ├── test_scenarios.py       # Auto-discovers all .feature files (do not modify)
    │   └── [Module]/
    │       ├── feature/            # Gherkin .feature files
    │       ├── feature_code/       # Page Object classes
    │       └── step_def/           # @given/@when/@then step functions
    ├── utility/
    │   └── WebDriverHelper.py      # Playwright wrapper base class
    └── runners/
        ├── env_setup.py            # Thread-local state
        └── test_runner.py          # GLUE_MODULES list + pytest runner
```

---

## How to Treat Playwright Codegen Scripts

When a Playwright codegen script is provided, convert it into the BDD framework structure following these rules:

### Step 1 — Identify logical steps
Break the codegen script into logical user actions and group them into BDD steps:
- **Given** — preconditions (navigate to login page)
- **When** — user actions (sign in, navigate, click, fill forms)
- **Then** — assertions/verifications (expect visible, success messages)

### Step 2 — Reuse existing steps
Before creating new steps, check if a matching step already exists:
- `Given User navigates to the login page` → `LoginPage.navigate()` (login_step_def.py)
- `When User signs in with {cred_key} credentials` → `LoginPage.login()` (login_step_def.py)
- `When User navigates to Settings page` → `commonScript.goToSettings()` (login_step_def.py)

Do NOT duplicate existing step definitions.

### Step 3 — Create the module (if new area)
For each new functional area, create a folder under `sales/scr/[ModuleName]/` with:
```
[ModuleName]/
├── feature/
│   └── [module].feature        # Gherkin scenario
├── feature_code/
│   └── [module]page.py         # Page Object class
└── step_def/
    └── [module]_step_def.py    # Step definitions
```

### Step 4 — Write the feature file
```gherkin
@module_name
Feature: <description>

  @module_name_1
  Scenario: <scenario title>
    Given ...
    When ...
    Then ...
```
- Use `@module_name` on the Feature and `@module_name_1`, `@module_name_2` on each Scenario
- Inline data (e.g., names, emails) goes directly in the Gherkin step as quoted strings
- Credentials always use `cred_key` from config.yaml (e.g., `qaautomation_main_cred`), never hardcode email/password

### Step 5 — Write the Page Object
```python
class ModulePage:
    def __init__(self, page):
        self.page = page

    def navigateToX(self):
        # direct translation of navigation locators from codegen

    def verifyXVisible(self):
        # use .wait_for() instead of expect(...).to_be_visible()

    def fillXDetails(self, param1, param2):
        # use .fill() directly; no need for .click() before .fill() on textboxes

    def submitXForm(self):
        # button clicks to submit

    def verifySuccessMessage(self, message):
        self.page.get_by_text(message).wait_for()
```

**Rules for Page Objects:**
- Class name: `[Module]Page` (e.g., `ContactsPage`)
- File name: `[module]page.py` (lowercase, no underscore)
- Do NOT inherit from `WebDriverHelper` unless complex waits/assertions from that utility are needed
- Replace `expect(locator).to_be_visible()` → `locator.wait_for()`
- Replace `expect(locator).to_have_text(...)` → `locator.wait_for()` or `locator.inner_text()`
- Avoid hardcoded `sleep()` — use Playwright's built-in wait methods
- Do NOT hardcode test data that changes (e.g., table row content); use stable locators like buttons or headers

### Step 6 — Write the Step Definitions
```python
from pytest_bdd import when, then, parsers
from sales.scr.[Module].feature_code.[module]page import [Module]Page

@when("User navigates to X page")
def user_navigates_to_x(page):
    [Module]Page(page).navigateToX()

@when(parsers.parse('User fills details with name "{name}" and email "{email}"'))
def user_fills_details(page, name, email):
    [Module]Page(page).fillDetails(name, email)

@then(parsers.parse('User should see "{message}" message'))
def user_should_see_message(page, message):
    [Module]Page(page).verifySuccessMessage(message)
```

**Rules for Step Definitions:**
- Import only `when`/`then` if the module has no `given` steps (Given steps live in login_step_def.py)
- Use `parsers.parse(...)` for steps with inline string parameters (quoted values in Gherkin)
- One step function → one page object method call; no logic in step defs
- Step text must exactly match the Gherkin feature file

### Step 7 — Register the module
After creating the module, update these two files:

**`sales/runners/test_runner.py`** — add to `GLUE_MODULES`:
```python
GLUE_MODULES = [
    "Login",
    "Settings",
    "Common",
    "NewModule",   # ← add here
]
```

**`pytest.ini`** — add markers:
```ini
markers =
    newmodule: new module tests
    newmodule_1: new module test variant 1
```

---

## Locator Conversion Rules (Codegen → Page Object)

| Codegen Pattern | Page Object Equivalent |
|---|---|
| `page.get_by_role("textbox", name="X").click()` then `.fill(v)` | `page.get_by_role("textbox", name="X").fill(v)` — drop the `.click()` |
| `page.get_by_role("button", name="X").click()` | keep as-is |
| `page.get_by_role("img", name="X").click()` | keep as-is |
| `page.get_by_role("link", name="X").click()` | keep as-is |
| `expect(locator).to_be_visible()` | `locator.wait_for()` |
| `expect(locator).to_have_text("X")` | `page.get_by_text("X").wait_for()` |
| `page.locator(".css-class").first.click()` | keep as-is |
| `page.locator(".css-class").nth(n).click()` | keep as-is |

---

## Credential Handling
- Credentials are stored in `config.yaml` under each environment (`prod`, `staging`, `uat`)
- Format: `email___password___username___workspace_id___user_id`
- Always reference by key (e.g., `qaautomation_main_cred`) — never hardcode email/password in feature files or page objects
- To add a new credential: add it to all relevant environment sections in `config.yaml`

---

## Running Tests
```bash
# Run a specific scenario
pytest -m contacts_1 --local --headed

# Run all scenarios in a module
pytest -m contacts --local

# Run against staging
pytest -m contacts_1 --DVR_ENV=staging --local --headed
```
