import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


# CREATE PROJECT FOLDERS
BASE_DIR = Path(".")
CHARTS_DIR = BASE_DIR / "charts"
OUTPUTS_DIR = BASE_DIR / "outputs"

CHARTS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

print("Folders created successfully.")


#  LOAD DATA
file_path = BASE_DIR / "Online_Retail.csv"

df = pd.read_csv("Customer_Segementation_Analysis/online_retail.csv", encoding="utf-8-sig")

# Clean column names
df.columns = df.columns.str.strip()

print("\nDataset loaded successfully.")
print(df.head())
print(df.info())


# DATA CLEANING

df = df.dropna(subset=["CustomerID"]).copy()


df["CustomerID"] = df["CustomerID"].astype(int)


df = df[~df["InvoiceNo"].astype(str).str.startswith("C")].copy()


df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)].copy()


df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])


df["Revenue"] = df["Quantity"] * df["UnitPrice"]


cleaned_data_path = OUTPUTS_DIR / "cleaned_retail_data.csv"
df.to_csv(cleaned_data_path, index=False)

print("\nData cleaned successfully.")
print(f"Cleaned data saved to: {cleaned_data_path}")


#  FEATURE ENGINEERING
snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

customer_df = df.groupby("CustomerID").agg({
    "InvoiceDate": lambda x: (snapshot_date - x.max()).days,
    "InvoiceNo": "nunique",
    "Revenue": "sum",
    "Quantity": "sum",
    "StockCode": "nunique"
}).reset_index()

customer_df.columns = [
    "CustomerID",
    "Recency",
    "Frequency",
    "Monetary",
    "Total_Quantity",
    "Unique_Products"
]

customer_df["Avg_Order_Value"] = (
    customer_df["Monetary"] / customer_df["Frequency"]
)

# Save customer features
customer_features_path = OUTPUTS_DIR / "customer_features.csv"
customer_df.to_csv(customer_features_path, index=False)

print("\nCustomer-level features created successfully.")
print(customer_df.head())
print(f"Customer features saved to: {customer_features_path}")


#  EDA
sns.set_theme(style="whitegrid")

features = [
    "Recency",
    "Frequency",
    "Monetary",
    "Total_Quantity",
    "Unique_Products",
    "Avg_Order_Value"
]

# Histograms
plt.figure(figsize=(16, 10))
customer_df[features].hist(bins=25, figsize=(16, 10))
plt.suptitle("Feature Distributions Before Transformation", fontsize=16)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "feature_distributions.png", dpi=300, bbox_inches="tight")
plt.close()

# Boxplots
plt.figure(figsize=(16, 10))
for i, col in enumerate(features, 1):
    plt.subplot(2, 3, i)
    sns.boxplot(x=customer_df[col])
    plt.title(col)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "boxplots_before_log_transform.png", dpi=300, bbox_inches="tight")
plt.close()

print("\nEDA charts saved successfully.")


#  PREPROCESSING
clustering_data = customer_df[features].copy()

log_transform_cols = [
    "Recency",
    "Frequency",
    "Monetary",
    "Total_Quantity",
    "Avg_Order_Value"
]

for col in log_transform_cols:
    clustering_data[col] = np.log1p(clustering_data[col])

# Scale data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(clustering_data)

print("\nData preprocessing completed.")


#  FIND OPTIMAL NUMBER OF CLUSTERS
k_range = range(2, 11)
inertia = []
silhouette_scores = []

for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_data)
    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(scaled_data, cluster_labels))

# Elbow method plot
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, marker="o")
plt.title("Elbow Method")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.savefig(CHARTS_DIR / "elbow_method.png", dpi=300, bbox_inches="tight")
plt.close()

# Silhouette scores plot
plt.figure(figsize=(8, 5))
plt.plot(k_range, silhouette_scores, marker="o")
plt.title("Silhouette Scores by Number of Clusters")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Silhouette Score")
plt.savefig(CHARTS_DIR / "silhouette_scores.png", dpi=300, bbox_inches="tight")
plt.close()

# Choose best k based on highest silhouette score
optimal_k = k_range[np.argmax(silhouette_scores)]
print(f"\nOptimal number of clusters based on silhouette score: {optimal_k}")


#  TRAIN FINAL K-MEANS MODEL
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
customer_df["Cluster"] = kmeans.fit_predict(scaled_data)

print("\nK-Means model trained successfully.")


