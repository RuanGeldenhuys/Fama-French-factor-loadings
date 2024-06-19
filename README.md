# Purpose

Here is a function and supplementary code I wrote to calculate
Fama-French 5 Factor loadings on multiple funds simultaneously. These
factor loadings are often used within financial modelling, but their
creation (however simple) is not well documented in code. The function
itself is stored [here](../code/calcFactorLoadings.R) , while the README
serves as a usage guide.

# Data

In this example I work with US data. The actual Fama-French factors for
the US is freely available
[here](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html).
Two dataframes are required for the calculation that will follow. The
Fama-French factors and the historical returns of funds that you wish to
calculate loadings for. Where you get fund returns is up to you. The
data loading can be seen below.

``` r
# Load data
benchmark_vec <- c("Benchmark 1: S&P 500 TR USD",
                      "Benchmark 2: MSCI EAFE PR USD",
                      "Peer Group: Display Group",
                      "Number of investments ranked",
                      "Median")

main_df <- read.csv("data/main_df.csv") %>%
    select(-1) %>% 
    filter(!Fund %in% benchmark_vec) %>% #Filter out garbage columns
    select(Date, Fund, Returns)

FF_factors <- read_excel("data/FF5.xlsx") %>%
    mutate(Date = as.Date(Date))

kable(head(main_df), caption = "Fund Returns")
```

| Date       | Fund                                     |  Returns |
|:-----------|:-----------------------------------------|---------:|
| 2014-05-31 | 1618 Investment Actions Amérique du Nord |       NA |
| 2014-05-31 | 1741 Equity Systematic US Fund           | 1.995798 |
| 2014-05-31 | AAF-FoM North American Eqs A$            | 1.766953 |
| 2014-05-31 | AAM Selection US Equities D              |       NA |
| 2014-05-31 | AB Concentrated US Eq S1 USD             | 1.408451 |
| 2014-05-31 | AB Security of the Future WNN USD        |       NA |

Fund Returns

``` r
kable(head(FF_factors), caption = "FF5 factors")
```

| Date       | Mkt-RF |   SMB |   HML |   RMW |   CMA |  RF |
|:-----------|-------:|------:|------:|------:|------:|----:|
| 2014-05-31 |   2.06 | -1.89 | -0.13 |  0.05 | -1.00 |   0 |
| 2014-06-30 |   2.61 |  3.11 | -0.70 | -1.89 | -2.00 |   0 |
| 2014-07-31 |  -2.04 | -4.29 |  0.03 |  0.89 |  0.52 |   0 |
| 2014-08-31 |   4.24 |  0.31 | -0.45 | -0.64 | -0.70 |   0 |
| 2014-09-30 |  -1.97 | -3.72 | -1.34 |  1.30 | -0.51 |   0 |
| 2014-10-31 |   2.52 |  3.73 | -1.81 | -0.57 | -0.11 |   0 |

FF5 factors

As can be seen above, fund returns (`main_df`) should be in long format.
It requires three columns, namely Date, Fund, Returns. It can have
additional columns, since the function will deal with this
automatically. The factors (`FF_factors`), require a Date column in the
same format as the fund_returns, and then a column for each factor in
the analysis. **Note:** The column names are hard-coded into the
function. If you have a different naming convention / different factors,
you will have to alter them in the function itself.

# How are factor loadings calculated

Factor loadings are calculated based on a 36-month rolling regression
given by the equation:

*R*<sub>*i**t*</sub> − *R*<sub>*f**t*</sub> = *α*<sub>*i*</sub> + *β*<sub>*i**M*</sub>(*R*<sub>*M**t*</sub>−*R*<sub>*f**t*</sub>) + *β*<sub>*i**S**M**B*</sub>SMB<sub>*t*</sub> + *β*<sub>*i**H**M**L*</sub>HML<sub>*t*</sub> + *β*<sub>*i**R**M**W*</sub>RMW<sub>*t*</sub> + *β*<sub>*i**C**M**A*</sub>CMA<sub>*t*</sub> + *ϵ*<sub>*i**t*</sub>
where: - *R*<sub>*i**t*</sub> is the return of the portfolio or asset
*i* at time *t*, - *R*<sub>*f**t*</sub> is the risk-free rate at time
*t*, - *R*<sub>*M**t*</sub> is the return of the market portfolio at
time *t*, - *α*<sub>*i*</sub> is the intercept (alpha) for asset *i*, -
*β*<sub>*i**M*</sub> is the sensitivity of the asset’s returns to the
market risk premium (market beta), - *β*<sub>*i**S**M**B*</sub> is the
sensitivity of the asset’s returns to the size factor (Small Minus
Big), - *β*<sub>*i**H**M**L*</sub> is the sensitivity of the asset’s
returns to the value factor (High Minus Low), -
*β*<sub>*i**R**M**W*</sub> is the sensitivity of the asset’s returns to
the profitability factor (Robust Minus Weak), -
*β*<sub>*i**C**M**A*</sub> is the sensitivity of the asset’s returns to
the investment factor (Conservative Minus Aggressive), -
*ϵ*<sub>*i**t*</sub> is the error term for asset *i* at time *t*.

# Running the function

``` r
funds <- unique(main_df$Fund)

# Apply calcFactorLoadings to all funds in main dataframe
# Store each in a seperate element in a list
results_list <- lapply(funds, function(name) {
    calcFactorLoadings(main_df, name)
})
```

``` r
# Combine all dataframes in the list into one big dataframe
factor_loadings <- do.call(rbind, results_list) %>% 
    select(Date, Fund, c(1:(ncol(.)-2)))
```
