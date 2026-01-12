# sales/scr/Login/test_signin_scenarios.py
# IMPORTANT: Import step definitions BEFORE importing scenarios
# This ensures step definitions are registered before scenarios are parsed
import sales.scr.Login.step_def.login_step_def

from pytest_bdd import scenarios

# Register scenarios from the feature file
# Path is relative to bdd_features_base_dir (sales/scr) from pytest.ini
scenarios("Login/features/signIn_signUp.feature")
