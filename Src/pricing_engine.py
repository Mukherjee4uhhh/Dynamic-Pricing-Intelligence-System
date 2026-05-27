import pandas as pd
import numpy as np


# =========================================================
# BUILD FINAL PRICING RECOMMENDATIONS
# =========================================================

def build_recommendations(
    elasticity_df: pd.DataFrame,
    competitor_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Combine elasticity analysis +
    competitor benchmarking
    to generate final pricing recommendations.
    """

    # -----------------------------------------------------
    # MERGE DATASETS
    # -----------------------------------------------------

    df = competitor_df.merge(

        elasticity_df[
            [
                'StockCode',
                'Elasticity',
                'Elasticity_Category',
                'Recommended_Price_Change'
            ]
        ],

        on='StockCode',

        how='left'
    )

    # -----------------------------------------------------
    # FILL MISSING ELASTICITY
    # -----------------------------------------------------

    # Use fallback elasticity
    # when insufficient statistical data exists

    df['Elasticity'] = (
        df['Elasticity']
        .fillna(-1.0)
    )

    # -----------------------------------------------------
    # FINAL RECOMMENDATION ENGINE
    # -----------------------------------------------------

    def final_recommendation(row):

        e = row['Elasticity']

        flag = row['Pricing_Flag']

        # ---------------------------------------------
        # INELASTIC PRODUCTS
        # ---------------------------------------------

        if e > -0.5 and 'Underpriced' in flag:

            return 'RAISE PRICE +10% to +15%'

        elif e > -0.5 and 'Competitive' in flag:

            return 'RAISE PRICE +5% to +8%'

        elif e > -0.5 and 'Overpriced' in flag:

            return 'HOLD — Inelastic Demand Protects'

        # ---------------------------------------------
        # MODERATELY ELASTIC
        # ---------------------------------------------

        elif -1.0 < e <= -0.5 and 'Underpriced' in flag:

            return 'TEST +3% Increase'

        elif -1.0 < e <= -0.5 and 'Overpriced' in flag:

            return 'REDUCE -5%'

        # ---------------------------------------------
        # HIGHLY ELASTIC
        # ---------------------------------------------

        elif e <= -1.0 and 'Overpriced' in flag:

            return 'REDUCE PRICE -8% to -12%'

        elif e <= -1.0 and 'Underpriced' in flag:

            return 'HOLD — Elastic, Raising Will Hurt'

        # ---------------------------------------------
        # DEFAULT
        # ---------------------------------------------

        else:

            return 'MONITOR — No Clear Signal'

    # Apply logic

    df['Final_Recommendation'] = (
        df.apply(final_recommendation, axis=1)
    )

    # -----------------------------------------------------
    # PRICE CHANGE FACTORS
    # -----------------------------------------------------

    change_map = {

        'RAISE PRICE +10% to +15%': 0.125,

        'RAISE PRICE +5% to +8%': 0.065,

        'HOLD — Inelastic Demand Protects': 0.0,

        'TEST +3% Increase': 0.03,

        'REDUCE -5%': -0.05,

        'REDUCE PRICE -8% to -12%': -0.10,

        'HOLD — Elastic, Raising Will Hurt': 0.0,

        'MONITOR — No Clear Signal': 0.0
    }

    df['Price_Change_Factor'] = (

        df['Final_Recommendation']

        .map(change_map)

        .fillna(0)

    )

    # -----------------------------------------------------
    # RECOMMENDED PRICE
    # -----------------------------------------------------

    df['Recommended_Price'] = (

        df['Avg_Price']

        * (

            1

            + df['Price_Change_Factor']

        )

    ).round(2)

    # -----------------------------------------------------
    # PRICE DIFFERENCE
    # -----------------------------------------------------

    df['Price_Difference'] = (

        df['Recommended_Price']

        - df['Avg_Price']

    ).round(2)

    return df


# =========================================================
# REVENUE UPLIFT ANALYSIS
# =========================================================

def calculate_revenue_uplift(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Estimate revenue uplift
    after pricing recommendations.
    """

    result = df.copy()

    # -----------------------------------------------------
    # PRICE CHANGE %
    # -----------------------------------------------------

    result['Pct_Price_Change'] = (

        result['Price_Change_Factor']

        * 100

    )

    # -----------------------------------------------------
    # ESTIMATED QUANTITY CHANGE
    # -----------------------------------------------------

    # %ΔQ = Elasticity × %ΔP

    result['Estimated_Qty_Change_Pct'] = (

        result['Elasticity']

        * result['Pct_Price_Change']

    )

    # -----------------------------------------------------
    # ESTIMATED NEW QUANTITY
    # -----------------------------------------------------

    result['Estimated_New_Qty'] = (

        result['Total_Quantity']

        * (

            1

            + result['Estimated_Qty_Change_Pct'] / 100

        )

    ).clip(lower=0)

    # -----------------------------------------------------
    # CURRENT REVENUE
    # -----------------------------------------------------

    result['Current_Revenue'] = (

        result['Avg_Price']

        * result['Total_Quantity']

    )

    # -----------------------------------------------------
    # PROJECTED REVENUE
    # -----------------------------------------------------

    result['Projected_Revenue'] = (

        result['Recommended_Price']

        * result['Estimated_New_Qty']

    )

    # -----------------------------------------------------
    # REVENUE UPLIFT
    # -----------------------------------------------------

    result['Revenue_Uplift'] = (

        result['Projected_Revenue']

        - result['Current_Revenue']

    ).round(2)

    # -----------------------------------------------------
    # SUMMARY METRICS
    # -----------------------------------------------------

    total_uplift = (
        result['Revenue_Uplift'].sum()
    )

    positive_uplift = (

        result[
            result['Revenue_Uplift'] > 0
        ]['Revenue_Uplift']

        .sum()

    )

    positive_skus = len(

        result[
            result['Revenue_Uplift'] > 0
        ]

    )

    # -----------------------------------------------------
    # PRINT SUMMARY
    # -----------------------------------------------------

    print("\n" + "=" * 60)

    print("REVENUE IMPACT SUMMARY")

    print("=" * 60)

    print(
        f"Total projected uplift: "
        f"£{total_uplift:,.0f}"
    )

    print(
        f"Positive opportunities: "
        f"£{positive_uplift:,.0f}"
    )

    print(
        f"SKUs with positive uplift: "
        f"{positive_skus}"
    )

    print("=" * 60)

    return result


# =========================================================
# MAIN EXECUTION
# =========================================================

if __name__ == "__main__":

    from data_loader import (
        load_data,
        get_sku_summary
    )

    from price_elasticity import (
        run_elasticity_analysis
    )

    from competitor_benchmarking import (
        run_competitor_analysis
    )

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    print("Loading dataset...")

    filepath = (
        r"E:\Dynamic-pricing-intelligence\Data\data.xlsx"
    )

    df = load_data(filepath)

    sku_summary = get_sku_summary(df)

    # -----------------------------------------------------
    # RUN MODULES
    # -----------------------------------------------------

    elasticity_df = (
        run_elasticity_analysis(df)
    )

    competitor_df = (
        run_competitor_analysis(sku_summary)
    )

    # -----------------------------------------------------
    # BUILD RECOMMENDATIONS
    # -----------------------------------------------------

    recommendations = build_recommendations(

        elasticity_df,

        competitor_df

    )

    # -----------------------------------------------------
    # REVENUE UPLIFT
    # -----------------------------------------------------

    final = calculate_revenue_uplift(
        recommendations
    )

    # -----------------------------------------------------
    # SAVE OUTPUT
    # -----------------------------------------------------

    output_path = (
        'outputs/pricing_recommendations_v3.csv'
    )

    final.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nRecommendations saved to:\n"
        f"{output_path}"
    )

    # -----------------------------------------------------
    # DISPLAY SAMPLE
    # -----------------------------------------------------

    print("\nSample Recommendations:\n")

    cols = [

        'StockCode',

        'Description',

        'Avg_Price',

        'Recommended_Price',

        'Final_Recommendation',

        'Revenue_Uplift'
    ]

    print(

        final[cols]

        .head(15)

        .to_string()

    )