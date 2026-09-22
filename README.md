This model uses Markowitz's Modern Portfolio Theory to find the efficient frontier allocation of eight assets from different sectors. 
Included in this repository is both the Excel and Python file involved within this model, as well as a png of a sample result: "efficient_frontier.png".
This sample result is built in the Python file, with no short selling allowed, a maximum absolute weighting per asset of 0.4 and the mean 10 Year Treasury Yields from 2016 to 2026 used as the risk-free rate.

Python Process:
For the Python process firstly the user is asked whether they want to begin the model, whether they wish to save the graph, whether they want to allow short selling, what their desired maximum absolute weighting for each individual asset is, and how they want to calculate the risk-free rate. The risk-free rate is either calculated by the mean 10 Year Treasury Yields from 2016 to 2026 or the 10 Year Treasury Yield at the start of 2026. 

Then the historical series data is downloaded from Yahoo finance for the period of 2016 to 2026 for the eight assets, and the logged returns of the series data are calculated, with these being used to generate the expected annualised returns per asset and the annual covariance matrix. 

The equal weighted portfolio is then constructed, with the returns, variance, volatility, and Sharpe ratio being found. Following this, the efficient frontier is calculated by using different weightings to minimise the variance of the portfolio for a given target return, and then recording the volatility and weight matrix of this result. The maximal Sharpe ratio portfolio is also found and recorded.

The expected returns and volatility results were then plotted on a scatter graph, alongside the equal-weight and max Sharpe portfolio, with the expected returns covered by the graph depending on whether optimal point were found within the parameters inputted.

Excel Process:
The Excel process involved assembling the database of historical data for these eight assets over the past ten years from Yahoo finance, annualising the expected returns of each asset, and creating their expected covariance matrix.

Following this, Excel's solver was used to maximise the Sharpe ratio for a portfolio around these ten assets, with the solver changing the weightings of the assets within the portfolio. The solver was then used to minimise the portfolio variance for a set of different expected returns, recording the portfolio volatility for each.

The expected returns and volatility were then plotted on a scatter graph alongside the point that maximised the Sharpe ratio and the capital allocation line going through the risk free rate on the y-axis and the maximal Sharpe ratio point. 
