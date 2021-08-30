import numpy as np
import pandas as pd
import sys
from datetime import date
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import time
import datetime
import math

# Calculates Beta for CAPM model
# Beta = Covariance/Variance 
#      = the correlation between portfolio and market * (std of returns of portfolio/ std of returns of market)
# Covariance=Measure of a stock’s return relative to that of the market
# Variance=Measure of how the market moves relative to its mean
#
# params: investment portfolio, market portfolio, period length
# return: beta
def calculate_beta(rp, mkt, period = 5):
    # extract data for the period
    cleanrp = rp[(rp['Day'].dt.year > 2019-period) & (rp['Day'].dt.year <= 2019)]
    cleanmkt = mkt[(mkt['Date'].dt.year > 2019-period) & (mkt['Date'].dt.year <= 2019)]
    # drop rows with non-trading days
    cleanrp = cleanrp.dropna(subset=['WTISpot'])
    cleanmkt = cleanmkt.dropna(subset=['Price'])
    
    cleanrp = cleanrp.set_index('Day')
    cleanmkt = cleanmkt.set_index('Date')
    # convert prices to rate of returns
    cleanrp = cleanrp.pct_change()
    cleanmkt = cleanmkt.pct_change()
    
    # covariance(WTI return, market return)
    cov = cleanrp['WTISpot'].cov(cleanmkt['Price'])
    # variance of market return
    var = cleanmkt['Price'].var()
    # Beta = Covariance/Variance
    beta = cov/var
    
    # cov / var = beta = corr * (stdp/stdm)
    
    corr = cleanrp['WTISpot'].corr(cleanmkt['Price'])
    stdp = cleanrp['WTISpot'].std()
    stdm = cleanmkt['Price'].std()
    
    #plt.figure()
    #plt.plot(cleanmkt)
    #plt.show()
    return beta

# Calculates Daily Excess Return
# using CAPM for expected return
# excess return = rp - [rf + beta*(rm-rf)]
# params: risk-free rates, investment portfolio, market portfolio, beta
# return: daily excess return between 12/31/2019 - 12/31/2020
def calculate_excess(rf, rp, rm, beta):
    # extract data for the period
    cleanrf = rf[(rf['DATE'] >= '2019-12-31') & (rf['DATE'] <= '2020-12-31')]
    cleanrp = rp[(rp['Day'] >= '2019-12-31') & (rp['Day'] <= '2020-12-31')]
    cleanrm = rm[(rm['Date'] >= '2019-12-31') & (rm['Date'] <= '2020-12-31')]

    # drop non-trading days
    cleanrf = cleanrf[cleanrf.DTB3 != '.']
    cleanrp = cleanrp.dropna(subset=['WTISpot'])
    cleanrm = cleanrm.dropna(subset=['Price'])

    cleanrf = cleanrf.set_index('DATE')
    cleanrp = cleanrp.set_index('Day')
    cleanrm = cleanrm.set_index('Date')
    #plt.figure()
    #plt.plot(cleanrp)
    #plt.show()
    
    # calculate daily risk-free rate
    cleanrf = cleanrf['DTB3'].apply(lambda a: (1 + float(a)/100)**(1/365)-1)
    # convert prices to rate of returns
    cleanrp = cleanrp.pct_change()
    cleanrm = cleanrm.pct_change()

    # combine dataFrames and add Daily Excess Return colume 
    data = pd.concat([cleanrf, cleanrp, cleanrm], axis=1).dropna()
    data['DailyExr'] = pd.Series(dtype = 'float64')
    
    # for each row/day, calculate excess return using formula:
    # excess return = rp - expected return
    #               = rp - [rf + beta*(rm-rf)]
    for index, row in data.iterrows():
        exc = row['WTISpot'] - (row['DTB3'] + beta*(row['Price'] - row['DTB3']))
        row['DailyExr'] = exc
    

    return data['DailyExr']*100

# Calculates log cumulative excess return
# log(portfolio return - expected return)
# using 10 year T-bill rate for risk-free rate because the period is longer than 3MO
# params: investment portfolio, market portfolio, beta, risk-free rate
# return: log cumulative excess return
def calculate_log_cumulative(rp, rm, beta, rf = 0.0192):

    # get beginning and ending price for WTI Spot
    startp = rp.loc[rp['Day'] =='2019-12-31']['WTISpot'].values[0]
    endp = rp.loc[rp['Day'] =='2020-12-31']['WTISpot'].values[0]
    # get beginning and ending price for benchmark market
    startm = rm.loc[rm['Date'] =='2019-12-31']['Price'].values[0]
    endm = rm.loc[rm['Date'] =='2020-12-31']['Price'].values[0]
    
    # find return for both portfolio and market over the period
    crp = (endp - startp) / startp
    crm = (endm - startm) / startm
    # calculate expected return using CAPM
    capm = rf + beta * (crm - rf)
    # calculate cumulative excess return
    cum_excess = crp - capm

    return math.log(1+cum_excess)


if __name__ == "__main__":
    

    # reading files from command line
    # 3MO T-bill: argv[1]   ----- risk-free rate   rf
    # WTI spot price: argv[2] ----- investment portfolio      rp
    # SPGSCI index: argv[3] ----- commodity market portfolio/benchmark    spgsci
    # SP500: argv[4] ----- general market portfolio/benchmark       spx
    rf = pd.read_csv(sys.argv[1])
    rp = pd.read_csv(sys.argv[2])
    spgsci = pd.read_csv(sys.argv[3], thousands=',')
    spgsci = spgsci.drop(spgsci.columns[[2,3,4,5,6]], axis=1) 
    spx = pd.read_csv(sys.argv[4], thousands=',')
    spx = spx.drop(columns=['Open', 'High','Low','Vol.','Change %'], axis=1)

    # format all dates
    rf['DATE'] = pd.to_datetime(rf['DATE'], infer_datetime_format=True)
    rp['Day'] = pd.to_datetime(rp['Day'], format = '%m/%d/%Y',infer_datetime_format=True)
    spgsci['Date'] = pd.to_datetime(spgsci['Date'], infer_datetime_format=True)
    spx['Date'] = pd.to_datetime(spx['Date'], infer_datetime_format=True)


    print("Using SPGSCI as benchmark")
    beta = calculate_beta(rp,spgsci)
    print("Beta: ", beta)
    output = calculate_excess(rf, rp, spgsci, beta)
    output.to_csv('Daily_ER_result_spgsci.csv',header=False)
    print("Daily Excess Return: \n", output)
    log_exc = calculate_log_cumulative(rp,spgsci, beta)
    print("Log Cumulative Excess Return: ",log_exc*100, '%')

    print("\n \nUsing S&P500 as benchmark")
    beta = calculate_beta(rp,spx)
    print("Beta: ", beta)
    output = calculate_excess(rf, rp, spx, beta)
    output.to_csv('Daily_ER_result_spx.csv',header=False)
    print("Daily Excess Return: \n", output)
    log_exc = calculate_log_cumulative(rp,spx, beta)
    print("Log Cumulative Excess Return: ",log_exc*100,'%')











