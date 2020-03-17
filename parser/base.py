import logging

from chrome.chrome import ChromeDriver

logger = logging.getLogger("parser")


class BaseSeleniumSite:

    def __init__(self, driver: ChromeDriver):
        self.driver = driver

    async def load(self):
        pass

    async def login(self):
        pass

    async def parse_data(self):
        return []