#  PCA VISUALIZATION
pca = PCA(n_components=2, random_state=42)
pca_components = pca.fit_transform(scaled_data)

customer_df["PCA1"] = pca_components[:, 0]
customer_df["PCA2"] = pca_components[:, 1]

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=customer_df,
    x="PCA1",
    y="PCA2",
    hue="Cluster",
    palette="Set2",
    s=80,
    alpha=0.8
)
plt.title("Customer Segments Visualized with PCA")
plt.savefig(CHARTS_DIR / "pca_customer_segments.png", dpi=300, bbox_inches="tight")
plt.close()

print("\nPCA chart saved successfully.")


#  CLUSTER PROFILING
cluster_summary = customer_df.groupby("Cluster").agg({
    "Recency": "mean",
    "Frequency": "mean",
    "Monetary": "mean",
    "Total_Quantity": "mean",
    "Unique_Products": "mean",
    "Avg_Order_Value": "mean",
    "CustomerID": "count"
}).rename(columns={"CustomerID": "Customer_Count"}).round(2)

cluster_summary_path = OUTPUTS_DIR / "cluster_summary.csv"
cluster_summary.to_csv(cluster_summary_path)

print("\nCluster summary:")
print(cluster_summary)
print(f"Cluster summary saved to: {cluster_summary_path}")


# ASSIGN SEGMENT LABELS
ranking_df = cluster_summary.copy()
ranking_df["Value_Score"] = (
    ranking_df["Monetary"].rank(method="dense", ascending=False) +
    ranking_df["Frequency"].rank(method="dense", ascending=False) +
    ranking_df["Recency"].rank(method="dense", ascending=True)
)

ranking_df = ranking_df.sort_values("Value_Score", ascending=False)

segment_names = {}
ordered_clusters = ranking_df.index.tolist()

default_labels = [
    "VIP Customers",
    "Loyal Customers",
    "Regular Customers",
    "At-Risk Customers",
    "Low-Value Customers",
    "Occasional Customers",
    "Dormant Customers",
    "Promising Customers"
]

for i, cluster_id in enumerate(ordered_clusters):
    if i < len(default_labels):
        segment_names[cluster_id] = default_labels[i]
    else:
        segment_names[cluster_id] = f"Segment {cluster_id}"

customer_df["Segment"] = customer_df["Cluster"].map(segment_names)

print("\nSegment labels assigned:")
print(segment_names)


# HEATMAP OF CLUSTER PROFILES
heatmap_data = cluster_summary.drop(columns=["Customer_Count"])

plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlGnBu")
plt.title("Cluster Profile Heatmap")
plt.savefig(CHARTS_DIR / "cluster_heatmap.png", dpi=300, bbox_inches="tight")
plt.close()

print("\nHeatmap saved successfully.")


# SAVE FINAL OUTPUTS
customer_segments_path = OUTPUTS_DIR / "customer_segments.csv"
customer_df.to_csv(customer_segments_path, index=False)

print(f"\nCustomer segments saved to: {customer_segments_path}")


#  WRITE PROJECT SUMMARY
summary_text = f"""
Customer Segmentation Project Summary

Dataset:
- Online Retail Dataset

Data Cleaning Steps:
- Removed missing CustomerID rows
- Removed cancelled invoices
- Removed rows with non-positive Quantity and UnitPrice
- Created Revenue feature

Customer Features Used:
- Recency
- Frequency
- Monetary
- Total_Quantity
- Unique_Products
- Avg_Order_Value

Model:
- K-Means Clustering
- Optimal number of clusters selected using silhouette score
- Selected k = {optimal_k}

Output Files:
- cleaned_retail_data.csv
- customer_features.csv
- customer_segments.csv
- cluster_summary.csv

Charts Saved:
- feature_distributions.png
- boxplots_before_log_transform.png
- elbow_method.png
- silhouette_scores.png
- pca_customer_segments.png
- cluster_heatmap.png

Segment Mapping:
{segment_names}

Cluster Summary:
{cluster_summary.to_string()}
"""

summary_path = OUTPUTS_DIR / "project_summary.txt"
with open(summary_path, "w", encoding="utf-8") as f:
    f.write(summary_text)

print(f"Project summary saved to: {summary_path}")


# FINAL MESSAGE
print("\nProject completed successfully.")
print(f"Charts folder: {CHARTS_DIR.resolve()}")
print(f"Outputs folder: {OUTPUTS_DIR.resolve()}")