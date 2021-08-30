# LIT_TakeHomeTest
This repository is for LIT's take home test project
* Files Received in the email:
  * 3MO.csv
  * RWTCd.xls
    * Cushing_OK_WTI_Spot_Price_FOB.csv  
* Files Added to complete the project:
  * [SP500.csv](https://www.investing.com/indices/)
  * [SPGSCI.csv](https://www.investing.com/indices/)
  * new_Cushing.csv (formated Cushing_OK_WTI_Spot_Price_FOB.csv from command line)
* Python file:
  * excess.py

Please have all listed file stored in local directory for the program to function

## To run:

> $ python excess.py 3MO.csv new_Cushing.csv SPGSCI.csv SP500.csv 

## Result Breakdown:
The program will have **two blocks of output on screen**, `Using SPGSCI as benchmark` and `Using S&P500 as benchmark`, 

where **SPGSCI** is the S&P Goldman Sachs Commodity Index _(default)_

and **S&P500** is just a more general index

The output will have format:
```
Using _____ as benchmark
Beta: _____
Daily Excess Return:
   head 
   and 
   tail
Log Cumulative Excess Return: _____ %

```
Expected output:
```
Using SPGSCI as benchmark
Beta:  1.7103905592286368
Daily Excess Return: 
 2020-01-02    0.028606
2020-01-03    0.438742
2020-01-06   -0.062864
2020-01-07   -0.021840
2020-01-08   -0.487897
                ...   
2020-12-24    0.445795
2020-12-28   -0.211176
2020-12-29   -0.476789
2020-12-30   -0.514286
2020-12-31   -0.455489
Name: DailyExr, Length: 249, dtype: float64
Log Cumulative Excess Return:  -9.499716509206957 %

 
Using S&P500 as benchmark
Beta:  0.7810306051124787
Daily Excess Return: 
 2020-01-02   -0.606240
2020-01-03    3.542173
2020-01-06    0.151692
2020-01-07   -0.682861
2020-01-08   -5.248227
                ...   
2020-12-24    0.224354
2020-12-28   -2.092695
2020-12-29    0.910746
2020-12-30    0.710220
2020-12-31   -0.274920
Name: DailyExr, Length: 249, dtype: float64
Log Cumulative Excess Return:  -41.609650294905094 %
```

And **two output files** naming `Daily_ER_result_spgsci.csv` and `Daily_ER_result_spx.csv` which contain ful daily excess return results. The numbers are expressed in percentage.

Depending on the portfolio structure: 

if account is restricted to commodities only, obviously SPGSCI would be more appropriate

## Approach

#### Define excess return

`excess return = portfolio return - expected return`

I used **CAPM** model for expected return

` ER = Rf + β*(Emkt - Rf) `

#### Rf

for Daily Excess return, I used the 3Mo T-bill rate as risk-free rate, by converting it to daily rate

`( 1 + r/100 ) ^ ( 1/365 ) - 1`

for cumulative excess return, I used 10-year T-bill rate which was `1.92% @12/31/2019`

#### β

` Beta = Covariance/Variance `

Beta is calculated using Coveriance between portfolio(WTI) and market and Variance of the portfolio

_Covariance = Measure of a portfolio return relative to that of the market_

_Variance = Measure of how the market moves relative to its mean_


which can also be expressed as

`Beta = correlation between portfolio and mkt * (std Rportfolio / std Rmkt)`

#### Emkt

`( P_t1 - P_t0 )/( P_t0 )`

#### Log Cumulative Excess Return
Cumulative Excess Return is just extending the period of calculation to the period of 12/31/2019-12/31/2020 and take log of the result.

` ln(1+r) = R ` where r is simple return and R is the log return

## excess.py Breakdown

`calculate_beta()` - calculates beta, using the convention of 5-year data

`calculate_excess()` - calculates daily excess return

`calculate_log_cumulative()` - calculates log cumulative excess return, using the convention of 10-year T-bill as risk-free rate

Program reads 4 input files from command line arguments. Then it generates two sets of result using different benchmark index. It will also output two files naming `Daily_ER_result_spgsci.csv` and `Daily_ER_result_spx.csv` which contains daily excess returns.  

