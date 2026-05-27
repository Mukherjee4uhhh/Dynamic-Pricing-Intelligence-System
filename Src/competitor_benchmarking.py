import pandas as pd
import numpy as np


# ---------------------------------------------------
# SIMULATE COMPETITOR PRICES
# ---------------------------------------------------

def simulate_competitor_prices(
    sku_df: pd.DataFrame,
    seed: int = 42
) -> pd.DataFrame:
    """
    Simulate competitor pricing.

    Competitor A:
    aggressive discount player

    Competitor B:
    market average

    Competitor C:
    premium pricing player
    """

    np.random.seed(seed)

    n = len(sku_df)

    df = sku_df.copy()

    # -----------------------------------------
    # COMPETITOR PRICES
    # -----------------------------------------

    df['Competitor_A_Price'] = (
        df['Avg_Price']
        * np.random.uniform(0.85, 0.95, n)
    )

    df['Competitor_B_Price'] = (
        df['Avg_Price']
        * np.random.uniform(0.92, 1.08, n)
    )

    df['Competitor_C_Price'] = (
        df['Avg_Price']
        * np.random.uniform(1.05, 1.20, n)
    )

    # -----------------------------------------
    # ROUNDING
    # -----------------------------------------

    price_cols = [

        'Competitor_A_Price',

        'Competitor_B_Price',

        'Competitor_C_Price'
    ]

    for col in price_cols:

        df[col] = df[col].round(2)

    # -----------------------------------------
    # MARKET AVERAGE PRICE
    # -----------------------------------------

    df['Market_Avg_Price'] = (
        df[
            [
                'Competitor_A_Price',
                'Competitor_B_Price',
                'Competitor_C_Price'
            ]
        ]
        .mean(axis=1)
        .round(2)
    )

    # -----------------------------------------
    # OUR PRICE VS MARKET
    # -----------------------------------------

    df['Price_vs_Market_Pct'] = (

        (
            df['Avg_Price']
            - df['Market_Avg_Price']
        )

        / df['Market_Avg_Price']

        * 100

    ).round(1)

    return df


# ---------------------------------------------------
# FLAG PRICING RISKS
# ---------------------------------------------------

def flag_pricing_risks(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Flag pricing risks
    versus competitor market.
    """

    def flag(pct):

        if pct > 15:
            return (
                ' Overpriced — Customer Loss Risk'
            )

        elif pct < -10:
            return (
                ' Underpriced — Revenue Leakage'
            )

        else:
            return (
                ' Competitive — Monitor'
            )

    df['Pricing_Flag'] = (
        df['Price_vs_Market_Pct']
        .apply(flag)
    )

    return df


# ---------------------------------------------------
# RUN FULL COMPETITOR ANALYSIS
# ---------------------------------------------------

def run_competitor_analysis(
    sku_summary: pd.DataFrame
) -> pd.DataFrame:
    """
    Full competitor benchmarking pipeline.
    """

    print(
        "Running competitor benchmarking..."
    )

    # -----------------------------------------
    # SIMULATE COMPETITOR DATA
    # -----------------------------------------

    df = simulate_competitor_prices(
        sku_summary
    )

    # -----------------------------------------
    # FLAG RISKS
    # -----------------------------------------

    df = flag_pricing_risks(df)

    # -----------------------------------------
    # SUMMARY
    # -----------------------------------------

    print("\nPricing Risk Summary:\n")

    print(
        df['Pricing_Flag']
        .value_counts()
    )

    overpriced = df[
        df['Pricing_Flag']
        .str.contains('Overpriced')
    ]

    underpriced = df[
        df['Pricing_Flag']
        .str.contains('Underpriced')
    ]

    print(
        f"\n⚠️ {len(overpriced)} "
        f"SKUs are overpriced"
    )

    print(
        f"💰 {len(underpriced)} "
        f"SKUs are underpriced"
    )

    return df


# ---------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------

if __name__ == "__main__":

    from data_loader import (
        load_data,
        get_sku_summary
    )

    print("Loading dataset...")

    df = load_data(
        r"E:\Dynamic-pricing-intelligence\Data\data.xlsx"
    )

    sku_summary = get_sku_summary(df)

    result = run_competitor_analysis(
        sku_summary
    )

    # -----------------------------------------
    # DISPLAY SAMPLE
    # -----------------------------------------

    print(
        "\nTop Benchmarking Results:\n"
    )

    print(

        result[
            [
                'StockCode',
                'Description',
                'Avg_Price',
                'Market_Avg_Price',
                'Price_vs_Market_Pct',
                'Pricing_Flag'
            ]
        ]

        .head(20)

    )

    # -----------------------------------------
    # SAVE RESULTS
    # -----------------------------------------

    result.to_csv(
    'outputs/competitor_benchmarking_v2.csv',
    index=False
    )

    print(
    "\nBenchmarking results saved successfully!"
    )

    print(
        "\nCompetitor benchmarking "
        "saved to outputs/"
    )