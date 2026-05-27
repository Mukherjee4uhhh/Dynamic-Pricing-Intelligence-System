import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


# ---------------------------------------------------
# MONTHLY AGGREGATION
# ---------------------------------------------------

def calculate_monthly_aggregates(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Aggregate price and quantity
    at SKU-Month level.
    """

    monthly = (
        df.groupby(
            ['StockCode', 'Description', 'Month']
        )
        .agg(
            Avg_Price=('Price', 'mean'),
            Total_Quantity=('Quantity', 'sum'),
            Revenue=('Revenue', 'sum')
        )
        .reset_index()
    )

    return monthly


# ---------------------------------------------------
# ELASTICITY CALCULATION
# ---------------------------------------------------

def calculate_elasticity(
    sku_data: pd.DataFrame
) -> float:
    """
    Calculate price elasticity
    using log-log regression.

    log(Q) = α + β log(P)

    β = elasticity
    """

    # Need enough observations
    if len(sku_data) < 6:
        return np.nan

    try:

        # -----------------------------------------
        # REMOVE OUTLIERS USING IQR
        # -----------------------------------------

        Q1 = sku_data['Avg_Price'].quantile(0.25)

        Q3 = sku_data['Avg_Price'].quantile(0.75)

        IQR = Q3 - Q1

        sku_data = sku_data[
            (
                sku_data['Avg_Price']
                >= Q1 - 1.5 * IQR
            )
            &
            (
                sku_data['Avg_Price']
                <= Q3 + 1.5 * IQR
            )
        ]

        # Need enough rows after filtering
        if len(sku_data) < 6:
            return np.nan

        # -----------------------------------------
        # LOG TRANSFORMATION
        # -----------------------------------------

        log_price = np.log(
            sku_data['Avg_Price']
        )

        log_quantity = np.log(
            sku_data['Total_Quantity']
        )

        # -----------------------------------------
        # LINEAR REGRESSION
        # -----------------------------------------

        slope, intercept, r_value, p_value, std_err = (
            stats.linregress(
                log_price,
                log_quantity
            )
        )

        # Return only significant results
        if p_value < 0.10:
            return round(slope, 3)

        return np.nan

    except Exception:
        return np.nan


# ---------------------------------------------------
# RUN ELASTICITY ANALYSIS
# ---------------------------------------------------

def run_elasticity_analysis(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Run elasticity analysis
    across all SKUs.
    """

    print(
        "Calculating price elasticity..."
    )

    monthly = calculate_monthly_aggregates(df)

    results = []

    for stock_code in monthly['StockCode'].unique():

        sku_data = monthly[
            monthly['StockCode']
            == stock_code
        ].copy()

        elasticity = calculate_elasticity(
            sku_data
        )

        avg_price = (
            sku_data['Avg_Price'].mean()
        )

        avg_qty = (
            sku_data['Total_Quantity'].mean()
        )

        description = (
            sku_data['Description']
            .iloc[0]
        )

        results.append({

            'StockCode': stock_code,

            'Description': description,

            'Avg_Price': round(avg_price, 2),

            'Avg_Monthly_Qty': round(avg_qty, 0),

            'Elasticity': elasticity

        })

    # -----------------------------------------
    # CREATE RESULTS DATAFRAME
    # -----------------------------------------

    results_df = pd.DataFrame(results)

    results_df = results_df.dropna(
        subset=['Elasticity']
    )

    # Remove unrealistic elasticity
    results_df = results_df[
        results_df['Elasticity'].between(-10, 2)
    ]

    # -----------------------------------------
    # CLASSIFICATION
    # -----------------------------------------

    def classify(e):

        if e > -0.5:
            return (
                'Price Insensitive — Raise Price'
            )

        elif -0.5 >= e > -1.0:
            return (
                'Moderately Sensitive — Test Small Increase'
            )

        elif -1.0 >= e > -1.5:
            return (
                'Elastic — Maintain Price'
            )

        else:
            return (
                'Highly Elastic — Consider Discount'
            )

    results_df[
        'Elasticity_Category'
    ] = results_df[
        'Elasticity'
    ].apply(classify)

    # -----------------------------------------
    # PRICE RECOMMENDATION
    # -----------------------------------------

    def recommend_change(e):

        if e > -0.5:
            return '+10%'

        elif -0.5 >= e > -1.0:
            return '+5%'

        elif -1.0 >= e > -1.5:
            return '0%'

        else:
            return '-5%'

    results_df[
        'Recommended_Price_Change'
    ] = results_df[
        'Elasticity'
    ].apply(recommend_change)

    print(
        f"\nElasticity analysis complete for "
        f"{len(results_df)} SKUs"
    )

    print(
        "\nDistribution of product categories:"
    )

    print(
        results_df[
            'Elasticity_Category'
        ].value_counts()
    )

    return results_df.sort_values(
        'Elasticity',
        ascending=False
    )


# ---------------------------------------------------
# VISUALIZATION
# ---------------------------------------------------

def plot_elasticity_distribution(
    results_df: pd.DataFrame
):
    """
    Visualize elasticity distribution.
    """

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(14, 5)
    )

    # -----------------------------------------
    # HISTOGRAM
    # -----------------------------------------

    axes[0].hist(
        results_df['Elasticity'],
        bins=30,
        color='#2563EB',
        edgecolor='white',
        alpha=0.8
    )

    axes[0].axvline(
        x=-1,
        color='red',
        linestyle='--',
        label='Elasticity = -1'
    )

    axes[0].set_title(
        'Price Elasticity Distribution'
    )

    axes[0].set_xlabel(
        'Elasticity'
    )

    axes[0].set_ylabel(
        'Number of SKUs'
    )

    axes[0].legend()

    # -----------------------------------------
    # CATEGORY BREAKDOWN
    # -----------------------------------------

    category_counts = (
        results_df[
            'Elasticity_Category'
        ]
        .value_counts()
    )

    colors = [
        '#16a34a',
        '#2563eb',
        '#f59e0b',
        '#dc2626'
    ]

    axes[1].barh(
        category_counts.index,
        category_counts.values,
        color=colors[:len(category_counts)]
    )

    axes[1].set_title(
        'SKUs by Pricing Opportunity'
    )

    axes[1].set_xlabel(
        'Number of SKUs'
    )

    plt.tight_layout()

    plt.savefig(
        'outputs/elasticity_distribution.png',
        dpi=150,
        bbox_inches='tight'
    )

    #plt.show()

    plt.close()

    print(
        "Chart saved to outputs/"
    )


