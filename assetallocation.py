import numpy as np
import pandas as pd
from scipy.optimize import minimize 
import matplotlib.pyplot as plt
import yfinance as yf
import pandas_datareader.data as web
import datetime

#Stopping the print from showing up with "np.float64"
np.set_printoptions(legacy='1.25')

#Setting years we wish to follow within the historical data collection
first_year = 2016
final_year = 2026
start = datetime.datetime(first_year, 1, 1)
end = datetime.datetime(final_year, 1, 1)

#Setting the list of tickers which we will follow within the historical data collection
ticker_list = ["AAL.L", "BARC.L", "HSX.L", "MKS.L", "NG.L", "ULVR.L", "VGOV.L", "SGLN.L"]

#Initialisation of the arrays, lists, and the aimed returns utilised within the code
data_array = []
ind_log_returns = []
exp_log_returns = []
log_returns_array = []
weights_equal = []
frontier = []
return_aims = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25]
model_go = False
recorded = False

#Requires input from user as to when to begin the model
while model_go != True:
    print("\nPlease enter 1 if you wish to begin running the model")
    if input() == "1": 
        model_go = True
    else:
        print("\nModel not begun")

#Asks whether the user wants to save the efficient frontier graph
print("\nPlease enter 1 if you wish to save the efficient frontier graph to a file labelled: 'efficient_frontier.png', \notherwise it will not be saved")
if input() == "1":
    print("\nEfficient frontier graph will be saved")
    save_graph = True
else:
    print("\nEfficient frontier graph will not be saved")
    save_graph = False
    
#Asks whether the user wants to allow short selling
print("\nPlease enter 1 if you wish to allow short selling")
if input() == "1":
    print("\nShort selling will be allowed")
    short_input = True
else:
    print("\nShort selling will not be allowed")
    short_input = False

#Asks what maximum weighting the user desires for each individual ticker
while recorded != True:
    print("\nPlease enter your desired maximum absolute weighting for each individual ticker, \nwith this being 1 for uncapped weights and at least greater than 0")
    error = 0
    max_ind_weight = input()

    #Tests for the form of the string and denies if it cannot be a float
    try:
        float(max_ind_weight)
    except ValueError:
        error = 1
    if error == 0 and 1 >= float(max_ind_weight) > 0:
        max_ind_weight = float(max_ind_weight)
        recorded = True
    else:
        print("\nError please try again")

print("\nPlease enter 1 if you wish to use the mean 10 Year Treasury Yields from 2016 to 2026, \notherwise the yield at the start of 2026 will be used")
if input() == "1": 
    average_rates = True
    print("\nMean 10 Year Treasury Yield from 2016 to 2026 will be used")
else:
    average_rates = False
    print("\n10 Year Treasury Yield from the start of 2026 will be used")

#Function which collects the data from yahoo finance based on the given ticker
def data_collection(ticker):
    raw_series = yf.download(ticker, start=start, end=end)['Close'] 
    raw_series.columns = raw_series.columns.get_level_values(0)
    historical_series = raw_series.resample('MS').last().dropna().values.flatten()
    return historical_series

#Function which creates an list of average logged returns for each ticker
def exp_log_return_calc(data):
    for i in range(len(data)-1):
        ind_log_returns.append(np.log(data[i+1] / data[i]))
    ind_exp_log_returns = sum(ind_log_returns) / len(ind_log_returns)
    ind_log_returns.clear()
    return ind_exp_log_returns

#Function which calculates the variance of a portfolio given the weights and covariance function
def portfolio_variance_func(weights, cov):
    return np.dot(np.dot(weights, cov), np.transpose(weights))

#Function which calculates the weights to minimise portfolio variance based on a targeted return and covariance function
def min_variance(cov, exp_returns, target_return, allow_short=short_input):
    error_status = False
    n = len(exp_returns)
    weights = weights_equal

    #Constraints placed on the minimisation
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}, {'type': 'eq', 'fun': lambda w: np.dot(w, exp_returns - target_return)}]

    #Bounds placed on the value of the individual weights 
    if allow_short:
        bounds = [(-max_ind_weight, max_ind_weight) for _ in range(n)]
    else:
        bounds = [(0, max_ind_weight) for _ in range(n)]

    #Minimisation performed based on previous inputs
    result = minimize(portfolio_variance_func, weights, args=(cov,), method='SLSQP', bounds=bounds, constraints=constraints)
    if not result.success:
        print (f"Optimization failed for target: {target_return}")
        error_status = True
    return result.x, error_status

#Function which calculates a negative sharpe ratio for use in a minimisation function
def neg_sharpe_ratio(weights, exp_returns, cov, mean_rates):
    max_return = np.dot(weights, exp_returns)
    max_volatility = np.sqrt(portfolio_variance_func(weights, cov))
    return -(max_return - mean_rates) / max_volatility

