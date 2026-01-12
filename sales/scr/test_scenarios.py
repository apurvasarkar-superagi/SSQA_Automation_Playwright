"""
Centralized test file for auto-discovering and registering all feature files.
Similar to Java Cucumber's @CucumberOptions(features = { "src/main/java" })

This single file replaces the need for individual test files in each module.
All .feature files are automatically discovered and registered here.
"""
from pathlib import Path
from pytest_bdd import scenarios

# ============================================================================
# AUTO-DISCOVER FEATURE FILES - Similar to Java Cucumber's features parameter
# ============================================================================
# Automatically discover and register all .feature files recursively
# This mimics Java's: @CucumberOptions(features = { "src/main/java" })
# No need for individual test files in each module - all scenarios are registered here

# Get the directory containing this test file (sales/scr)
test_file_dir = Path(__file__).parent

# Find all feature files recursively and register them
for feature_file in test_file_dir.rglob("*.feature"):
    # Register each feature file
    # Path should be relative to the test file's directory (sales/scr)
    rel_path = feature_file.relative_to(test_file_dir)
    scenarios(str(rel_path))
