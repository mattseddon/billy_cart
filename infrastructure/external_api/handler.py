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
        self._app_key = None
        self._token = None
        self._headers = None

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

        return 0

    def _call_account(self):
        response = self._call_api(
            url=get_account_url(),
            request='{"jsonrpc": "2.0", "method": "%s"}' % get_account_str(),
        )
        account_status = self._try_get_data(data=response)
        return account_status

    def _call_exchange(self, request):
        response = self._call_api(url=get_exchange_url(), request=request)
        data = self._try_get_data(data=response, name="result")
        return data

    def _post_instructions(self, request):
        response = self._call_api(url=get_exchange_url(), request=request)
        data = self._try_get_data(data=response, name="instructionReports") or []
        return data

    def _call_api(self, url, request):
        response = open_url(url=url, request=request, headers=self.get_headers())
        return response

    def _try_get_data(self, data, name="result"):
        try:
            result = data.get(name)
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
