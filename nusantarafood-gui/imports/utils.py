import os
from urllib.parse import urlparse


def load_cfg(filename):
    with open(filename, 'r') as env_file:
        lines = env_file.read().splitlines()

    settings = dict()
    for line in lines:
        if line and line[0] != '#':
            key, value = line.split('=', 1)
            settings[key] = value

    return settings


def is_absolute(url):
    return bool(urlparse(url).netloc)


def create_dir(path="downloads"):
    if not os.path.exists(path):
        os.mkdir(path)