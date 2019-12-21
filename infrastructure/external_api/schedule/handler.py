from infrastructure.external_api.handler import ExternalAPIHandler
from app.schedule.interface import ExternalAPIScheduleInterface
from infrastructure.built_in.adapter.request import post_data, open_url
from private.details import get_catalogue_str

class ExternalAPIScheduleHandler(ExternalAPIHandler, ExternalAPIScheduleInterface):
    def __init__(self, environment="Prod"):
        ExternalAPIHandler.__init__(self, environment=environment)
        self.set_headers()

    def get_schedule(self, event_type_id, to_date_time):

        request = (
            '{"jsonrpc": "2.0", "method": "%s",'
            '"params" : {"filter":{"eventTypeIds":["%s"],"marketTypeCodes":["WIN"],"marketCountries":["AU","GB","IE"],'
            '"marketStartTime":{"to":"%s"}},"sort":"FIRST_TO_START","maxResults":"1000",'
            '"marketProjection":["MARKET_START_TIME","EVENT"]}}'
        ) % (get_catalogue_str(), event_type_id, to_date_time)

        schedule = self._call_exchange(request=request)
        return schedule
