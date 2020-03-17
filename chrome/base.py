import asyncio
import logging
import os
import time

from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException, \
    NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from utils import get_os_name, sleep, get_xy_random, get_xy_center

OS_NAME = get_os_name()

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger("driver")


class BaseDriver(RemoteWebDriver):

    def __init__(self, *args, **kwargs):
        self.is_loaded = False
        self.is_exited = False
        self.current_iframes_xp = ""
        self.current_iframes_offset_x = 0
        self.current_iframes_offset_y = 0
        self.async_lock = asyncio.Lock()

    def __del__(self):
        self.quit()

    # static methods:

    @staticmethod
    def sel_select_option_by_text(sel_select, text_in):
        for sel_option in sel_select.find_elements_by_tag_name("option"):
            if text_in in sel_option.text:
                sel_option.click()

    @staticmethod
    def sel_parse_tbody(el):
        data = []
        rows = el.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            data.append(tuple([col.text for col in row.find_elements(By.TAG_NAME, "td")]))
        return data

    def get_scroll_offset(self):
        return self.execute_script(
            """var supportPageOffset = window.pageXOffset !== undefined;\nvar isCSS1Compat = ((document.compatMode || "") === "CSS1Compat");\nvar x = supportPageOffset ? window.pageXOffset : isCSS1Compat ? document.documentElement.scrollLeft : document.body.scrollLeft;\nvar y = supportPageOffset ? window.pageYOffset : isCSS1Compat ? document.documentElement.scrollTop : document.body.scrollTop; return [x, y];""")

    def _sel_wait_and_get(self, xpath, timeout=180):  # without iframes
        logger.debug("_sel_wait_and_get for '%s' with timeout %i" % (xpath, timeout))
        try:
            return WebDriverWait(self, timeout).until(
                expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            raise TimeoutError()

    def sel_wait_and_get(self, xpath, timeout=180):
        logger.debug("sel_wait_and_get for '%s' with timeout %i" % (xpath, timeout))
        xpath = xpath.rsplit(":", 1) if ":" in xpath else ["", xpath]
        return self._sel_wait_and_get(xpath[1], timeout=timeout)

    def sel_js_wait_and_get(self, xpath):
        return self.execute_script('''
        function getElementByXpath(path) {
            return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        }
        return getElementByXpath(arguments[0]);
        ''', xpath)

    def sel_wait_click_hard(self, el, timeout=180):
        t_deadline = time.time() + timeout
        logger.debug("sel_wait_click_hard with timeout %i" % timeout)
        while time.time() < t_deadline:
            try:
                self.sel_click(el)
                return
            except WebDriverException as e:
                if ("is not clickable" not in str(e)) and ("Element is not currently interactable" not in str(e)):
                    raise
            sleep(3)
        raise TimeoutError()

    def sel_click_until_appear(self, el, xpath_appear, timeout=180):
        t_deadline = time.time() + timeout
        logger.debug("sel_click_until_appear xpath_appear='%s' with timeout %i" % (xpath_appear, timeout))
        while time.time() < t_deadline:
            self.sel_wait_click_hard(el, timeout)
            try:
                return self.sel_wait_and_get(xpath_appear, 5)
            except StaleElementReferenceException:
                self.sel_click_until_appear(el, xpath_appear)
            except TimeoutError:
                pass
        raise TimeoutError()

    def sel_click(self, element, regular=False):
        if regular:
            element.click()
        else:
            el_size = element.size
            x2, y2 = el_size["width"], el_size["height"]
            if (x2 > 2) and (y2 > 2):
                x, y = get_xy_random(1, 1, x2 - 1, y2 - 1)
            else:
                x, y = get_xy_center(0, 0, x2, y2)
            self.sel_click_at(element, x, y)

    def sel_js_click(self, element):
        self.execute_script("arguments[0].click()", element)

    def _check_exists_by_xpath(self, element, xpath):
        try:
            return element.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False

    def sel_set_input_value(self, sel_input, val):
        try:
            sel_input.click()
        except:
            pass
        try:
            self.execute_script("arguments[0].value = '';", sel_input)
        except:
            pass
        sleep(1)
        sel_input.clear()
        sleep(1)
        sel_input.send_keys(val)

    def sel_js_set_input_value(self, sel_input, val):
        try:
            self.execute_script(f'arguments[0].value = "{val}";', sel_input)
        except:
            pass

    def scroll_top(self):
        self.find_element_by_tag_name("body").send_keys(Keys.CONTROL + Keys.HOME)

    def sel_move_to(self, el):
        self.execute_script("arguments[0].scrollIntoView();", el)

    def sel_click_at(self, el, x, y):
        ActionChains(self).move_to_element_with_offset(el, x, y).click().perform()
