import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from utils import sleep, get_host_from_url, get_os_name
from .base import BaseDriver

OS_NAME = get_os_name()


class ChromeDriver(BaseDriver, webdriver.Chrome):

    def load(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--test-type')
        chrome_options.add_argument('--disable-fre')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument("--disable-site-isolation-for-policy")
        chrome_options.add_argument("--disable-site-isolation-trials")

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"

        if OS_NAME == "ubuntu":
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36")
            webdriver.Chrome.__init__(self, os.path.join(".", "bin", "chromedriver_ubuntu"), options=chrome_options,
                                      desired_capabilities=caps)
        elif OS_NAME == "windows":
            webdriver.Chrome.__init__(self, os.path.join(".", "bin", "chromedriver_windows.exe"),
                                      options=chrome_options, desired_capabilities=caps)
        elif OS_NAME == "macos":
            chrome_options.binary_location = os.path.join(".", "bin", "Google Chrome.app/Contents/MacOS/Google Chrome")
            webdriver.Chrome.__init__(self, os.path.join(".", "bin", "chromedriver"),
                                      options=chrome_options, desired_capabilities=caps)

        self.set_page_load_timeout(180)
        self.is_loaded = True
        self.implicitly_wait(10)
        sleep(2)
        self.maximize_window()

    def get(self, url, xpath='', timeout=180):
        if url[0] == "/":
            host_url = get_host_from_url(self.current_url)
            url = host_url + url[1:]

        if self.current_url != url:
            webdriver.Chrome.get(self, url)
            if xpath:
                WebDriverWait(self, timeout).until(
                    expected_conditions.visibility_of_all_elements_located((By.XPATH, xpath)))
            return True
        else:
            return False

    def get_version(self):
        return self.capabilities["browserVersion"]


if __name__ == "__main__":
    d = ChromeDriver()
    d.load()
    sleep(1000)
