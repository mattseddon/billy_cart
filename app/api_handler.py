import urllib
import json
import requests
from private.details import (
    get_app_key,
    get_cert,
    get_account_url,
    get_exchange_url,
    get_login_url,
    get_user_details,
)
from app.singleton import Singleton


class APIHandler(metaclass=Singleton):
    def __init__(self, environment="Prod"):
        self.app_key = get_app_key(environment=environment)
        self.cert = get_cert()
        self.account_url = get_account_url()
        self.exchange_url = get_exchange_url()
        self.login_url = get_login_url()
        self.user_details = get_user_details()
        self.set_headers()

    def set_headers(self, environment="Prod"):

        response = self.__login()
        if self.__is_ok(response):
            self.headers = self.__make_headers(response=response)
            return 1

        else:
            return 0
            # print("   > Request failed.")

    def __login(self):
        response = requests.post(
            self.login_url,
            data=self.user_details,
            cert=self.cert,
            headers={
                "X-Application": self.app_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return response

    def __is_ok(self, response):
        return response.status_code == 200

    def __make_headers(self, response):
        return {
            "X-Application": self.app_key,
            "X-Authentication": self.__get_token(response=response),
            "content-type": "application/json",
        }

    def __get_token(self, response):
        dict = response.json()
        # print("   > login status: " + resp_json["loginStatus"].lower())
        token = dict["sessionToken"]
        return token

    def get_account_status(self):

        account_status = self.__call_api(
            url=self.account_url,
            request='{"jsonrpc": "2.0", "method": "AccountAPING/v1.0/getAccountFunds"}',
        )

        return account_status

    def get_market(self, market_id):

        marketList = (
            '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook","params":{"marketIds":['
            + market_id
            + '],"priceProjection":{"priceData":["EX_BEST_OFFERS","SP_AVAILABLE","SP_TRADED","EX_TRADED"]},"marketProjection":["MARKET_START_TIME"]}, "id": 1}'
        )

        market = self.__call_api(url=self.exchange_url, request=marketList)
        return market[0]

    def get_markets(self, eventTypeID, toDateTime):

        market_categories = (
            '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue","params" : {"filter":{"eventTypeIds":["'
            + eventTypeID
            + '"],"marketTypeCodes":["WIN"],"marketCountries":["AU","GB","IE"],"marketStartTime":{"to":"'
            + toDateTime
            + '"}},"sort":"FIRST_TO_START","maxResults":"1000","marketProjection":["MARKET_START_TIME","EVENT"]}}'
        )

        markets = self.__call_api(url=self.exchange_url, request=market_categories)
        return markets

    def __call_api(self, url, request):
        try:
            return self.__process_request(url, request)

        except urllib.error.URLError:
            # print("     > Oops there is some issue with the request")
            return None

    def __process_request(self, url, request):
        response = self.__get_response(url=url, request=request)
        data = self.__process_response(response=response)
        return data

    def __get_response(self, url, request):
        urllib_request = urllib.request.Request(
            url, request.encode("utf-8"), self.headers
        )
        response = urllib.request.urlopen(urllib_request)
        return response

    def __process_response(self, response):
        dict = self.__get_dict(response=response)
        result = self.__try_get_result(dict=dict)
        return result

    def __get_dict(self, response):
        json_response = response.read()
        dict = json.loads(json_response.decode("utf-8"))
        return dict

    def __try_get_result(self, dict):
        try:
            result = dict["result"]
        except:
            result = None
        return result