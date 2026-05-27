import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:

    print("Loading dataset...")

    df = pd.read_excel(filepath)

    # -----------------------------------
    # CLEANING
    # -----------------------------------

    df = df[~df['Invoice'].astype(str).str.startswith('C')]

    df = df.dropna(subset=['Customer ID'])

    df = df[df['Price'] > 0]

    df = df[df['Quantity'] > 0]

    # -----------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------

    df['Revenue'] = (
        df['Price'] * df['Quantity']
    )

    df['InvoiceDate'] = pd.to_datetime(
        df['InvoiceDate']
    )

    df['Month'] = (
        df['InvoiceDate'].dt.to_period('M')
    )

    df['Week'] = (
        df['InvoiceDate']
        .dt.isocalendar()
        .week
    )

    df['Year'] = (
        df['InvoiceDate'].dt.year
    )

    print(
        f"Clean data shape: {df.shape}"
    )

    return df


def get_sku_summary(
    df: pd.DataFrame
) -> pd.DataFrame:

    sku_df = (

        df.groupby('StockCode')

        .agg(
            Description=('Description', 'first'),
            Avg_Price=('Price', 'mean'),
            Total_Quantity=('Quantity', 'sum'),
            Total_Revenue=('Revenue', 'sum'),
            Transaction_Count=('Invoice', 'nunique')
        )

        .reset_index()

    )

    return sku_df.sort_values(
        'Total_Revenue',
        ascending=False
    )


# ------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------

if __name__ == "__main__":

    filepath = (
        r"E:\Dynamic-pricing-intelligence\Data\data.xlsx"
    )

    df = load_data(filepath)

    sku_summary = get_sku_summary(df)

    print("\nTop 10 SKUs by Revenue:\n")

    print(sku_summary.head(10))