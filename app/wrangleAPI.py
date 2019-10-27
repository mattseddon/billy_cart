import os
import io
import datetime
from shared import UTCNormalFormat, pth, betfairExchangeURL, betfairAccountURL
import shared
from fileHelpers import md, writeFile
from dateHelpers import getUTCNow
from APIHelpers import callAping


def getMarkets(eventTypeID, toDateTime):
    """
    returns a list of markets starting before the toDateTime
    """
    print("    > markets:", getUTCNow().strftime(UTCNormalFormat))

    marketCats = (
        "{"
        '"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketCatalogue",'
        '"params" : '
        "{"
        '"filter":'
        "{"
        '"eventTypeIds":["' + eventTypeID + '"],'
        '"marketTypeCodes":["WIN"],'
        '"marketCountries":["AU","GB","IE"],'
        '"marketStartTime":{"to":"' + toDateTime + '"}'
        "},"
        '"sort":"FIRST_TO_START",'
        '"maxResults":"1000",'
        '"marketProjection":["MARKET_START_TIME","EVENT"]'
        "}"
        "}"
    )

    markets = callAping(betfairExchangeURL, marketCats)

    return markets


def getMarket(market):
    """
    stores API json data to the correct file for a single market
    """
    marketId = market.get("marketId")
    marketName = market.get("marketName")

    event = market.get("event")
    eventId = event.get("id")
    eventName = event.get("name")
    eventCountry = event.get("countryCode")

    print("     > market:", marketName, "@", eventName)

    eventPath = pth + str(eventId) + "/"
    eventFile = eventPath + str(eventId) + ".txt"

    # make the directory if it doesn't exist and dump the event information into a new file there
    md(eventPath)
    if not os.path.exists(eventFile):
        writeFile(eventFile, event)

    # remove the event information from the dictionary as it is already stored
    del market["event"]

    # get current time for et (extract time) in file
    now = getUTCNow().strftime(UTCNormalFormat)

    marketList = (
        '{"jsonrpc": "2.0", "method": "SportsAPING/v1.0/listMarketBook",'
        '"params": '
        "{"
        '"marketIds":['
        + marketId
        + '],"priceProjection":{"priceData":["EX_BEST_OFFERS","SP_AVAILABLE","SP_TRADED","EX_TRADED"]},'
        '"marketProjection":["MARKET_START_TIME"]'
        "}"
        ', "id": 1}'
    )

    odds = callAping(betfairExchangeURL, marketList)

    market.update({"marketInfo": odds, "et": now})

    marketFile = eventPath + str(marketId) + ".txt"

    writeFile(marketFile, market)

    return marketFile, marketId, eventCountry


def getAccountStatus():
    """
    returns global variables that relate to the status of the account
    balance (bank),
    Betfair turnover points (betfairPoints),
    turnover commission reduction (discountRate)
    """
    accountFunds = '{"jsonrpc": "2.0", "method": "AccountAPING/v1.0/getAccountFunds"}'

    getAccountStatus = callAping(betfairAccountURL, accountFunds)

    shared.bank = getAccountStatus.get("availableToBetBalance")
    betfairPoints = getAccountStatus.get("pointsBalance")
    shared.discountRate = getAccountStatus.get("discountRate") / 100

    print("     > account status: balance=$" + str(shared.bank) + ",")
    print("points=" + str(betfairPoints) + ",")
    print("discount rate=" + str(shared.discountRate))

    return None
