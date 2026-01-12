import pytest
import sys
from pathlib import Path

def run_failed_tests(env="prod", headless=False, browser="chromium"):
    """
    Run only the tests that failed in the previous run.
    
    Args:
        env: Environment to use (prod or staging)
        headless: Run browser in headless mode
        browser: Browser to use (chromium, firefox, webkit)
    """
    # Check for failed scenarios file (similar to rerun/failed_scenarios.txt)
    failed_file = Path("sales/Reports/failed_scenarios.txt")
    
    if not failed_file.exists():
        print("No failed scenarios file found. Run tests first to generate it.")
        sys.exit(1)
    
    args = [
        str(failed_file),
        "-v",
        f"--DVR_ENV={env}",
        f"--browser={browser}",
    ]
    
    if headless:
        args.append("--headless")
    
    # Add reporting
    args.extend([
        "--html=sales/Reports/report_failed.html",
        "--self-contained-html",
        "--junitxml=sales/Reports/junit_failed.xml"
    ])
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    import os
    env = os.getenv("DVR_ENV", "prod")
    run_failed_tests(env=env)
