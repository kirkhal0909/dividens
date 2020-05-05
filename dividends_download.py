def __currentYear__():
    import datetime
    return datetime.datetime.now().year

__YEAR__ = __currentYear__()
#GET request link for get dividends
__LINK__ = 'https://api.open-broker.ru/data/v2.0/corporate_events/dividends?date_from=%d-01-01&rowsCount=9999999&orderBy=FixingDate+&status=&instrument_Id=&search_text='

#  Download dividends data for specific year
#
#  downloadData() - download dividends data for current year setted on PC
#  downloadData(2019) - download dividends data for 2019 year
#
#  if response HTTP code == 200:
#        return [[CompanyName,companySymbol,LastDayForDividend],[...],...]
#  else:
#        return response_HTTP_code
def downloadData(year = 0):
    import requests
    if year == 0: year = __YEAR__
    request = requests.get(__LINK__ % year)
    if request.status_code == 200:
        return __parseData__(request.json()['Dividends'])
    else:
        print('in downloadData()')
        print('response %d http' % request.status_code)
        return request.status_code

def __parseBlock__(block):
    return [block['InstrumentName'],
            block['InstrumentCode'],
            block['LastDayCanBuy'].split('T')[0],
            ]

def __parseData__(data):
    parsed = []
    for block in data:
        parsed.append(__parseBlock__(block))
    return parsed


#dividends = downloadData()
#dividends = downloadData(2020)
