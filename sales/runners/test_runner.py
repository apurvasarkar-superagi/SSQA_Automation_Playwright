"""
Test runner for executing all tests with specific configurations.
Similar to SCRunnerTest.java in the Java framework.
"""
import pytest
import sys
import os

def run_all_tests(env="prod", tags=None, headless=False, browser="chromium"):
    """
    Run all tests with specified configuration.
    
    Args:
        env: Environment to use (prod or staging)
        tags: List of tags to filter tests (e.g., ["@signIn", "@smoke"])
        headless: Run browser in headless mode
        browser: Browser to use (chromium, firefox, webkit)
    """
    args = [
        "sales/scr",
        "-v",
        f"--DVR_ENV={env}",
        f"--browser={browser}",
    ]
    
    if headless:
        args.append("--headless")
    
    if tags:
        tag_expression = " and ".join(tags)
        args.extend(["-m", tag_expression])
    
    # Add reporting
    args.extend([
        "--html=sales/Reports/report.html",
        "--self-contained-html",
        "--junitxml=sales/Reports/junit.xml"
    ])
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    # Default: run all tests in prod environment
    env = os.getenv("DVR_ENV", "prod")
    run_all_tests(env=env)
