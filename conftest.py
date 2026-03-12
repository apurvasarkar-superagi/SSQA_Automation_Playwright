import pytest
import os
import shutil
import logging
import uuid
import threading
import random
import string
from pathlib import Path
from urllib.parse import urlparse
import requests

from datetime import datetime, timezone
from dotenv import load_dotenv
from sales.sync_api import sync_playwright, Page

step_log = logging.getLogger("bdd.steps")

load_dotenv()

# ── Dashboard API integration ─────────────────────────────────────────────────
# Set DASHBOARD_URL in .env to enable (e.g., http://localhost:8080)
# All hooks are no-ops when DASHBOARD_URL is not set.

_launch_id: str | None = None  # UUID for the current pytest session
_launch_start_ms: int = 0  # epoch ms when session started
_launch_tag_set = False  # whether we've updated tag from feature tags
_scenario_ids: dict[str, str] = {}  # nodeid → scenario UUID
_scenario_start: dict[str, float] = {}  # scenario UUID → start timestamp (epoch ms)
_api_lock = threading.Lock()


def _api(method: str, path: str, data: dict | None = None) -> None:
    """Fire-and-forget API call to the dashboard backend."""
    url = os.environ.get("DASHBOARD_URL", "").rstrip("/")
    if not url:
        return
    try:
        import requests as _req
        fn = getattr(_req, method.lower())
        fn(f"{url}{path}", json=data, timeout=3)
    except Exception:
        pass  # never block test execution


def _now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


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
    parser.addoption(
        "--remote-ws-url",
        action="store",
        default=os.environ.get("PLAYWRIGHT_REMOTE_URL"),
        help="WebSocket URL of remote Playwright browser server (e.g., wss://abc123.ngrok-free.app)"
    )
    parser.addoption(
        "--local",
        action="store_true",
        default=False,
        help="Force run tests on local browser, ignoring PLAYWRIGHT_REMOTE_URL"
    )


def pytest_sessionstart(session):
    """Create a launch entry on the dashboard at the start of a test session."""
    global _launch_id, _launch_start_ms
    # Only run on the main process (not xdist workers)
    if hasattr(session.config, "workerinput"):
        return
    _launch_id = str(uuid.uuid4())
    _launch_start_ms = _now_ms()
    keyword = getattr(session.config.option, "keyword", "") or ""
    # Use keyword as initial tag; will be refined to feature tag on first scenario
    tag = keyword.strip() or "all"
    env = os.environ.get("DVR_ENV", "prod")
    _api("POST", "/api/launches", {"id": _launch_id, "tag": tag, "env": env})


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

    if rep.when != "call":
        return

    sc_id = _scenario_ids.get(item.nodeid)
    screenshot_name = None

    # Take screenshot on failure
    if rep.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            if isinstance(page, Page):
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    test_name = item.name.replace(" ", "_")
                    screenshot_path = SCREENSHOTS_DIR / f"{test_name}_{timestamp}.png"
                    page.screenshot(path=str(screenshot_path))
                    screenshot_name = screenshot_path.name
                    print(f"\nScreenshot saved: {screenshot_path}")
                    if _launch_id:
                        _api("POST", f"/api/launches/{_launch_id}/logs", {
                            "type": "info",
                            "text": f"   Screenshot: {screenshot_name}",
                        })
                except Exception as e:
                    print(f"Failed to take screenshot: {e}")

    # Update scenario status on dashboard
    if _launch_id and sc_id:
        status = "passed" if rep.passed else "failed"
        start_ms = _scenario_start.get(sc_id)
        duration_ms = (_now_ms() - start_ms) if start_ms else None
        _api("PATCH", f"/api/launches/{_launch_id}/scenarios/{sc_id}", {
            "status": status,
            "duration_ms": duration_ms,
            "screenshot": screenshot_name,
        })
        _api("POST", f"/api/launches/{_launch_id}/logs", {
            "type": "pass" if rep.passed else "fail",
            "text": f"{'✓' if rep.passed else '✗'}  Scenario {status}",
        })


def pytest_sessionfinish(session, exitstatus):
    """
    Clean up __pycache__ directories after all tests complete.
    Only runs on the main process, not on xdist workers.
    """
    if hasattr(session.config, "workerinput"):
        return

    # Finalize launch on dashboard
    if _launch_id:
        status = "passed" if exitstatus == 0 else "failed"
        duration_ms = _now_ms() - _launch_start_ms if _launch_start_ms else None
        _api("PATCH", f"/api/launches/{_launch_id}", {
            "status": status,
            "end_time": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
        })
        _api("POST", f"/api/launches/{_launch_id}/logs", {
            "type": "info",
            "text": f"── SESSION FINISHED — {status.upper()} ──",
        })

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


