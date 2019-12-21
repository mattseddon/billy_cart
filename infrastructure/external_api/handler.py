from infrastructure.built_in.adapter.request import post_data, open_url
from private.details import (
    get_app_key,
    get_cert,
    get_exchange_url,
    get_account_url,
    get_login_url,
    get_user_details,
    get_account_str,
)


class ExternalAPIHandler:
    def __init__(self, environment="Prod"):
        self.environment = environment

    def get_headers(self):
        return self._headers

    def get_account_status(self):

        account_status = self._call_account()

        return account_status

    def set_headers(self):

        self._app_key = get_app_key(environment=self.environment)
        data = self._login()
        self._token = self._get_token(data=data)
        if self._has_token():
            self._headers = self._make_headers()
            return 1

        else:
            return 0

    def _call_account(self):
        dict = self._call_api(
            url=get_account_url(),
            request='{"jsonrpc": "2.0", "method": "%s"}' % get_account_str(),
        )
        account_status = self._try_get_data(dict=dict)
        return account_status

    def _call_exchange(self, request):
        dict = self._call_api(url=get_exchange_url(), request=request)
        data = self._try_get_data(dict=dict, name="result")
        return data

    def _post_instructions(self, request):
        dict = self._call_api(url=get_exchange_url(), request=request)
        data = self._try_get_data(dict=dict, name="instructionReports") or []
        return data

    def _call_api(self, url, request):
        dict = open_url(url=url, request=request, headers=self.get_headers())
        return dict

    def _try_get_data(self, dict, name="result"):
        try:
            result = dict.get(name)
        except:
            result = None
        return result

    def _login(self):
        response = post_data(
            url=get_login_url(),
            data=get_user_details(),
            cert=get_cert(),
            headers={
                "X-Application": self._app_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return response

    def _get_token(self, data):
        return data.get("sessionToken")

    def _has_token(self):
        return self._token is not None

    def _make_headers(self):
        return {
            "X-Application": self._app_key,
            "X-Authentication": self._token,
            "content-type": "application/json",
        }
