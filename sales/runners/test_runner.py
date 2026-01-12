"""
Test runner for executing all tests with specific configurations.
Similar to SCRunnerTest.java in the Java framework.
"""
import pytest
import sys
import os
from pathlib import Path
from typing import List
import importlib

GLUE_MODULES = [
    "Login",
    "Settings",
    "Common",
]

STEP_DEF_BASE_PATH = "sales.scr"

def load_glue_modules() -> List[str]:
    # Automatically discover and import step definitions from all glue modules.
    # Returns list of imported module paths.
    loaded_modules = []
    base_path = Path("sales/scr")
    
    for module_name in GLUE_MODULES:
        module_path = f"{STEP_DEF_BASE_PATH}.{module_name}"
        step_def_path = base_path / module_name / "step_def"
        
        if not step_def_path.exists():
            print(f"Warning: Step definitions path not found for module '{module_name}': {step_def_path}")
            continue
        
        # Find all Python files in step_def directory
        step_def_files = list(step_def_path.glob("*.py"))
        step_def_files = [f for f in step_def_files if not f.name.startswith("__")]
        
        if not step_def_files:
            print(f"Warning: No step definition files found in {step_def_path}")
            continue
        
        # Import each step definition file
        for step_def_file in step_def_files:
            module_file_name = step_def_file.stem  # filename without .py
            full_module_path = f"{module_path}.step_def.{module_file_name}"
            
            try:
                # Import the module to register step definitions with pytest-bdd
                importlib.import_module(full_module_path)
                loaded_modules.append(full_module_path)
                print(f"Loaded step definitions from: {full_module_path}")
            except ImportError as e:
                print(f"Warning: Could not import {full_module_path}: {e}")
            except Exception as e:
                print(f"Error loading {full_module_path}: {e}")
    
    return loaded_modules


def get_glue_modules_for_pytest_plugins() -> List[str]:
    """
    Get list of module paths formatted for pytest_plugins.
    This ensures step definitions are registered before tests run.
    """
    return load_glue_modules()

def run_all_tests(env="prod", tags=None, headless=False, browser="chromium", workers=None):
    """
    Run all tests with specified configuration.
    
    Args:
        env: Environment to use (prod or staging)
        tags: Optional tag expression to override default filtering
              If None, uses default exclusions similar to Java implementation
              Java: tags = "not @not_automated and not @Duplicate and not @obsolete and not @flaky and not @not_v3"
        headless: Run browser in headless mode
        browser: Browser to use (chromium, firefox, webkit)
        workers: Number of parallel workers (None = sequential, "auto" = auto-detect CPU count, or int)
    
    Note: Glue modules are already loaded via pytest_plugins in conftest.py,
    so we don't need to load them again here.
    """
    args = [
        "sales/scr",
        "-v",
        f"--DVR_ENV={env}",
        f"--browser={browser}",
    ]
    
    # Add parallel execution if workers specified
    if workers:
        if workers == "auto":
            args.append("-n=auto")  # Auto-detect CPU count
        else:
            try:
                num_workers = int(workers)
                if num_workers > 0:
                    args.append(f"-n={num_workers}")
                else:
                    print(f"Warning: Workers must be > 0, running sequentially")
            except (ValueError, TypeError):
                print(f"Warning: Invalid workers value '{workers}', running sequentially")
    
    if headless:
        args.append("--headless")
    
    # Add tag filtering (similar to Java's tag filtering)
    if tags:
        # Use custom tag expression if provided
        tag_expression = tags if isinstance(tags, str) else " and ".join(tags)
        args.extend(["-m", tag_expression])
    else:
        # Default tag filtering - exclude the same tags as Java implementation
        # Java: tags = "not @not_automated and not @Duplicate and not @obsolete and not @flaky and not @not_v3 and @apurva"
        exclude_tags = ["not_automated", "Duplicate", "obsolete", "flaky", "not_v3"]
        exclude_expression = " and ".join([f"not {tag}" for tag in exclude_tags])
        # Include @apurva tag (matching Java behavior)
        tag_expression = f"{exclude_expression} and apurva"
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
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all tests with tag filtering")
    parser.add_argument("--env", default=os.getenv("DVR_ENV", "prod"),
                       help="Environment to use (prod or staging)")
    parser.add_argument("--headless", action="store_true",
                       help="Run browser in headless mode")
    parser.add_argument("--browser", default="chromium",
                       choices=["chromium", "firefox", "webkit"],
                       help="Browser to use")
    parser.add_argument("--tags", type=str,
                       help="Tag expression (e.g., 'not not_automated and not Duplicate')")
    parser.add_argument("--workers", type=str, default=None,
                       help="Number of parallel workers (e.g., '4', 'auto', or omit for sequential)")
    
    args = parser.parse_args()
    
    run_all_tests(
        env=args.env,
        headless=args.headless,
        browser=args.browser,
        tags=args.tags,
        workers=args.workers
    )
