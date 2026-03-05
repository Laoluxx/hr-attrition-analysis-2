import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "ibm_hr.csv")
    return pd.read_csv(file_path)


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


def kpi_report(df):
    total = len(df)
    left = (df["Attrition"] == "Yes").sum()
    stayed = (df["Attrition"] == "No").sum()

    attrition_rate = (left / total) * 100
    avg_age_left = df[df["Attrition"] == "Yes"]["Age"].mean()
    avg_income_left = df[df["Attrition"] == "Yes"]["MonthlyIncome"].mean()

    print("\n--- HR ATTRITION REPORT ---")
    print(f"Total Employees: {total}")
    print(f"Stayed: {stayed}")
    print(f"Left: {left}")
    print(f"Attrition Rate: {attrition_rate:.2f}%")
    print(f"Average Age (Left): {avg_age_left:.2f}")
    print(f"Average Monthly Income (Left): {avg_income_left:.2f}")


def pivot_tables(df, outputs_dir):

    dept_attrition = (
        df.groupby("Department")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
        .sort_values(by="AttritionRate", ascending=False)
    )

    role_attrition = (
        df.groupby("JobRole")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
        .sort_values(by="AttritionRate", ascending=False)
    )

    overtime_attrition = (
        df.groupby("OverTime")["Attrition"]
        .apply(lambda x: (x == "Yes").mean() * 100)
        .reset_index(name="AttritionRate")
    )

    dept_attrition.to_csv(os.path.join(outputs_dir, "attrition_by_department.csv"), index=False)
    role_attrition.to_csv(os.path.join(outputs_dir, "attrition_by_jobrole.csv"), index=False)
    overtime_attrition.to_csv(os.path.join(outputs_dir, "attrition_by_overtime.csv"), index=False)


def save_plot(path):
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def visualizations(df, charts_dir):

    sns.set(style="whitegrid")

    plt.figure()
    sns.countplot(data=df, x="Attrition")
    plt.title("Employee Attrition Count")
    save_plot(os.path.join(charts_dir, "attrition_count.png"))

    plt.figure()
    sns.countplot(data=df, x="Department", hue="Attrition")
    plt.xticks(rotation=45)
    plt.title("Attrition by Department")
    save_plot(os.path.join(charts_dir, "attrition_by_department.png"))

    plt.figure()
    sns.boxplot(data=df, x="Attrition", y="MonthlyIncome")
    plt.title("Income vs Attrition")
    save_plot(os.path.join(charts_dir, "income_vs_attrition.png"))

    plt.figure()
    sns.boxplot(data=df, x="Attrition", y="Age")
    plt.title("Age Distribution by Attrition")
    save_plot(os.path.join(charts_dir, "age_vs_attrition.png"))


def main():

    charts_dir, outputs_dir = ensure_folders()

    df = load_data()

    basic_overview(df)

    kpi_report(df)

    pivot_tables(df, outputs_dir)

    visualizations(df, charts_dir)


if __name__ == "__main__":
    main()