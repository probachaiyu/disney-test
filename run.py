import asyncio
import logging

from chrome.chrome import ChromeDriver
from parser.disney import DisneySite
from utils import setup_logger

logger = setup_logger("parser", "./logs/logs.txt", level=logging.DEBUG)


async def main():
    driver = ChromeDriver()
    driver.load()
    await asyncio.sleep(1)
    await DisneySite(driver).run(),


def run():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()


if __name__ == '__main__':
    run()
