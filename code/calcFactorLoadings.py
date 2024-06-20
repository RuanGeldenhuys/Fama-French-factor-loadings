import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.api import OLS, add_constant
import statsmodels.api as sm
from pandas.tseries.offsets import MonthEnd

def calcFactorLoadings(df, fund):

    # Pull correct fund's returns
    test_fund = df[df['Fund'] == fund][['Date', 'Fund', 'Returns']]
    test_fund['Date'] = pd.to_datetime(test_fund['Date'])

    # Exit condition 1: The particular fund has no returns data
    if test_fund['Returns'].isna().all():
        return None

    # Join with FAMA-FRENCH factors
    joined_df = pd.merge(test_fund, FF_factors, on='Date', how='left')
    joined_df['ret_min_rf'] = joined_df['Returns'] - joined_df['RF']
    joined_df.dropna(inplace=True)

    # Rolling regression
    def rolling_regression(data, window=36):
        results = []
        for start in range(len(data) - window + 1):
            window_data = data.iloc[start:start + window]
            X = window_data[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']]
            y = window_data['ret_min_rf']
            X = add_constant(X)
            model = OLS(y, X).fit()
            betas = model.params
            std_errors = model.bse
            result = pd.concat([betas, std_errors.rename(lambda x: x + '_se')])
            results.append(result)

        return pd.DataFrame(results)

    fund_name = joined_df['Fund'].iloc[0]

    # Exit condition 2: Not enough time periods to run regression
    if len(joined_df) < 36:
        return None

    start_date = joined_df['Date'].iloc[35]

    # Select columns for the regression (excluding Fund and Date)
    regression_data = joined_df.drop(columns=['Fund', 'Date', 'Returns'])

    # Perform the rolling regression
    regression_results = rolling_regression(regression_data)

    factor_loadings = regression_results.reset_index(drop=True)
    factor_loadings['Fund'] = fund_name

    # Create corresponding date sequence
    start_date = start_date - MonthEnd(1)
    date_seq = pd.date_range(start=start_date, periods=len(factor_loadings), freq='ME') + MonthEnd(1)
    factor_loadings['Date'] = date_seq

    return factor_loadings

# Load data
benchmark_vec = [
    "Benchmark 1: S&P 500 TR USD",
    "Benchmark 2: MSCI EAFE PR USD",
    "Peer Group: Display Group",
    "Number of investments ranked",
    "Median"
]

# Read the main dataframe and filter it
main_df = pd.read_csv("data/main_df.csv")
main_df = main_df.iloc[:, 1:]  # Select all columns except the first one
main_df = main_df[~main_df['Fund'].isin(benchmark_vec)]  # Filter out garbage columns
main_df = main_df[['Date', 'Fund', 'Returns']]

# Read the FF factors dataframe and mutate the Date column
FF_factors = pd.read_excel("data/FF5.xlsx")
FF_factors['Date'] = pd.to_datetime(FF_factors['Date'])

# Get all the funds in the data
funds = main_df['Fund'].unique()

# Apply calcFactorLoadings to all funds in main dataframe
# Store each in a separate element in a list
results_list = [calcFactorLoadings(main_df, name) for name in funds]

# Filter out None values from results_list
results_list = [result for result in results_list if result is not None]

# Combine all dataframes in the list into one big dataframe
factor_loadings = pd.concat(results_list, ignore_index=True)

# Select Date, Fund, and all other columns except the last two (which are likely the index columns)
factor_loadings = factor_loadings[['Date', 'Fund'] + factor_loadings.columns[0:-2].tolist()]

print(factor_loadings.head())