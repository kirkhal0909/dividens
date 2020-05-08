import datetime

import dividends_download
from pandas_datareader import data


__EXCHANGE_SUFFIX__ = '.ME'  #Upload prices from Moscow Exchange

def __strToDatetime__(strDate):    
    return datetime.datetime(*tuple(map(int,strDate)))

def __addMonth__(date,minus = False):    
    date = date.split('-')
    month = int(date[1])+1 - 2*minus
    if month<1:
        date[0] = str(int(date[0])-1)
        month = 12
    elif month>12:
        date[0] = str(int(date[0])+1)
        month = 1
    if month < 10:
        date[1] = '0'+str(month)
    else:
        date[1] = str(month)
    try:
        d = __strToDatetime__(date)
    except ValueError:
        date[2] = int(date[2])
        add = -1
        cont = False
        while not cont:
            date[2] += add
            try:
                d = __strToDatetime__(date)
                cont = True
            except ValueError:
                cont = False
        date[2] = str(date[2])
    return "-".join(date)

def __findPercent__(fromN,toN):
    if fromN >= toN:
        return format((toN/fromN-1)*100,'.2f')+'%'
    else:
        return '+' + format((toN/fromN-1)*100,'.2f')+'%'

def __downloadPeriod__(dividendBlock):
    date = dividendBlock[2]
    try:        
        period = data.DataReader(dividendBlock[1]+__EXCHANGE_SUFFIX__, 'yahoo', __addMonth__(date,True),__addMonth__(date))
        return period
    except KeyError:
        #Date start is the future
        return None

def statsCalc(dividendBlock):
    period = __downloadPeriod__(dividendBlock)
    if type(period) == type(None):
        return False
    rows = len(period)
    row = 0
    endDateBuy = dividendBlock[2]
    while row<rows and str(period.index[row]) < endDateBuy:
        row += 1
    #If period one month ago and last day of bought for dividends
    if row+1==rows:
        return False 
    if row<rows:

        #
        #Block before
        #
        
        minBefore = period.Close[row]*1000 #Find min close price
        workedDaysMinBefore = 0 #How many days ago
        rowBack = row-1
        while rowBack >= 0:
            if period.Close[rowBack] < minBefore:
                minBefore = period.Close[rowBack]
                workedDaysMinBefore = row-rowBack
            rowBack -= 1

        maxBefore = 0 #Find max close price
        workedDaysMaxBefore = 0 #How many days ago
        rowBack = row-1
        while rowBack >= 0:
            if period.Close[rowBack] > maxBefore:
                maxBefore = period.Close[rowBack]
                workedDaysMaxBefore = row-rowBack
            rowBack -= 1
        #
        #End block before
        #----------------------

        #Price at end buy and on next day
        closedPriceAtEndDateBuy = period.Close[row]
        closedPriceDayAfter = period.Close[row+1]
        #----------------------

        #
        #Block after
        #
        
        minAfter = period.Close[row]*1000 #Find min close price
        workedDaysMinAfter = 0 #How many days ago
        rowNext = row+1
        while rowNext < rows:
            if period.Close[rowNext] < minAfter:
                minAfter = period.Close[rowNext]
                workedDaysMinAfter = rowNext-row
            rowNext += 1

        maxAfter = 0 #Find max close price
        workedDaysMaxAfter = 0 #How many days ago
        rowNext = row+1
        while rowNext < rows:
            if period.Close[rowNext] > maxAfter:
                maxAfter = period.Close[rowNext]
                workedDaysMaxAfter = rowNext-row
            rowNext += 1
        #
        #End block after
        #----------------------
        
              
        return [minBefore,workedDaysMinBefore,maxBefore,workedDaysMaxBefore,
                closedPriceAtEndDateBuy,closedPriceDayAfter,
                minAfter,workedDaysMinAfter,maxAfter,workedDaysMaxAfter,dividendBlock[0]+' ('+dividendBlock[1]+' '+dividendBlock[2]+')']
    else:
        return False

def statsFormat(stats,easy = True):
    sign = '>=' if stats[2]>=stats[4] else '<'
    if easy:
        formated = "%s\t%d\t%s\t%.2f\t%.2f\t%s\t%d" % (stats[-1],
                               stats[1],
                               __findPercent__(stats[0],stats[4]),
                                stats[4],stats[5],
                                __findPercent__(stats[4],stats[8]),stats[9])
    else:
        formated = "%s\t%.2fp. (%s) %d рабоч.дней_перед\t%.2f\t%.2f\t%.2fp. (%s) %d рабоч.дней_после" % (stats[-1],
                                    stats[0],__findPercent__(stats[0],stats[4]),stats[1], #__findPercent__(stats[2],stats[4]),
                                     stats[4],stats[5],
                                     #__findPercent__(stats[4],stats[6]),
                                     stats[8],
                                     __findPercent__(stats[4],stats[8]),stats[9])
    #print(formated)
    return formated.replace('\t',';')
   
def statsFromYear(year = '',stop_after_none = True,writeToFile=True,easyOut = True):
    if not year:
        dividends = dividends_download.downloadData()
    else:
        dividends = dividends_download.downloadData(year)
    stats = []
    if writeToFile:
                import os
                folderName = 'info'
                if not os.path.exists(folderName):
                    os.mkdir(folderName)
                fileName = folderName+'/'
                if not year:
                    fileName += 'current_year.csv'
                else:
                    fileName += str(year)+'.csv'
                file = open(fileName,'w')
                if easyOut:
                    file.write('Компания(последняя дата покупки дивидендов);')
                    file.write('Рабочих дней от минимальной стоимости до конечной даты;')
                    file.write('От минимальной стоимости до стоимости в последней дате;')
                    file.write('Стоимость акции в последний день для получения дивидендов;')
                    file.write('Стоимость акции на следующий день после последнего дня покупки для получения дивидендов;')
                    file.write('От стоимости с последней даты до максимальной стоимости после;')
                    file.write('Рабочих дней от конечной даты до максимальной стоимости;')
                else:
                    file.write('Компания(последняя дата покупки дивидендов);')
                    file.write('Минимальная стоимость за месяц перед последней датой;')
                    file.write('Стоимость акции в последний день;')
                    file.write('Стоимость акции на следующий день после последней даты;')
                    file.write('Максимальная стоимость за месяц после последней даты;')
                file.write('\n')
                file.close()
    for pos in range(len(dividends)):        
        stat = statsCalc(dividends[pos])
        print('downloaded %d from %d records' % ((pos+1),len(dividends)))
        if stat:
            if writeToFile:
                file = open(fileName,'a')
                file.write(statsFormat(stat)+'\n')
                file.close()
            stats.append(stat)
        elif stop_after_none:
            return stats
    return stats

s = statsFromYear(2017)

#dividends = dividends_download.downloadData()
#period = __downloadPeriod__(dividends[0])
#s = statsCalc(dividends[0])
#print(statsFormat(s))

'''
for pos in range(len(dividends)):
    #period = __downloadPeriod__(dividends[pos])
    if not stats(dividends[pos]):
        print('not exists date range -',pos)
    else:
        print('normal -',pos)
'''
