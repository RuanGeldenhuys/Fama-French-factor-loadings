calcFactorLoadings <- function(df, fund){

    #Pull correct fund's returns
    test_fund <- df %>%
        filter(Fund == fund) %>%
        select(Date, Fund, Returns) %>%
        mutate(Date = as.Date(Date))

    # Exit condition 1: The particular fund has no returns data
    if (all(is.na(test_fund$Returns))) {
        return(NULL)
    }

    #Join with FAMA-FRENCH factors
    joined_df <- test_fund %>%
        left_join(FF_factors, by="Date") %>%
        mutate(ret_min_rf = Returns - RF) %>%
        drop_na()

    # Rolling regression
    rolling_regression <- function(data, window = 36) {
        rollapply(data,
                  width = window,
                  FUN = function(x) {
                      model <- lm(ret_min_rf ~ `Mkt-RF` + SMB + HML + RMW + CMA, data = as.data.frame(x))
                      betas <- coefficients(model)
                      std_errors <- coef(summary(model))[, "Std. Error"]
                      names(std_errors) <- paste0(names(std_errors), "_se")
                      data.frame(t(c(betas, std_errors)))

                  },
                  by.column = FALSE,
                  align = 'right')
    }

    fund <- joined_df %>%
        select(Fund) %>%
        slice(1) %>%
        pull(1)

    # Exit condition 2: Not enough time periods to run regression
    if (nrow(joined_df) < 36) {
        return(NULL)
    }

    start_date <- joined_df %>%
        select(Date) %>%
        slice(36) %>%
        pull(1)

    # Select columns for the regression (excluding Fund and Date)
    regression_data <- joined_df %>%
        select(-Fund, -Date, -Returns)

    # Perform the rolling regression
    regression_results <- rolling_regression(regression_data)

    factor_loadings <- as.data.frame(regression_results) %>%
        mutate(Fund = fund)

    # Create corresponding date sequence
    start_date <- floor_date(start_date, "months")
    date_seq <- seq.Date(from = start_date, by = "month", length.out = nrow(factor_loadings))
    date_seq <- date_seq + months(1) - days(1)

    factor_loadings <- factor_loadings %>%
        mutate(Date = date_seq)

    return(factor_loadings)

}