def pytest_bdd_before_scenario(request, feature, scenario):
    global _launch_tag_set
    step_log.warning("\nScenario: %s", scenario.name)

    if not _launch_id:
        return

    # Refine launch tag once using the feature-level tag (e.g. @signIn)
    if not _launch_tag_set and feature.tags:
        with _api_lock:
            if not _launch_tag_set:
                _launch_tag_set = True
                _api("PATCH", f"/api/launches/{_launch_id}", {"tag": next(iter(feature.tags))})

    # Derive a short scenario name from its tags, or fall back to scenario name
    sc_name = next(iter(scenario.tags)) if scenario.tags else scenario.name[:40]
    sc_id = str(uuid.uuid4())
    _scenario_ids[request.node.nodeid] = sc_id
    _scenario_start[sc_id] = _now_ms()

    _api("POST", f"/api/launches/{_launch_id}/scenarios", {
        "id": sc_id,
        "name": sc_name,
        "description": scenario.name,
    })
    _api("POST", f"/api/launches/{_launch_id}/logs", {
        "type": "step",
        "text": f"SCENARIO: {sc_name} — {scenario.name}",
    })


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    step_log.warning("  PASSED  %s %s", step.keyword, step.name)
    if not _launch_id:
        return
    sc_id = _scenario_ids.get(request.node.nodeid)
    _api("POST", f"/api/launches/{_launch_id}/logs", {
        "type": "pass",
        "text": f"✓  {step.keyword} {step.name}",
    })
    if sc_id:
        _api("POST", f"/api/launches/{_launch_id}/steps", {
            "scenario_id": sc_id,
            "keyword": step.keyword,
            "text": step.name,
            "status": "passed",
        })


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    step_log.warning("  FAILED  %s %s", step.keyword, step.name)
    if not _launch_id:
        return
    sc_id = _scenario_ids.get(request.node.nodeid)
    error_text = str(exception)[:500]
    _api("POST", f"/api/launches/{_launch_id}/logs", {
        "type": "fail",
        "text": f"✗  {step.keyword} {step.name}",
    })
    _api("POST", f"/api/launches/{_launch_id}/logs", {
        "type": "fail",
        "text": f"   {error_text}",
    })
    if sc_id:
        _api("POST", f"/api/launches/{_launch_id}/steps", {
            "scenario_id": sc_id,
            "keyword": step.keyword,
            "text": step.name,
            "status": "failed",
            "error": error_text,
        })


@pytest.fixture(scope="function", autouse=True)
def scenario_id():
    """Unique 9-character alphanumeric identifier, regenerated for every scenario."""
    sid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    os.environ["SCENARIO_ID"] = sid
    yield sid
    os.environ.pop("SCENARIO_ID", None)


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
    remote_ws_url = request.config.getoption("--remote-ws-url")
    run_local = request.config.getoption("--local")

    with sync_playwright() as p:
        # Select browser based on option using dictionary mapping
        browser_map = {
            "firefox": p.firefox,
            "webkit": p.webkit,
        }
        browser_launcher = browser_map.get(browser_type, p.chromium)

        if remote_ws_url and not run_local:
            scenario_node = getattr(request.node, 'scenario', None)
            if scenario_node:
                scenario_name = scenario_node.name
            else:
                scenario_name = request.node.name.replace('test_', '', 1).replace('_', ' ').title()
            parsed = urlparse(remote_ws_url)
            scheme = "https" if parsed.scheme == "wss" else "http"
            base_url = f"{scheme}://{parsed.netloc}"
            resp = requests.post(f"{base_url}/api/acquire-worker", json={}, timeout=130)
            resp.raise_for_status()
            ws_url = base_url.replace("https://", "wss://") + resp.json()["wsUrl"]
            connect_headers = {"X-Scenario-Name": scenario_name}
            if headless:
                connect_headers["x-playwright-headless"] = "true"
            browser = browser_launcher.connect(
                ws_endpoint=ws_url,
                headers=connect_headers,
            )
        else:
            browser = browser_launcher.launch(headless=headless)

        context = browser.new_context(viewport={"width": 1920, "height": 900})
        page = context.new_page()
        page.set_default_timeout(30000)

        yield page

        # Cleanup — suppress TargetClosedError which occurs during
        # parallel xdist shutdown when targets are already closing
        try:
            context.close()
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass