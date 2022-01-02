from urllib.error import URLError
from urllib.request import Request, urlopen
from requests import post
from infrastructure.built_in.adapter.json_utils import make_dict


def post_data(url, data=None, cert=None, headers=None):
    response = post(url, data=data, cert=cert, headers=headers)
    if __is_ok(response=response):
        data = _add_ok_status(response.json())
    else:
        data = {}
    return data


def __is_ok(response):
    return response.status_code == get_ok_status()


def open_url(url, request, headers={}):
    try:
        request = URLRequest(url=url, request=request, headers=headers)
        return request.openurl()
    except URLError:
        return None


class URLRequest:
    def __init__(self, url, request, headers):
        self.__url = url
        self.__request = request
        self.__headers = headers
        self.__response = None

    def openurl(self):
        self.__get_response()
        if self.__is_ok():
            json_response = self.__response.read()
            data = _add_ok_status(data=make_dict(json_response.decode("utf-8")))
        else:
            data = {}
        return data

    def __get_response(self):
        urllib_request = Request(
            self.__url, self.__request.encode("utf-8"), self.__headers
        )
        self.__response = urlopen(urllib_request)

    def __is_ok(self):
        return self.__response.getcode() == get_ok_status()


def _add_ok_status(data):
    data["status_code"] = get_ok_status()
    return data


def get_ok_status():
    return 200