#Function which minimises the negative sharpe ratio to calculate the weights that give the maximum sharpe ratio
def max_sharpe(cov, exp_returns, mean_rates, allow_short=short_input):
    n = len(exp_returns)
    weights = weights_equal

    #Constraints placed on the minimisation
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]

    #Bounds placed on the value of the individual weights    
    if allow_short:
        bounds = [(-1, max_ind_weight) for _ in range(n)]
    else:
        bounds = [(0, max_ind_weight) for _ in range(n)]

    #Minimisation performed based on previous inputs
    result = minimize(neg_sharpe_ratio, weights, args=(exp_returns, cov, mean_rates), method='SLSQP', bounds=bounds, constraints=constraints)
    if not result.success:
        print("Optimization failed for max sharpe ratio")
    return result.x

if model_go == True:
    #Iterates over the ticker list to collect the data, append the series to an array, appends the annualised returns to a list, appends the log returns to an array, and creates an equal weight list the length of the ticker list
    for i in ticker_list:
        ticker_data = data_collection(ticker=i)
        data_array.append(ticker_data)
        exp_log_returns.append(exp_log_return_calc(ticker_data) * 12)
        log_returns_array.append(np.log(ticker_data[1:] / ticker_data[:-1]))
        weights_equal.append(1 / len(ticker_list))
    
    #Changing the list into a numpy array for faster calculations
    exp_log_returns = np.array(exp_log_returns)
    
    #Creates the start of current month 10 year treasury yields or the mean 10 year treasury yields from 2016 to 2026 via FRED
    if average_rates == True:
        mean_rates = float((web.DataReader('DGS10', 'fred', start, end) / 100).resample('MS').last().dropna().mean().item())
    else:
        mean_rates = (web.DataReader('DGS10', 'fred', end - pd.Timedelta(days=7), end)/ 100).resample('MS').last().dropna().iloc[-1,0]
    
    #Annualises the covariance from the log returns array
    annual_covariance = np.cov(log_returns_array) * 12
    
    #Calculating the sharpe ratio for the equal weight portfolio
    portfolio_return_equal = sum([i * j for i, j in zip(weights_equal, exp_log_returns)])
    portfolio_variance_equal = np.dot(np.dot(weights_equal, annual_covariance), np.transpose(weights_equal))
    portfolio_volatility_equal = np.sqrt(portfolio_variance_equal)
    sharpe_ratio = (portfolio_return_equal - mean_rates) / portfolio_volatility_equal
    
    #Iterates to calculate the frontier for every target in the returns targets
    for target in return_aims:
        try:
            weight_opt = min_variance(annual_covariance, exp_log_returns, target, allow_short=short_input)[0]
            volatility = np.sqrt(portfolio_variance_func(weight_opt, annual_covariance))
            if min_variance(annual_covariance, exp_log_returns, target, allow_short=short_input)[1] == False:
                frontier.append((target, volatility, weight_opt))
                print(f"Target return {target:.2%} -> volatility {volatility:.4f}, weights {np.round(weight_opt, 3)}")
            else:
                pass
        except ValueError as e:
            print(e)
    
    #Calculation of the max sharpe ratio portfolio
    weights_max_sharpe = max_sharpe(annual_covariance, exp_log_returns, mean_rates, allow_short=short_input)
    return_max_sharpe = np.dot(weights_max_sharpe, exp_log_returns)
    volatility_max_sharpe = np.sqrt(portfolio_variance_func(weights_max_sharpe, annual_covariance))
    sharpe_max = (return_max_sharpe - mean_rates) / volatility_max_sharpe
    
    #Taking the return and volatility from the main frontier array
    frontier_return = [i[0] for i in frontier]
    frontier_volatility = [i[1] for i in frontier]
    
    #Initialising the figure
    fig, ax = plt.subplots(figsize=(9, 6))
    
    #Plotting the efficient frontier 
    ax.plot(frontier_volatility, frontier_return, 'b-o', markersize=4, label='Efficient frontier')
    
    #Plotting the Equal weight portfolio point
    ax.scatter(portfolio_volatility_equal, portfolio_return_equal, color='red', marker='.', s=200,
               label='Equal-weight portfolio', zorder=5)
    
    #Plotting the Max Sharpe ratio portfolio point
    ax.scatter(volatility_max_sharpe, return_max_sharpe, color='green', marker='s', s=140,
               label=f'Max Sharpe = {sharpe_max:.2f}', zorder=5)
    
    #Plotting the labels, title, legend, and grid
    ax.set_xlabel('Volatility (annualised std. dev.)')
    ax.set_ylabel('Expected return (annualised)')
    ax.set_title('Efficient Frontier')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2%}'))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.2%}'))
    ax.legend()
    ax.grid(alpha=0.25)
    
    #Saving of graph if desired
    if save_graph == True:
        fig.savefig("efficient_frontier.png", dpi=150, bbox_inches='tight')
    else:
        pass
    
    #Final displaying of the figure
    plt.tight_layout()
    plt.show()