import requests
from urllib.parse import urljoin


class Api:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password

    def get(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.get(url, auth=(self.username, self.password), **kwargs)

    def post(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.post(url, auth=(self.username, self.password), **kwargs)

    def patch(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.patch(url, auth=(self.username, self.password), **kwargs)

    def delete(self, path, **kwargs):
        url = urljoin(self.host, path)
        return requests.delete(url, auth=(self.username, self.password), **kwargs)