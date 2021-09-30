from app.market.handler import MarketHandler

from infrastructure.external_api.market.handler import ExternalAPIMarketHandler

from infrastructure.built_in.adapter.date_time import DateTime


class ScheduleHandler:
    def __init__(self, external_api):
        self.external_api = external_api

    def get_schedule(self):
        return self.external_api.get_schedule("7", DateTime.utc_5_minutes_from_now())

    def create_new_markets(self, schedule):
        scheduled_markets = []
        for market in schedule:
            market_id = float(market.get("marketId"))
            external_api = ExternalAPIMarketHandler(
                market_id=market_id, headers=self.external_api.get_headers()
            )
            market_handler = MarketHandler(
                market_id=market_id,
                market_start_time=market.get("marketStartTime"),
                external_api=external_api,
            )
            external_api.set_mediator(mediator=market_handler)
            scheduled_markets.append(market_handler)
        return scheduled_markets
