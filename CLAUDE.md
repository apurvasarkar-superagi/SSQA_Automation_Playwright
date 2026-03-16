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

---

## Manual Scenario Verification via Browser

### Trigger
When the user says **"manually validate @tag1, @tag2, ..."** (e.g., `manually validate @leads_1, @contacts_2`), execute the full verification process below for each listed scenario tag. The browser must already be open or navigable via MCP Playwright.

When verifying a scenario, do NOT just walk through the Gherkin steps literally. You must **read and understand the full code chain** before executing in the browser.

### Verification Process

#### Phase 1 — Code Analysis (before touching the browser)
1. **Read the feature file** — understand the scenario, its tags, and all parameters (Scenario Outline examples, inline data, etc.)
2. **Read the step definitions** — understand the actual Python code that runs for each step, including:
   - Data transformations (e.g., splitting `___`-delimited strings)
   - Dynamic modifications (e.g., appending `SCENARIO_ID` to emails)
   - Environment variable usage (e.g., `os.environ.get("SCENARIO_ID")`)
3. **Read the page objects** — understand what locators and actions are used
4. **Read conftest.py fixtures** — understand what fixtures are auto-injected:
   - `scenario_id` fixture generates a random 9-char alphanumeric ID per test and sets `os.environ["SCENARIO_ID"]`
   - `page` fixture provides the Playwright page instance
   - `env` fixture provides the environment (prod/staging/uat)
5. **Read config.yaml** — resolve credential keys to actual values (email, password, etc.)

#### Phase 2 — Simulate Runtime Behavior
When executing in the browser, replicate what the **code actually does at runtime**, not just the Gherkin text:
- If the step def appends a `SCENARIO_ID` to an email, generate a random identifier and use it (e.g., `apurvasarkar+abc123def@gmail.com`)
- If the step def splits a `___`-delimited string, use the split values correctly
- If a fixture transforms data, apply that transformation
- If there is an `if` statement or conditional logic, evaluate it as the code would

#### Phase 3 — Browser Execution & Validation
Execute each step in the browser and verify:
1. **Navigation** — correct pages load, expected elements appear
2. **Actions** — forms fill correctly, buttons are clickable and enabled
3. **Assertions** — success messages appear, data is visible where expected
4. **Locators** — every locator in the page object actually finds an element on the page

#### Phase 4 — Report Results
Provide a step-by-step table with PASS/FAIL for each Gherkin step, and note any issues found.

### Locator Verification in Browser Snapshots

The Playwright MCP browser snapshot shows an **accessibility tree**, not the raw DOM. This means:
- **HTML `id` attributes are NOT shown** in snapshots — elements like `id="profile_details_section"` will appear as `generic [ref=eXXX]` without the id
- **CSS class names are NOT shown** — `.card_container` won't appear by name
- **`data-*` attributes are NOT shown**

When verifying locators that use CSS selectors or DOM ids, you **cannot rely on the snapshot alone**. These locators are valid even if not visible in the snapshot:

| Locator Type | Example | Visible in Snapshot? |
|---|---|---|
| `page.locator("#some_id")` | `page.locator("#profile_details_section")` | No — id attributes hidden |
| `page.locator("[id='some_id']")` | `page.locator("[id='profile_details_section']")` | No — same as above |
| `page.locator(".css-class")` | `page.locator(".card_container")` | No — classes hidden |
| `page.locator("[data-attr='value']")` | `page.locator("[data-testid='lead-email']")` | No — data attrs hidden |
| `page.get_by_role(...)` | `page.get_by_role("button", name="Add Lead")` | Yes — roles shown |
| `page.get_by_text(...)` | `page.get_by_text("Lead added successfully")` | Yes — text shown |
| `page.get_by_role("textbox", name="X")` | `page.get_by_role("textbox", name="Email")` | Yes — roles shown |
| `page.get_by_role("img", name="X")` | `page.get_by_role("img", name="crm_icon")` | Yes — roles shown |

**Rule**: Do NOT flag CSS/id-based locators as broken just because they don't appear in the accessibility snapshot. Only flag a locator as potentially broken if you have concrete evidence (e.g., a JavaScript evaluation confirms the element doesn't exist, or the action using it visibly fails).
