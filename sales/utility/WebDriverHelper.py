import os
import re
import time
import platform
import logging
import urllib.request
from typing import Optional, List, Union

from playwright.sync_api import Page, Locator, FrameLocator, TimeoutError as PlaywrightTimeoutError

from sales.runners.env_setup import EnvSetup


class WebDriverHelper:
    """
    Playwright-based WebDriver helper providing utility methods for browser automation.
    Python equivalent of the Java WebDriverHelper Selenium class.
    """

    DEFAULT_WAIT_TIME: int = int(os.getenv("DEFAULT_WAIT_TIME", "30"))
    SCREENSHOT_DIR: str = "sales/Reports/screenshots"
    LOG_DIRECTORY: str = "logs/"

    def __init__(self, page: Optional[Page] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.page: Page = page or EnvSetup.get_page()
        self.default_wait_time: int = self.DEFAULT_WAIT_TIME

    # ── Navigation ─────────────────────────────────────────────────────────────

    def get_url(self, url: str) -> None:
        self.logger.info("Open URL: ['%s']", url)
        try:
            self.page.goto(url)
            self.wait_for_time(2)
        except Exception as e:
            self.logger.info("URL %s not loaded in given time: %s", url, e)

    def get_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    def hard_refresh(self) -> None:
        self.page.evaluate("location.reload(true)")

    def page_refresh(self) -> None:
        self.page.reload()

    def go_to_previous_page(self) -> None:
        self.page.go_back()

    def hit_browser_back_button(self) -> None:
        self.page.go_back()

    def open_url_and_wait_for_element(
        self,
        url: str,
        locator: str,
        ele_visibility: bool,
        retry_count: int = 3,
        wait_time: int = 10,
    ) -> None:
        for _ in range(retry_count):
            self.get_url(url)
            self.logger.info(
                "Element visibility should be '%s', element displayed is '%s'",
                ele_visibility,
                self.is_displayed(locator),
            )
            ele_visible = self.is_displayed(locator, wait_time)
            if (ele_visibility and ele_visible) or (not ele_visibility and not ele_visible):
                break
        actually_visible = self.is_displayed(locator)
        assert (ele_visibility and actually_visible) or (
            not ele_visibility and not actually_visible
        ), f"Element visibility is not equal to '{ele_visibility}'."

    # ── Element Finding ────────────────────────────────────────────────────────

    def get_element(self, locator: str, wait_time: Optional[int] = None) -> Locator:
        """Returns a Playwright Locator after waiting for it to be present in the DOM."""
        timeout_ms = (wait_time if wait_time is not None else self.default_wait_time) * 1000
        self.logger.info("Find element via %s", locator)
        ele = self.page.locator(locator).first
        if timeout_ms > 0:
            ele.wait_for(timeout=timeout_ms)
        self.logger.info("Element %s found", locator)
        return ele

    def get_elements(self, locator: str, wait_time: Optional[int] = None) -> List[Locator]:
        """Returns all Playwright Locators matching the selector."""
        timeout_ms = (wait_time if wait_time is not None else self.default_wait_time) * 1000
        self.page.wait_for_selector(locator, timeout=timeout_ms)
        return self.page.locator(locator).all()

    def get_nested_element(self, parent: Locator, locator: str) -> Locator:
        ele = parent.locator(locator).first
        self.logger.info("Child element found: %s", locator)
        return ele

    def get_element_within_element(self, parent: Locator, child_locator: str) -> Locator:
        return parent.locator(child_locator).first

    def get_nested_element_if_present(
        self, parent: Locator, locator: str
    ) -> Optional[Locator]:
        try:
            child = parent.locator(locator).first
            if child.count() > 0:
                self.logger.info("Nested element found: %s", locator)
                return child
            self.logger.info("Nested element not found: %s", locator)
            return None
        except Exception as e:
            self.logger.error("Error finding nested element %s: %s", locator, e)
            return None

    def is_element_found(self, locator: str, wait: int = 0) -> bool:
        try:
            self.get_element(locator, wait)
            return True
        except Exception as e:
            self.logger.error("Element %s not found: %s", locator, e)
            return False

    def get_element_via_inner_text(
        self, locator: str, inner_text: str
    ) -> Optional[Locator]:
        elements = self.get_elements(locator)
        self.logger.info("Element list: %s", elements)
        for ele in elements:
            ele_text = ele.inner_text()
            self.logger.info("List element text: %s", ele_text)
            if ele_text.lower() == inner_text.lower():
                return ele
        self.logger.error("Element not found with inner text: %s", inner_text)
        return None

    def get_element_via_inner_text_contains(
        self, locator: str, inner_text: str
    ) -> Optional[Locator]:
        elements = self.get_elements(locator)
        self.logger.info("Element list: %s", elements)
        for ele in elements:
            ele_text = ele.inner_text()
            self.logger.info("List element text: %s", ele_text)
            if inner_text.lower() in ele_text.lower():
                return ele
        self.logger.error("Element not found with inner text containing: %s", inner_text)
        return None

    def get_last_element(self, locator: str) -> Locator:
        try:
            return self.page.locator(locator).last
        except Exception:
            self.wait_for_time(3)
            return self.page.locator(locator).last

    def get_nth_element(self, locator: str, nth: int) -> Locator:
        return self.page.locator(locator).nth(nth)

    def get_elements_count(self, locator: str) -> int:
        try:
            return self.page.locator(locator).count()
        except Exception:
            self.logger.info("Zero elements found with locator %s", locator)
            return 0

    # ── Interactions ───────────────────────────────────────────────────────────

    def send_keys(self, locator_or_ele: Union[str, Locator], text: str) -> None:
        if isinstance(locator_or_ele, str):
            self.get_element(locator_or_ele).fill(text)
        else:
            locator_or_ele.fill(text)

    def click_and_type_text(self, locator: str, text: str) -> None:
        ele = self.get_element(locator)
        ele.click()
        ele.fill(text)

    def click_on_element(self, locator_or_ele: Union[str, Locator]) -> None:
        if isinstance(locator_or_ele, str):
            try:
                self.wait_for_element_till_clickable(locator_or_ele, self.default_wait_time)
                self.page.locator(locator_or_ele).first.click()
                self.logger.info("Click on element '%s' successful", locator_or_ele)
            except PlaywrightTimeoutError:
                self.wait_for_time(5)
                self.page.locator(locator_or_ele).first.click()
                self.logger.info("Click on element '%s' successful on retry", locator_or_ele)
        else:
            locator_or_ele.click()
            self.logger.info("Click on locator element successful")

    def click_on_element_without_retry(self, locator: str) -> None:
        self.wait_for_element_till_clickable(locator, self.default_wait_time)
        self.page.locator(locator).first.click()
        self.logger.info("Click on element '%s' successful", locator)

    def click_element_using_java_script(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele)
        else:
            ele = locator_or_ele
        ele.evaluate("el => el.click()")
        self.logger.info("Click on element successful using JavaScript executor")

    def click_on_element_if_present(self, locator: str) -> None:
        try:
            ele = self.get_element(locator)
            self.wait_for_element_till_clickable(locator, self.default_wait_time)
            ele.click()
            self.logger.info("Click on element '%s' successful as element is present", locator)
        except Exception:
            self.logger.info("Element not clicked as it is not present")

    def click_on_element_via_inner_text_contains(
        self, locator: str, inner_text: str
    ) -> str:
        self.wait_for_time(5)
        ele = self.get_element_via_inner_text_contains(locator, inner_text)
        value = self.get_text(ele)
        ele.click()
        return value

    def double_click_on_element(self, locator: str) -> None:
        self.get_element(locator).dbl_click()

    def click_on_last_element(self, locator: str) -> None:
        try:
            self.page.locator(locator).last.click()
        except Exception:
            self.wait_for_time(3)
            self.page.locator(locator).last.click()

    def click_on_nth_element(self, locator: str, nth: int) -> None:
        try:
            self.page.locator(locator).nth(nth).click()
        except Exception:
            self.wait_for_time(3)
            self.page.locator(locator).nth(nth).click()

    def click_by_absolute_coordinates(self, x: int, y: int) -> None:
        try:
            self.page.mouse.click(x, y)
            self.logger.info("Clicked at absolute coordinates (%d, %d)", x, y)
        except Exception as e:
            self.logger.error("Failed to click at coordinates (%d, %d): %s", x, y, e)

    def click_empty_space(self) -> None:
        self.click_by_absolute_coordinates(565, 165)

    def click_inside_canvas(self, locator: str, x: int, y: int) -> None:
        self.get_element(locator).click(position={"x": x, "y": y})

    def mouse_down_on_element(self, locator: str) -> None:
        self.get_element(locator).evaluate(
            "el => el.dispatchEvent(new MouseEvent('mousedown', "
            "{bubbles: true, cancelable: true, view: window}))"
        )

    def drag_and_drop_element(
        self, from_element: Locator, to_element: Locator
    ) -> None:
        from_element.drag_to(to_element)

    def slide_bar(self, locator: str, x_offset: int, y_offset: int) -> None:
        slider = self.get_element(locator)
        box = slider.bounding_box()
        if box:
            start_x = box["x"] + box["width"] / 2
            start_y = box["y"] + box["height"] / 2
            self.page.mouse.move(start_x, start_y)
            self.page.mouse.down()
            self.page.mouse.move(start_x + x_offset, start_y + y_offset)
            self.page.mouse.up()

    def send_keys_inside_canvas(self, locator: str, text: str) -> None:
        self.get_element(locator).click()
        self.page.keyboard.type(text)

    def clear_text(self, locator_or_ele: Union[str, Locator]) -> None:
        if isinstance(locator_or_ele, str):
            self.logger.info("Clear text '%s' successful", locator_or_ele)
            self.get_element(locator_or_ele).clear()
        else:
            locator_or_ele.clear()

    def clear_text_using_key_strokes(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele)
        else:
            ele = locator_or_ele
        ele.click()
        self.page.keyboard.press("Control+a")
        self.page.keyboard.press("Backspace")

    def clear_and_send_keys(self, locator: str, text: str) -> None:
        self.logger.info("Type '%s' for locator '%s' after clearing", text, locator)
        try:
            ele = self.get_element(locator)
            ele.clear()
            self.wait_for_time(1)
            ele.fill(text)
        except Exception:
            ele = self.get_element(locator)
            ele.clear()
            self.wait_for_time(1)
            ele.fill(text)

    def clear_with_keys_and_send_keys(self, locator: str, text: str) -> None:
        self.logger.info(
            "Type '%s' for locator '%s' after clearing with keys", text, locator
        )
        try:
            ele = self.get_element(locator)
            self.clear_text_using_key_strokes(ele)
            self.wait_for_time(1)
            ele.fill(text)
        except Exception:
            ele = self.get_element(locator)
            self.clear_text_using_key_strokes(ele)
            self.wait_for_time(1)
            ele.fill(text)

    def clear_text_with_command(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele)
        else:
            ele = locator_or_ele
        try:
            ele.click()
            self.wait_for_time(1)
            if "windows" in self.get_current_os().lower():
                self.page.keyboard.press("Control+a")
                self.page.keyboard.press("Backspace")
            else:
                self.page.keyboard.press("Meta+a")
                self.page.keyboard.press("Delete")
        except Exception as e:
            self.logger.error(e)

    # ── Keyboard ───────────────────────────────────────────────────────────────

    def press_key(self, key: str, locator: Optional[str] = None) -> None:
        if locator:
            self.get_element(locator).press(key)
            self.logger.info(
                "pressKey with locator %s and key %s is successful", locator, key
            )
        else:
            self.page.keyboard.press(key)

    def send_key_via_action(self, chars: str) -> None:
        self.page.keyboard.type(chars)

    def type_using_keyboard(self, locator: str, key: str) -> None:
        try:
            ele = self.get_element(locator)
            ele.click()
            self.page.keyboard.type(key)
        except Exception as e:
            self.logger.error(e)

    def send_key_with_custom_time(self, char_list: str, wait_time_ms: int) -> None:
        for char in char_list:
            self.page.keyboard.type(char)
            self.wait_for_time_in_ms(wait_time_ms)

    def send_key_with_default_time(self, char_list: str) -> None:
        self.send_key_with_custom_time(char_list, 1000)

    def paste_text(self, ele: Locator) -> None:
        try:
            ele.click()
            self.wait_for_time(1)
            local_browser = os.getenv("LOCAL_BROWSER", "false").lower()
            if local_browser == "false":
                self.page.keyboard.press("Control+v")
            elif "windows" in self.get_current_os().lower():
                self.page.keyboard.press("Control+v")
            else:
                self.page.keyboard.press("Meta+v")
            self.wait_for_time(1)
        except Exception as e:
            self.logger.error("Error pasting text: %s", e)

    # ── Text & Attributes ──────────────────────────────────────────────────────

    def get_text(
        self, locator_or_ele: Union[str, Locator], wait_time: Optional[int] = None
    ) -> str:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele, wait_time)
        else:
            ele = locator_or_ele
        return (ele.text_content() or "").strip()

    def get_text_from_input_tag(self, locator: str) -> str:
        return self.get_element(locator).input_value()

    def get_attribute_value(
        self, locator_or_ele: Union[str, Locator], attribute_name: str
    ) -> Optional[str]:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele)
        else:
            ele = locator_or_ele
        self.logger.info(
            "Get attribute '%s' for element '%s'", attribute_name, locator_or_ele
        )
        return ele.get_attribute(attribute_name)

    def get_elements_text(self, locator: str) -> List[str]:
        self.wait_for_element(locator)
        return [ele.text_content() or "" for ele in self.get_elements(locator)]

    def get_elements_text_lower_case(self, locator: str) -> List[str]:
        return [t.lower() for t in self.get_elements_text(locator)]

    def get_elements_text_upper_case(self, locator: str) -> List[str]:
        return [t.upper() for t in self.get_elements_text(locator)]

    def get_elements_value(self, locator: str) -> List[str]:
        try:
            return [self.get_text(ele) for ele in self.get_elements(locator)]
        except Exception as e:
            self.logger.error("Locator %s not available: %s", locator, e)
            return []

    def get_nth_element_text(self, locator: str, nth: int) -> str:
        try:
            return self.page.locator(locator).nth(nth).text_content() or ""
        except Exception:
            self.wait_for_time(3)
            return self.page.locator(locator).nth(nth).text_content() or ""

    def get_element_tag_name(self, element: Locator) -> str:
        try:
            return element.evaluate("el => el.tagName.toLowerCase()")
        except Exception:
            self.logger.error("Unable to retrieve tag name for element")
            return ""

    @staticmethod
    def get_element_attribute(element: Locator, attribute_name: str) -> str:
        return (element.get_attribute(attribute_name) or "").strip()

    def get_computed_background_color(self, element: Locator) -> str:
        rgb_color = element.evaluate(
            "el => window.getComputedStyle(el).backgroundColor"
        )
        match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", rgb_color)
        if match:
            r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
            return f"#{r:02x}{g:02x}{b:02x}"
        return rgb_color

    def verify_ele_attribute_value(
        self, locator: str, attribute_name: str, attribute_value: str
    ) -> bool:
        try:
            curr = (self.get_attribute_value(locator, attribute_name) or "").strip()
            return curr.lower() == attribute_value.lower()
        except Exception:
            return False

    def set_attribute_value(
        self, locator: str, attribute_name: str, attribute_value: str
    ) -> None:
        self.logger.info(
            "Set attribute '%s' for locator '%s'", attribute_name, locator
        )
        ele = self.get_element(locator)
        ele.evaluate(f"el => {{ el['{attribute_name}'] = '{attribute_value}'; }}")
        ele.evaluate("el => el.dispatchEvent(new Event('input'))")
        ele.evaluate("el => el.dispatchEvent(new Event('change'))")

    # ── Visibility & State ─────────────────────────────────────────────────────

    def is_displayed(
        self, locator_or_ele: Union[str, Locator], wait_time: int = 0
    ) -> bool:
        try:
            if isinstance(locator_or_ele, str):
                if wait_time > 0:
                    self.page.wait_for_selector(
                        locator_or_ele,
                        timeout=wait_time * 1000,
                        state="visible",
                    )
                return self.page.locator(locator_or_ele).first.is_visible()
            else:
                return locator_or_ele.is_visible()
        except Exception:
            return False

    def is_displayed_with_retry_element_found(
        self, locator: str, wait_time: int
    ) -> bool:
        if self.is_displayed(locator, wait_time):
            return True
        return self.is_displayed(locator, wait_time)

    def is_selected(self, locator: str, wait_time: int = 0) -> bool:
        try:
            return self.get_element(locator, wait_time).is_checked()
        except Exception:
            return False

    def is_element_clickable(
        self, locator_or_ele: Union[str, Locator]
    ) -> bool:
        try:
            if isinstance(locator_or_ele, str):
                ele = self.get_element(locator_or_ele, 0)
            else:
                ele = locator_or_ele
            return ele.is_visible() and ele.is_enabled()
        except Exception as e:
            self.logger.error("Element not visible or clickable: %s", e)
            return False

    def is_attribute_present(self, locator: str, attribute: str) -> bool:
        try:
            return self.get_attribute_value(locator, attribute) is not None
        except Exception as e:
            self.logger.error(e)
            return False

    def is_attribute_present_as_expected(
        self, locator: str, attribute: str, seconds: int, expected: bool
    ) -> bool:
        max_time = time.time() + seconds
        while time.time() < max_time:
            try:
                value = self.get_attribute_value(locator, attribute)
                if value is not None and expected:
                    return True
                if value is None and not expected:
                    return True
                self.wait_for_time(5)
            except Exception as e:
                self.logger.error(e)
        return False

    def is_element_present(self, locator: str) -> bool:
        return self.page.locator(locator).count() > 0

    def is_image_broken(self, element: Locator) -> bool:
        return element.evaluate("el => el.naturalWidth") == 0

    # ── Waits ──────────────────────────────────────────────────────────────────

    def wait_for_time(self, seconds: int) -> None:
        self.page.wait_for_timeout(seconds * 1000)

    def wait_for_time_in_ms(self, timeout_ms: int) -> None:
        self.page.wait_for_timeout(timeout_ms)

    def wait_for_element(
        self, locator: str, timeout: Optional[int] = None
    ) -> None:
        timeout_ms = (
            timeout if timeout is not None else self.default_wait_time
        ) * 1000
        self.logger.info("Wait for element via %s", locator)
        self.page.wait_for_selector(locator, timeout=timeout_ms)

    def wait_for_element_visibility(self, locator: str, timeout: int) -> None:
        self.logger.info("Wait for element visibility via %s", locator)
        self.page.wait_for_selector(
            locator, state="visible", timeout=timeout * 1000
        )

    def wait_for_element_till_clickable(
        self, locator: str, timeout: int
    ) -> None:
        self.logger.info("Wait for element to be clickable: %s", locator)
        self.page.wait_for_selector(
            locator, state="visible", timeout=timeout * 1000
        )

    def wait_for_element_to_disappear(self, locator: str, timeout: int) -> None:
        self.page.wait_for_selector(
            locator, state="hidden", timeout=timeout * 1000
        )

    def wait_for_staleness(self, element: Locator, timeout: int) -> None:
        element.wait_for(state="detached", timeout=timeout * 1000)

    def wait_for_element_contains_text(
        self, locator: str, expected_text: str, wait_time: int
    ) -> None:
        counter = wait_time // 5
        for _ in range(counter):
            if expected_text in self.get_text(locator, 0):
                break
            self.wait_for_time(5)

    def wait_for_page_to_be_ready(self, wait_time: int) -> None:
        counter = wait_time // 5
        for _ in range(counter):
            try:
                state = self.page.evaluate("document.readyState")
                if state.lower() == "complete":
                    break
            except Exception as e:
                self.logger.info(e)
            self.wait_for_time(5)

    def wait_for_element_with_retries_and_refresh(
        self, locator: str, max_retries: int, wait_time_seconds: int
    ) -> bool:
        for _ in range(max_retries):
            if self.is_displayed(locator, wait_time_seconds):
                return True
            self.page_refresh()
            self.wait_for_time(wait_time_seconds)
        return False

    def time_for_element_to_appear(self, locator: str, timeout: int) -> float:
        start = time.time()
        self.wait_for_element(locator, timeout)
        return time.time() - start

    # ── Scrolling ──────────────────────────────────────────────────────────────

    def scroll_into_element_view(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        try:
            if isinstance(locator_or_ele, str):
                self.page.locator(locator_or_ele).first.scroll_into_view_if_needed()
            else:
                locator_or_ele.scroll_into_view_if_needed()
        except Exception as e:
            self.logger.error(
                "Error scrolling to element %s: %s", locator_or_ele, e
            )

    def scroll_to_element_center(self, locator: str) -> None:
        try:
            self.get_element(locator).evaluate(
                "el => el.scrollIntoView({block: 'center', inline: 'center'})"
            )
        except Exception as e:
            self.logger.error(
                "Error scrolling to element center %s: %s", locator, e
            )

    def scroll_into_bottom_of_element(self, locator: str) -> None:
        self.get_element(locator).evaluate(
            "el => el.scrollIntoView({block: 'end', behavior: 'smooth'})"
        )

    def scroll_to_top(self) -> None:
        self.page.evaluate("window.scrollTo(0, 0)")

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_horizontally(
        self,
        scroll_direction: str,
        container_locator: str,
        scroll_amount: int,
    ) -> None:
        try:
            scroll_offset = (
                scroll_amount if scroll_direction.lower() == "right" else -scroll_amount
            )
            self.get_element(container_locator).evaluate(
                f"el => {{ el.scrollLeft += {scroll_offset}; }}"
            )
            self.logger.info(
                "Scrolled %s by %d pixels in %s",
                scroll_direction,
                scroll_amount,
                container_locator,
            )
        except Exception as e:
            self.logger.error("Error during horizontal scroll: %s", e)

    def scroll_horizontally_until_element_found(
        self, custom_container: str, target_element: str, direction: str
    ) -> None:
        max_attempts = 50
        scroll_amount = 300
        attempt = 0
        self.logger.info(
            "Horizontal scroll in '%s' to find '%s'",
            custom_container,
            target_element,
        )
        while not self.is_displayed(target_element) and attempt < max_attempts:
            self.scroll_horizontally(direction, custom_container, scroll_amount)
            self.wait_for_time_in_ms(50)
            attempt += 1
        if self.is_displayed(target_element):
            self.scroll_into_element_view(target_element)
            self.logger.info("Target element found after %d attempts", attempt)
        else:
            self.logger.error(
                "Target element not found after %d scroll attempts", max_attempts
            )
            assert False, (
                f"Element '{target_element}' not found in '{custom_container}' "
                f"after scrolling {direction} for {max_attempts} attempts"
            )

    # ── JavaScript ─────────────────────────────────────────────────────────────

    def javascript_execution(
        self, script: str, element: Optional[Locator] = None
    ) -> None:
        try:
            if element:
                element.evaluate(f"el => {{ {script} }}")
            else:
                self.page.evaluate(script)
            self.logger.info("Script executed successfully: %s", script)
        except Exception as e:
            self.logger.error("Script execution failed: %s", script)
            raise e

    def execute_js_fetch_value(self, script: str) -> str:
        self.logger.info("executeJSFetchValue script: %s", script)
        result = self.page.evaluate(script)
        self.logger.info("Output: %s", result)
        return str(result) if result is not None else ""

    def get_java_script_return_value(self, java_script: str) -> str:
        result = self.page.evaluate(f"() => {java_script}")
        return str(result) if result is not None else ""

    def js_click(self, element: Locator) -> None:
        element.evaluate("el => el.click()")

    def click_element_using_js_executor(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        if isinstance(locator_or_ele, str):
            self.get_element(locator_or_ele).evaluate("el => el.click()")
        else:
            locator_or_ele.evaluate("el => el.click()")

    def click_on_dropdown_element_using_js(
        self, locator_or_ele: Union[str, Locator]
    ) -> None:
        if isinstance(locator_or_ele, str):
            ele = self.get_element(locator_or_ele)
        else:
            ele = locator_or_ele
        ele.evaluate("el => el.focus()")
        ele.evaluate(
            "el => el.dispatchEvent(new MouseEvent('mousedown', "
            "{bubbles: true, cancelable: true, view: window}))"
        )

    # ── Mouse ──────────────────────────────────────────────────────────────────

    def mouse_hover_on_element(self, locator: str) -> None:
        try:
            self.get_element(locator).hover()
        except Exception:
            self.wait_for_time(5)
            self.get_element(locator).hover()

    def get_and_click_on_element_by_coordinate(self, locator: str) -> None:
        try:
            box = self.get_element(locator).bounding_box()
            if box:
                center_x = box["x"] + box["width"] / 2
                center_y = box["y"] + box["height"] / 2
                self.page.mouse.click(center_x, center_y)
                self.logger.info(
                    "Clicked at center (%.1f, %.1f) of element '%s'",
                    center_x,
                    center_y,
                    locator,
                )
        except Exception as e:
            self.logger.error(
                "Failed to click on element '%s' at center: %s", locator, e
            )

    # ── Dropdowns ──────────────────────────────────────────────────────────────

    def select_value_from_dropdown(self, locator: str, value: str) -> None:
        self.get_element(locator).select_option(label=value)

    def get_dropdown_value(
        self, locator_or_ele: Union[str, Locator]
    ) -> str:
        try:
            if isinstance(locator_or_ele, str):
                ele = self.get_element(locator_or_ele)
            else:
                ele = locator_or_ele
            return ele.evaluate(
                "el => el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : ''"
            )
        except Exception as e:
            self.logger.error(e)
            return ""

    def get_drop_down_options_by_index(self, locator: str, index: int) -> None:
        self.get_element(locator).select_option(index=index)

    def get_drop_down_options_by_value(self, locator: str, value: str) -> None:
        self.get_element(locator).select_option(value=value)

    # ── Screenshots ────────────────────────────────────────────────────────────

    def get_screen_shot(self, file_name: str) -> None:
        try:
            os.makedirs(self.SCREENSHOT_DIR, exist_ok=True)
            path = os.path.join(self.SCREENSHOT_DIR, f"{file_name}.png")
            self.page.screenshot(path=path)
        except Exception as e:
            self.logger.error("Screenshot not taken: %s", e)

    def capture_specific_element_screenshot(self, locator: str) -> None:
        try:
            self.get_element(locator).screenshot(path=f"{locator}_image.png")
        except Exception as e:
            self.logger.error(e)

    # ── Frames ─────────────────────────────────────────────────────────────────

    def switch_to_iframe(self, locator: str) -> FrameLocator:
        """Returns a FrameLocator for locating elements within the matched iframe."""
        return self.page.frame_locator(locator)

    def switch_to_iframe_by_name(self, frame_name: str) -> None:
        """Stores the frame as context; use page.frame(name=...) for direct frame access."""
        frame = self.page.frame(name=frame_name)
        if frame is None:
            self.logger.error("Frame not found: %s", frame_name)
        else:
            self.logger.info("Switched to frame: %s", frame_name)

    def switch_to_iframe_by_number(self, iframe_number: int) -> None:
        frames = self.page.frames
        if iframe_number < len(frames):
            self.logger.info("Switched to iframe number: %d", iframe_number)
        else:
            self.logger.error(
                "Iframe number %d not available (%d frames)", iframe_number, len(frames)
            )

    def back_to_main_frame(self) -> None:
        self.logger.info(
            "In Playwright, use page.locator() directly to interact with the main frame"
        )

    def switch_to_default_frame(self) -> None:
        self.back_to_main_frame()

    def exit_i_frame(self) -> None:
        self.back_to_main_frame()

    # ── Windows / Tabs ─────────────────────────────────────────────────────────

    def get_windows(self) -> List[Page]:
        return self.page.context.pages

    def get_tabs_count(self) -> int:
        return len(self.page.context.pages)

    def switch_window(self, index: int) -> None:
        pages = self.page.context.pages
        if index < len(pages):
            self.page = pages[index]
        else:
            self.logger.error(
                "Window index %d not available (%d pages open)", index, len(pages)
            )

    def switch_to_last_tab(self) -> None:
        self.page = self.page.context.pages[-1]

    def switch_to_first_tab(self) -> None:
        self.page = self.page.context.pages[0]

    def switch_to_nth_tab(self, n: int) -> None:
        self.page = self.page.context.pages[n - 1]

    def switch_to_second_last_tab(self) -> None:
        pages = self.page.context.pages
        if len(pages) > 1:
            self.page = pages[-2]
        else:
            self.logger.info("Not enough tabs to switch to the second last one")

    def switch_to_tab_and_close_tab(
        self, tab_to_close: int, tab_to_switch: int
    ) -> None:
        try:
            pages = self.page.context.pages
            pages[tab_to_close].close()
            self.page = self.page.context.pages[tab_to_switch]
            self.logger.info("Tab closed and switched successfully")
        except Exception:
            self.logger.error("Tab close/switch failed")

    def switch_to_tab(self, from_tab: int, to_tab: int) -> None:
        try:
            self.page = self.page.context.pages[to_tab]
            self.logger.info("Switched to tab %d", to_tab)
        except Exception:
            self.logger.error("Tab switch failed")

    def switch_to_window_by_number(self, number: int) -> None:
        self.switch_window(number)

    def get_window_handles(self) -> None:
        for p in self.page.context.pages:
            self.page = p

    def open_new_tab(self, url: str) -> None:
        if not url or not url.strip():
            self.logger.error("Cannot open new tab: URL is null or empty")
            raise ValueError("URL cannot be null or empty")
        new_page = self.page.context.new_page()
        new_page.goto(url)
        self.page = new_page

    def is_child_window_displayed(self, url: str) -> bool:
        pages = self.page.context.pages
        if len(pages) < 2:
            return False
        child = pages[1]
        current_url = child.url
        self.logger.info("Child window URL: %s", current_url)
        child.close()
        self.page = self.page.context.pages[0]
        return url in current_url

    def close_tab(self) -> None:
        self.page.close()

    def close_driver(self) -> None:
        self.page.close()

    def refresh_child_window(self) -> None:
        pages = self.page.context.pages
        if len(pages) > 1:
            child = pages[1]
            for _ in range(5):
                self.wait_for_time(60)
                child.reload()
            self.wait_for_time(3)
            self.page = self.page.context.pages[0]

    # ── Cookies ────────────────────────────────────────────────────────────────

    def delete_all_cookie(self) -> None:
        self.page.context.clear_cookies()

    def delete_cookie(self, cookie_name: str) -> None:
        cookies = self.page.context.cookies()
        self.page.context.clear_cookies()
        remaining = [c for c in cookies if c["name"] != cookie_name]
        if remaining:
            self.page.context.add_cookies(remaining)

    def add_cookie(self, cookie_name: str, cookie_value: str) -> None:
        self.page.context.add_cookies(
            [
                {
                    "name": cookie_name,
                    "value": cookie_value,
                    "domain": ".openphone.com",
                    "path": "/",
                }
            ]
        )
        self.page.reload()

    # ── Network ────────────────────────────────────────────────────────────────

    def access_basic_authentication_website(
        self, website_url: str, user_name: str, password: str
    ) -> None:
        self.page.context.set_http_credentials(
            {"username": user_name, "password": password}
        )
        self.get_url(website_url)
        self.wait_for_time(10)

    def access_bad_ssl_website(self, url: str) -> None:
        # SSL certificate errors are ignored via ignore_https_errors=True
        # at browser context creation time in Playwright.
        self.get_url(url)

    def emulate_offline_network(self) -> None:
        self.page.context.set_offline(True)

    def get_normal_url_load_time(self, url: str) -> float:
        start = time.time()
        self.get_url(url)
        return (time.time() - start) * 1000

    def http_response_code_via_get(self, url: str) -> int:
        try:
            with urllib.request.urlopen(url) as response:
                return response.getcode()
        except Exception as e:
            self.logger.error("Error fetching URL %s: %s", url, e)
            return -1

    def emulate_geographical_location(
        self, latitude: float, longitude: float
    ) -> None:
        self.page.context.grant_permissions(["geolocation"])
        self.page.context.set_geolocation(
            {"latitude": latitude, "longitude": longitude}
        )

    # ── File Handling ──────────────────────────────────────────────────────────

    def upload_file(self, filename: str) -> None:
        try:
            self.page.locator("input[type='file']").set_input_files(filename)
            self.logger.info("File uploaded successfully")
        except Exception as e:
            self.logger.info("Error uploading file: %s", e)
            assert False, f"File Upload Failed: {e}"

    def write_data_to_text_file(self, file_name: str, data: str) -> None:
        os.makedirs(self.LOG_DIRECTORY, exist_ok=True)
        try:
            with open(
                os.path.join(self.LOG_DIRECTORY, f"{file_name}.txt"), "w"
            ) as f:
                f.write(data)
        except Exception as e:
            self.logger.error(e)

    def read_data_from_test_file(self, file_name: str) -> str:
        path = os.path.join("logs", f"{file_name}.txt")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(e)
            return ""

    def is_hook_file_exist(self, file_name_with_extension: str) -> bool:
        try:
            result = self.execute_js_fetch_value(
                f"lambda-file-exists={file_name_with_extension}"
            )
            return result.lower() == "true"
        except Exception:
            return False

    def get_all_downloaded_files(self, file_name: str) -> str:
        try:
            file_list_str = self.execute_js_fetch_value(
                f"lambda-file-list={file_name}"
            )
            if not file_list_str:
                return ""
            return file_list_str.replace("[", "").replace("]", "").strip()
        except Exception as e:
            self.logger.info("Error fetching file list: %s", e)
            return ""

    def is_file_exist_automation_test(
        self, file_name_with_extension: str, wait_time: int = 20
    ) -> bool:
        counter = wait_time // 2
        for _ in range(counter):
            if self.is_hook_file_exist(file_name_with_extension):
                return True
            self.wait_for_time(2)
        return self.is_hook_file_exist(file_name_with_extension)

    def get_file_content_base64(self, file_name_with_extension: str) -> str:
        try:
            return self.execute_js_fetch_value(
                f"lambda-file-content={file_name_with_extension}"
            )
        except Exception:
            return ""

    def close_file_dialog(self) -> None:
        try:
            self.logger.info("Closing file dialog using Escape key")
            self.page.keyboard.press("Escape")
            self.wait_for_time(2)
            self.logger.info("File dialog closed successfully")
        except Exception as e:
            self.logger.error("Error closing file dialog: %s", e)
            self.close_file_dialog_with_cancel_button()

    def close_file_dialog_with_cancel_button(self) -> None:
        try:
            cancel_button = "//button[text()='Cancel']"
            if self.is_displayed(cancel_button, 2):
                self.click_on_element(cancel_button)
                self.logger.info("File dialog closed using Cancel button")
            else:
                self.logger.info(
                    "Cancel button not found, dialog may already be closed"
                )
        except Exception as e:
            self.logger.error(
                "Error closing file dialog with Cancel button: %s", e
            )

    # ── Clipboard ──────────────────────────────────────────────────────────────

    def get_clipboard_text(self) -> str:
        try:
            return self.page.evaluate("() => navigator.clipboard.readText()") or ""
        except Exception:
            return ""

    def get_clipboard_content(self) -> str:
        original_page = self.page
        self.open_new_tab("https://the-internet.herokuapp.com/key_presses")
        self.switch_to_last_tab()
        self.wait_for_time(4)
        ele = self.get_element("input#target")
        self.paste_text(ele)
        text = self.get_attribute_value("input#target", "value") or ""
        self.close_tab()
        self.page = original_page
        self.logger.info("getClipboardContent text: %s", text)
        return text

    # ── Utility ────────────────────────────────────────────────────────────────

    def get_current_os(self) -> str:
        return platform.system()

    def get_resolution_of_current_screen(self) -> dict:
        return self.page.viewport_size or {}

    def device_override_mode(self, width: int, height: int) -> None:
        self.page.set_viewport_size({"width": width, "height": height})
        self.logger.info("Viewport set to %dx%d", width, height)

    def get_domain_from_url(self, url: str) -> str:
        try:
            if not url:
                return ""
            clean_url = re.sub(r"^https?://", "", url)
            end = len(clean_url)
            slash_idx = clean_url.find("/")
            query_idx = clean_url.find("?")
            if slash_idx > 0:
                end = min(end, slash_idx)
            if query_idx > 0:
                end = min(end, query_idx)
            return clean_url[:end]
        except Exception as e:
            self.logger.error("Error extracting domain from URL %s: %s", url, e)
            return url

    def rename_test(self, test_id: str) -> None:
        self.page.evaluate(f"_ => 'lambda-name={test_id}'")

    def get_shadow_element(self, locator: str) -> Locator:
        """Playwright handles shadow DOM natively via the >> piercing selector."""
        return self.page.locator(locator)

    def click_checkbox_inside_label(self, label_element: Locator) -> None:
        label_element.locator("input.ant-checkbox-input").evaluate(
            "el => el.click()"
        )

    def verify_all_elements_text_contains(
        self, locator: str, given_string: str
    ) -> None:
        actual_values = self.get_elements_text_lower_case(locator)
        self.logger.info("Actual elements: %s", actual_values)
        for value in actual_values:
            assert value in given_string.lower(), (
                f"Element not found in expected list: {value}. Expected: {given_string}"
            )

    def verify_all_elements_text_contains_any_list_elements(
        self, locator: str, given_list: List[str]
    ) -> None:
        actual_values = self.get_elements_text(locator)
        self.logger.info("Actual items: %s", actual_values)
        for ele in actual_values:
            split_values = ele.split()
            is_match = any(v in given_list for v in split_values)
            self.logger.info(
                "Processing item: %s, Match found: %s", ele, is_match
            )
            assert is_match, (
                f"Item not found in expected list: {ele}. Expected: {given_list}"
            )

    def list_element_click_and_verify_first_last(
        self,
        ele_list_locator: str,
        ele_to_verify: str,
        custom_message: str,
        action_wait: int,
    ) -> None:
        ele_list = self.get_elements(ele_list_locator)
        ele_list[0].click()
        self.wait_for_time(action_wait)
        assert self.is_displayed(ele_to_verify, self.default_wait_time), (
            f"{custom_message} element not showing with locator {ele_to_verify}"
        )
        click_index = len(ele_list) - 1 if len(ele_list) < 5 else 4
        ele_list[click_index].click()
        self.wait_for_time(action_wait)
        assert self.is_displayed(ele_to_verify, self.default_wait_time), (
            f"{custom_message} element not showing with locator {ele_to_verify}"
        )
