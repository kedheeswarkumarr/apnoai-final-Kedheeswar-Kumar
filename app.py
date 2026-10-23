import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="ApnoMart Q2 2026 Executive Dashboard", layout="wide")
st.title("ApnoMart Q2 2026 Executive Dashboard")
st.caption("Built by Kedheesw Ar · ApnoAI Data Analytics Intern · October 2026")

DATA_PATH = Path(__file__).parent / "apnomart-sales-data.csv"
df = pd.read_csv(DATA_PATH)
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
# Q2 means April–June. The supplied dataset has no April records.
df = df[(df["Order_Date"] >= "2026-04-01") & (df["Order_Date"] < "2026-07-01")].copy()

if df.empty:
    st.error("No Q2 2026 rows were found in the supplied CSV.")
    st.stop()

st.warning("Data coverage note: the supplied file contains May–June 2026 records only; April has no rows. Results represent the available Q2 slice.")
regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())
segments = sorted(df["Customer_Segment"].dropna().unique())

with st.sidebar:
    st.header("Dashboard filters")
    selected_regions = st.multiselect("Region", regions, default=regions)
    selected_categories = st.multiselect("Category", categories, default=categories)
    date_range = st.date_input("Order date range", value=(df["Order_Date"].min().date(), df["Order_Date"].max().date()),
                               min_value=df["Order_Date"].min().date(), max_value=df["Order_Date"].max().date())
    st.caption("Charts and KPIs update when filters change.")

filtered = df[df["Region"].isin(selected_regions) & df["Category"].isin(selected_categories)]
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    filtered = filtered[(filtered["Order_Date"].dt.date >= date_range[0]) & (filtered["Order_Date"].dt.date <= date_range[1])]

if filtered.empty:
    st.info("No rows match these filters. Select a wider date range, region or category.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order_ID"].nunique()
weighted_margin = total_profit / total_sales if total_sales else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"₹{total_sales:,.0f}")
c2.metric("Total Profit", f"₹{total_profit:,.0f}", delta_color="normal")
c3.metric("Total Orders", f"{total_orders:,}")
c4.metric("Avg Profit Margin", f"{weighted_margin:.1%}")

left, right = st.columns(2)
with left:
    cat = filtered.groupby("Category", as_index=False).agg(Sales=("Sales", "sum")).sort_values("Sales", ascending=False)
    fig = px.bar(cat, x="Category", y="Sales", title="Sales by Category", color_discrete_sequence=["#3478F6"])
    fig.update_layout(xaxis_title="", yaxis_title="Sales (₹)", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    trend = filtered.groupby(filtered["Order_Date"].dt.to_period("M").astype(str), as_index=False).agg(Sales=("Sales","sum"))
    trend.columns = ["Month", "Sales"]
    fig = px.line(trend, x="Month", y="Sales", markers=True, title="Sales Trend over Time", color_discrete_sequence=["#3478F6"])
    fig.update_layout(yaxis_title="Sales (₹)", margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    reg = filtered.groupby("Region", as_index=False).agg(Profit=("Profit", "sum")).sort_values("Profit", ascending=True)
    fig = px.bar(reg, x="Profit", y="Region", orientation="h", title="Profit by Region",
                 color="Profit", color_continuous_scale=["#D64545", "#16845B"])
    fig.update_layout(xaxis_title="Profit (₹)", yaxis_title="", coloraxis_showscale=False, margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)
with right:
    pay = filtered.groupby("Payment_Method", as_index=False).agg(Orders=("Order_ID","nunique"))
    fig = px.pie(pay, names="Payment_Method", values="Orders", hole=.48, title="Orders by Payment Method")
    fig.update_layout(margin=dict(l=10,r=10,t=55,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Executive takeaways")
cat_all = filtered.groupby("Category")["Sales"].sum().sort_values(ascending=False)
reg_all = filtered.groupby("Region")["Profit"].sum().sort_values(ascending=False)
loss_orders = int((filtered["Profit"] < 0).sum())
a, b, c = st.columns(3)
a.info(f"Revenue leader: **{cat_all.index[0]}** at ₹{cat_all.iloc[0]:,.0f}.")
b.success(f"Profit leader: **{reg_all.index[0]}** at ₹{reg_all.iloc[0]:,.0f}.")
c.warning(f"**{loss_orders}** filtered orders have negative profit; review discounts and costs.")
st.caption("Built by Kedheesw Ar · ApnoAI Data Analytics Intern · October 2026")
