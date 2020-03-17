import json
import os
import sys

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from parser.base import BaseSeleniumSite
from parser.constants import MOVIE, SLIDER_NEXT_BUTTON, MOVIES_SECTIONS, LOGIN_BUTTON, MAIN_CONTAINER, \
    PASSWORD_INPUT_BUTTON, INPUT_FIELD, EMAIL_INPUT_BUTTON, EMAIL_INPUT_FIELD
from utils import parse_config_file

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import asyncio

CONFIG = parse_config_file("config/config-dev.ini")
logger = logging.getLogger("parser")


class DisneySite(BaseSeleniumSite):
    def __init__(self, driver):
        BaseSeleniumSite.__init__(self, driver)
        self.base_url = "https://www.disneyplus.com/"

    async def _login(self):
        logger.debug("login to page %s" % self.base_url)
        async with self.driver.async_lock:
            self.driver.sel_set_input_value(
                self.driver.sel_wait_and_get(EMAIL_INPUT_FIELD),
                CONFIG["DEFAULT"]["login"]
            )
            self.driver.sel_click_until_appear(
                self.driver.sel_wait_and_get(EMAIL_INPUT_BUTTON),
                INPUT_FIELD)
        await asyncio.sleep(3)

        async with self.driver.async_lock:
            self.driver.sel_set_input_value(
                self.driver.sel_wait_and_get(INPUT_FIELD),
                CONFIG["DEFAULT"]["password"]
            )
            self.driver.sel_click(
                self.driver.sel_wait_and_get(PASSWORD_INPUT_BUTTON)
            )

        await asyncio.sleep(20)

    async def _load_page(self):
        logger.debug("load page %s" % self.base_url)
        async with self.driver.async_lock:
            self.driver.get(self.base_url, MAIN_CONTAINER)
        await asyncio.sleep(15)

        async with self.driver.async_lock:
            self.driver.sel_click_until_appear(
                self.driver.sel_wait_and_get(LOGIN_BUTTON),
                EMAIL_INPUT_BUTTON
            )
        await asyncio.sleep(5)

    async def load(self):
        await self._load_page()
        await self._login()
        WebDriverWait(self.driver, 180).until(
            expected_conditions.visibility_of_all_elements_located((By.XPATH, MOVIES_SECTIONS)))

    async def parse_data(self):
        soup = self.driver.find_elements_by_xpath(MOVIES_SECTIONS)
        async_tasks = []
        for container in soup:
            async_tasks.append(self._get_section_data(container))
        result = await asyncio.gather(*async_tasks)
        return result

    async def _get_section_data(self, container):
        await self._move_to_el(container)
        section = {}
        section["Name"] = container.find_element_by_tag_name('h4').text
        section["Items"] = []
        button = container.find_element_by_xpath(SLIDER_NEXT_BUTTON)
        while button:
            movies = container.find_elements_by_xpath(MOVIE)
            for movie in movies:
                res = self._get_movie_data(movie)
                section["Items"].append(res)

            self.driver.sel_js_click(button)
            logger.debug("click slider button")
            await asyncio.sleep(1)
            button = self.driver._check_exists_by_xpath(container,
                                                        SLIDER_NEXT_BUTTON)
        logger.debug("parsed section %s" % section)
        return section

    async def _move_to_el(self, container):
        actions = ActionChains(self.driver)
        actions.move_to_element(container).perform()
        await asyncio.sleep(1)

    def _get_movie_data(self, movie):
        res = {}
        res["name"] = movie.find_element_by_tag_name('img').get_attribute("alt")
        res["image"] = movie.find_element_by_tag_name('img').get_attribute("src") if movie.find_element_by_tag_name(
            'img') else None
        logger.debug("parsed movie %s" % res)
        return res

    async def run(self):
        await self.load()
        parsed_data = await self.parse_data()

        logger.debug(parsed_data)
        with open(CONFIG["DEFAULT"]["output_file"], "w") as file:
            file.write(json.dumps(parsed_data, indent=4, sort_keys=True))
