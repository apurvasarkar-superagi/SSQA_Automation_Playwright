import pytest
import os
import shutil
from pathlib import Path
from datetime import datetime
from sales.sync_api import sync_playwright, Page

# Automatically load step definitions from glue modules
from sales.runners.test_runner import get_glue_modules_for_pytest_plugins

# Dynamically register all step definitions from glue modules
pytest_plugins = get_glue_modules_for_pytest_plugins()

# Constants for directory paths
REPORTS_DIR = Path("sales/Reports")
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

def pytest_addoption(parser):
    """Add custom command line options for pytest"""
    parser.addoption(
        "--DVR_ENV",
        action="store",
        default="prod",
        help="Environment to use: prod or staging (default: prod)"
    )
    parser.addoption(
        "--DTEST_ENV_DOMAIN",
        action="store",
        default=None,
        help="Override test_env_main_url_sub_str domain (e.g., '.in.superagi.com')"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--test-browser",
        action="store",
        default="chromium",
        choices=["chromium", "firefox", "webkit"],
        help="Browser to use for tests (default: chromium)"
    )

def pytest_configure(config):
    """Set environment variable from pytest option"""
    os.environ["DVR_ENV"] = config.getoption("--DVR_ENV")
    
    domain_value = config.getoption("--DTEST_ENV_DOMAIN")
    if domain_value:
        os.environ["TEST_ENV_DOMAIN"] = domain_value
    
    # Create Reports and screenshots directories
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(exist_ok=True)


def pytest_collection_modifyitems(config, items):
    """
    Automatically exclude tests tagged with @not_automated by default.
    This ensures that when you run 'pytest -m apurva', scenarios with
    @not_automated are automatically excluded, matching Java Cucumber behavior.
    
    This hook runs after test collection and before test execution, allowing
    us to filter out tests that should not run by default.
    """
    remaining = []
    deselected = []
    
    for item in items:
        # Check if item has not_automated marker
        # pytest-bdd converts @not_automated tag to pytest.mark.not_automated
        markers = [marker.name for marker in item.iter_markers()]
        if "not_automated" in markers:
            deselected.append(item)
        else:
            remaining.append(item)
    
    # Update items list to exclude @not_automated tests
    items[:] = remaining
    if deselected:
        config.hook.pytest_deselected(items=deselected)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results and take screenshots on failure"""
    outcome = yield
    rep = outcome.get_result()
    
    # Take screenshot on failure
    if rep.when == "call" and rep.failed:
        # Get the page fixture if available
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            if isinstance(page, Page):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    test_name = item.name.replace(" ", "_")
                    screenshot_path = SCREENSHOTS_DIR / f"{test_name}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"\nScreenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"Failed to take screenshot: {e}")


def pytest_sessionfinish(session, exitstatus):
    """
    Clean up __pycache__ directories after all tests complete.
    This hook runs at the end of the test session.
    """
    base_path = Path("sales")
    
    # Find and remove all __pycache__ directories
    for pycache_dir in base_path.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
        except Exception:
            pass

    for pyc_file in base_path.rglob("*.pyc"):
        try:
            pyc_file.unlink()
        except Exception:
            pass


@pytest.fixture(scope="session")
def env(request):
    """Fixture to get the DVR_ENV from command line"""
    return request.config.getoption("--DVR_ENV")

@pytest.fixture(scope="session")
def browser_type(request):
    """Fixture to get browser type from command line"""
    return request.config.getoption("--test-browser", default="chromium")

@pytest.fixture(scope="function")
def page(request, browser_type):
    """Fixture to provide a Playwright page instance"""
    headless = request.config.getoption("--headless")
    
    with sync_playwright() as p:
        # Select browser based on option using dictionary mapping
        browser_map = {
            "firefox": p.firefox,
            "webkit": p.webkit,
        }
        browser_launcher = browser_map.get(browser_type, p.chromium)
        browser = browser_launcher.launch(headless=headless)
        
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.set_default_timeout(30000)
        
        yield page
        
        # Cleanup
        try:
            context.close()
            browser.close()
        except Exception as e:
            print(f"Error during browser cleanup: {e}")