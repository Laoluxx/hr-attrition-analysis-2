import os
import pandas as pd

print("Working folder:", os.getcwd())
print("Files here:", os.listdir())

df = pd.read_csv("ibm_hr.csv.csv")
print(df.head())
print("Shape:", df.shape)
import pandas as pd

df = pd.read_csv("ibm_hr.csv.csv")

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nInfo:")
print(df.info())
print("\nAttrition counts:")
print(df["Attrition"].value_counts())
employees_left = df[df["Attrition"] == "Yes"]

print("\nAverage age of employees who left:")
print(employees_left["Age"].mean())
employees_left = df[df["Attrition"] == "Yes"]

print("\nAverage age of employees who left:")
print(employees_left["Age"].mean())
print("\nAttrition by department:")
print(employees_left["Department"].value_counts())

print("\nAverage salary of employees who left:")
print(employees_left["MonthlyIncome"].mean())

total_employees = len(df)
employees_left_count = len(employees_left)

print("\n--- HR ATTRITION REPORT ---")
print(f"Total Employees: {total_employees}")
print(f"Employees Who Left: {employees_left_count}")
print(f"Attrition Rate: {round(employees_left_count / total_employees * 100, 2)}%")
print(f"Average Age of Employees Who Left: {round(employees_left['Age'].mean(), 1)}")
print(f"Average Monthly Income of Employees Who Left: {round(employees_left['MonthlyIncome'].mean(), 2)}")