# ---------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------

if __name__ == "__main__":

    print("Loading dataset...")

    # Load dataset
    df = pd.read_excel(
        r"E:\Dynamic-pricing-intelligence\Data\data.xlsx"
    )

    # -----------------------------------------
    # CLEANING
    # -----------------------------------------

    df = df[
        ~df['Invoice']
        .astype(str)
        .str.startswith('C')
    ]

    df = df.dropna(
        subset=['Customer ID']
    )

    df = df[df['Price'] > 0]

    df = df[df['Quantity'] > 0]

    # -----------------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------------

    df['Revenue'] = (
        df['Price'] * df['Quantity']
    )

    df['InvoiceDate'] = pd.to_datetime(
        df['InvoiceDate']
    )

    df['Month'] = (
        df['InvoiceDate']
        .dt
        .to_period('M')
    )

    print(
        f"Clean data shape: {df.shape}"
    )

    # -----------------------------------------
    # RUN ANALYSIS
    # -----------------------------------------

    results = run_elasticity_analysis(df)

    # -----------------------------------------
    # PLOTS
    # -----------------------------------------

    plot_elasticity_distribution(results)

    # -----------------------------------------
    # OUTPUT
    # -----------------------------------------

    print(
        "\nTop 10 Price Insensitive SKUs:\n"
    )

    print(
        results[
            results[
                'Recommended_Price_Change'
            ] == '+10%'
        ].head(10)
    )

    # -----------------------------------------
    # SAVE RESULTS
    # -----------------------------------------

    results.to_csv(
        'outputs/elasticity_results.csv',
        index=False
    )

    print(
        "\nResults saved to outputs/"
    )
    # -----------------------------------------
    # SAVE RESULTS
    # -----------------------------------------

    output_path = (
        r"E:\Dynamic-pricing-intelligence\outputs\elasticity_results.csv"
    )

    results.to_csv(
    'outputs/elasticity_results.csv',
    index=False
    )

    print(
        f"\nResults saved to:\n{output_path}"
    )
