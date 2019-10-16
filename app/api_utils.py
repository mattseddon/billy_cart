from urllib.error import URLError
from urllib.request import Request, urlopen
from requests import post


def post_request(url, data=None, cert=None, headers=None):
    response = post(url, data=data, cert=cert, headers=headers)
    if __is_ok(response):
        data = response.json()
        data["status_code"] = 200
    else:
        data = {}
    return data


def __is_ok(response):
    return response.status_code == 200
