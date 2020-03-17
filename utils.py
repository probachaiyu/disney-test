import configparser
import logging
import os
import random
import sys
import time
from urllib.parse import urlparse

logger = logging.getLogger("automation_tools")


def parse_config_file(filename):
    f = configparser.ConfigParser()
    f.read(filename)
    return f


def setup_logger(name, filename, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.handlers.clear()
    formatter = logging.Formatter('[%(levelname)-5s][%(asctime)s %(filename)-20s:%(lineno)-4d] %(message)s')
    formatter_console = logging.Formatter('[%(levelname)-5s] %(asctime)s %(message)s')
    file_dirname = os.path.dirname(filename)
    if not os.path.exists(file_dirname):
        os.makedirs(file_dirname)
    fh = logging.FileHandler(filename, 'a', 'utf-8')
    fh.setLevel(level)
    fh.setFormatter(formatter)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(level)
    sh.setFormatter(formatter_console)
    logger.setLevel(level)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def get_os_name():
    return {"win32": "windows", "linux": "ubuntu", "darwin": "macos"}[sys.platform]


def sleep(s):
    logger.debug(f"time.sleep({s})")
    tend = time.time() + s
    while time.time() <= tend:
        time.sleep(0.2)


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


def get_xy_center(x1, y1, x2, y2):
    return ((x1 + x2) // 2), ((y1 + y2) // 2)


def get_xy_random(x1, y1, x2, y2):
    if (x1 > x2) or (y1 > y2):
        raise Exception("wrong area coordinates")
    return random.randint(x1, x2), random.randint(y1, y2)


def get_host_from_url(url):
    return "{url.scheme}://{url.netloc}/".format(url=urlparse(url))
