import streamlit as st
import pandas as pd
import plotly.express as px

# Load cleaned data (assuming you export it as CSV from the script before)
data_url = "performance_cleaned.csv"  # Replace with your path or URL
df = pd.read_csv(data_url, parse_dates=["Date"])

# --- SIDEBAR FILTERS ---
st.sidebar.title("Filters")

# Date range selector
date_min = df["Date"].min()
date_max = df["Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [date_min, date_max], min_value=date_min, max_value=date_max)

# Branch selector
branches = df["Branch"].dropna().unique()
selected_branches = st.sidebar.multiselect("Select Branches", options=sorted(branches), default=sorted(branches))

# --- FILTER DATA ---
df_filtered = df[(df["Date"] >= pd.to_datetime(date_range[0])) &
                 (df["Date"] <= pd.to_datetime(date_range[1])) &
                 (df["Branch"].isin(selected_branches))]

# --- MAIN DASHBOARD ---
st.title("🎬 Cinema Performance Dashboard")

# KPIs
def get_kpi(metric):
    return df_filtered[df_filtered["Metric"] == metric]["Value"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("🎟️ Box Office Sales", f"RM {get_kpi('Box Office Sales'):,.0f}")
col2.metric("🍿 Concession Sales", f"RM {get_kpi('Concession Sales'):,.0f}")
col3.metric("👥 Paid Admits", f"{get_kpi('Box Office Paid Admits'):,.0f}")

# --- TRENDS ---
st.subheader("📈 Performance Trends Over Time")
metrics_to_plot = st.multiselect("Select Metrics", df_filtered["Metric"].unique(), default=["Box Office Sales", "Concession Sales"])
df_trend = df_filtered[df_filtered["Metric"].isin(metrics_to_plot)]
df_trend_grouped = df_trend.groupby(["Date", "Metric"]).agg({"Value": "sum"}).reset_index()
fig = px.line(df_trend_grouped, x="Date", y="Value", color="Metric", title="Metric Trends Over Time")
st.plotly_chart(fig, use_container_width=True)

# --- BRANCH RANKING ---
st.subheader("🏆 Branch Performance")
metric_for_ranking = st.selectbox("Select Metric to Rank Branches", df_filtered["Metric"].unique(), index=0)
df_ranking = df_filtered[df_filtered["Metric"] == metric_for_ranking].groupby("Branch")["Value"].sum().sort_values(ascending=False).reset_index()
fig2 = px.bar(df_ranking, x="Value", y="Branch", orientation="h", title=f"Top Branches by {metric_for_ranking}", labels={"Value": metric_for_ranking, "Branch": "Branch"})
fig2.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig2, use_container_width=True)

# --- DATA TABLE ---
st.subheader("📋 Raw Data View")
st.dataframe(df_filtered.sort_values(by="Date", ascending=False))
