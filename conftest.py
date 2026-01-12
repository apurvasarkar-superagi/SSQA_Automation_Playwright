import pytest
import os
from pathlib import Path
from datetime import datetime
from sales.sync_api import sync_playwright, Page

# Import step definitions so they're registered with pytest-bdd
# Using pytest_plugins ensures the module is loaded as a plugin
pytest_plugins = ['sales.scr.Login.step_def.login_step_def']

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
    env_value = config.getoption("--DVR_ENV")
    os.environ["DVR_ENV"] = env_value
    
    # Set TEST_ENV_DOMAIN if provided
    domain_value = config.getoption("--DTEST_ENV_DOMAIN")
    if domain_value:
        os.environ["TEST_ENV_DOMAIN"] = domain_value
    
    # Create Reports directory if it doesn't exist
    reports_dir = Path("sales/Reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Create screenshots directory
    screenshots_dir = reports_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

def pytest_runtest_setup(item):
    """Setup before each test"""
    pass

def pytest_runtest_teardown(item):
    """Teardown after each test"""
    pass

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
                    screenshot_dir = Path("sales/Reports/screenshots")
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    test_name = item.name.replace(" ", "_")
                    screenshot_path = screenshot_dir / f"{test_name}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    print(f"\nScreenshot saved: {screenshot_path}")
                except Exception as e:
                    print(f"Failed to take screenshot: {e}")

@pytest.fixture(scope="session")
def env(request):
    """Fixture to get the DVR_ENV from command line"""
    return request.config.getoption("--DVR_ENV")

@pytest.fixture(scope="session")
def browser_type(request):
    """Fixture to get browser type from command line"""
    return request.config.getoption("--browser")

@pytest.fixture(scope="function")
def page(request, browser_type):
    """Fixture to provide a Playwright page instance"""
    headless = request.config.getoption("--headless")
    
    with sync_playwright() as p:
        # Select browser based on option
        if browser_type == "firefox":
            browser = p.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser = p.webkit.launch(headless=headless)
        else:
            browser = p.chromium.launch(headless=headless)
        
        # Create context with viewport
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        # Set default timeout
        page.set_default_timeout(30000)
        
        yield page
        
        # Cleanup
        try:
            context.close()
            browser.close()
        except Exception as e:
            print(f"Error during browser cleanup: {e}")