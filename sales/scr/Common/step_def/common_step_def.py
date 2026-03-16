from pytest_bdd import then, parsers
from sales.scr.Common.feature_code.common import commonScript


@then(parsers.parse('User should see "{message}" message'))
def user_should_see_message(page, message):
    page.get_by_text(message).wait_for()
