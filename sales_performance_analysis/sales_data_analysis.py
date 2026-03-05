import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "superstore.csv")
    return pd.read_csv(file_path, encoding="latin1")


def ensure_folders():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(script_dir, "charts")
    outputs_dir = os.path.join(script_dir, "outputs")

    os.makedirs(charts_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    return charts_dir, outputs_dir


def basic_overview(df):
    print("\n--- DATA OVERVIEW ---")
    print("Shape:", df.shape)
    print("\nColumns:")
    print(df.columns)
    print("\nFirst rows:")
    print(df.head())


def sales_kpis(df):

    total_sales = df["SALES"].sum()
    total_orders = df["ORDERNUMBER"].nunique()
    total_customers = df["CUSTOMERNAME"].nunique()

    avg_order_value = total_sales / total_orders

    print("\n--- SALES KPI REPORT ---")
    print(f"Total Revenue: ${round(total_sales,2)}")
    print(f"Total Orders: {total_orders}")
    print(f"Total Customers: {total_customers}")
    print(f"Average Order Value: ${round(avg_order_value,2)}")


def sales_by_country(df, outputs_dir):

    country_sales = df.groupby("COUNTRY")["SALES"].sum().sort_values(ascending=False)

    country_sales.to_csv(os.path.join(outputs_dir,"sales_by_country.csv"))

    print("\nSales by Country:")
    print(country_sales)


def top_products(df, outputs_dir):

    top_products = df.groupby("PRODUCTLINE")["SALES"].sum().sort_values(ascending=False)

    top_products.to_csv(os.path.join(outputs_dir,"sales_by_productline.csv"))

    print("\nSales by Product Line:")
    print(top_products)


def monthly_sales(df, outputs_dir):

    df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"])

    df["Month"] = df["ORDERDATE"].dt.to_period("M")

    monthly_sales = df.groupby("Month")["SALES"].sum()

    monthly_sales.to_csv(os.path.join(outputs_dir,"monthly_sales.csv"))

    print("\nMonthly Sales:")
    print(monthly_sales.head())


def save_plot(path):
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def visualizations(df, charts_dir):

    sns.set(style="whitegrid")

    plt.figure()
    sns.barplot(data=df, x="PRODUCTLINE", y="SALES")
    plt.xticks(rotation=45)
    plt.title("Sales by Product Line")
    save_plot(os.path.join(charts_dir,"sales_by_productline.png"))

    plt.figure()
    sns.boxplot(data=df, x="DEALSIZE", y="SALES")
    plt.title("Sales Distribution by Deal Size")
    save_plot(os.path.join(charts_dir,"sales_by_dealsize.png"))

    plt.figure()
    sns.scatterplot(data=df, x="QUANTITYORDERED", y="SALES")
    plt.title("Quantity vs Sales")
    save_plot(os.path.join(charts_dir,"quantity_vs_sales.png"))


def main():

    charts_dir, outputs_dir = ensure_folders()

    df = load_data()

    basic_overview(df)

    sales_kpis(df)

    sales_by_country(df, outputs_dir)

    top_products(df, outputs_dir)

    monthly_sales(df, outputs_dir)

    visualizations(df, charts_dir)


if __name__ == "__main__":
    main()