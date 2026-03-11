# ==============================
# Crypto Investment Manager Dashboard
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from concurrent.futures import ThreadPoolExecutor

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="Crypto Investment Manager", layout="wide")

st.title("🪙 Crypto Investment Manager Dashboard")

# ------------------------------
# Load Data
# ------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("preprocessed_data.csv", index_col=0, parse_dates=True)
    return df

data = load_data()

# ------------------------------
# Sidebar Inputs
# ------------------------------
st.sidebar.header("📥 Investment Inputs")

amount = st.sidebar.number_input("Enter Investment Amount (₹)", min_value=1000, value=10000, step=500)

level = st.sidebar.selectbox(
    "Select Investment Level",
    ["Low Risk", "Medium Risk", "High Risk"]
)

# ------------------------------
# EDA Section
# ------------------------------
st.subheader("📊 Exploratory Data Analysis")

col1, col2 = st.columns(2)

with col1:
    st.write("### Price Trends")
    st.line_chart(data)

with col2:
    st.write("### Returns Distribution")
    returns = data.pct_change().dropna()
    st.bar_chart(returns.mean())

# ------------------------------
# Risk + Prediction Functions
# ------------------------------

def risk_checker(df):
    return df.pct_change().std()

def predictor(df):
    return df.pct_change().mean()

# Parallel Processing
with ThreadPoolExecutor() as executor:
    risk_future = executor.submit(risk_checker, data)
    pred_future = executor.submit(predictor, data)

risk_values = risk_future.result()
pred_values = pred_future.result()

# ------------------------------
# Investment Mix Calculator
# ------------------------------

st.subheader("📈 Investment Mix Calculator")

if st.button("Calculate Investment Strategy"):

    # Rule-based weights
    weights = pred_values / risk_values

    if level == "Low Risk":
        weights = weights / weights.sum()

    elif level == "Medium Risk":
        weights = (weights * 1.2) / (weights * 1.2).sum()

    else:  # High Risk
        weights = (weights * 1.5) / (weights * 1.5).sum()

    allocation = weights * amount

    # Table Output
    result_df = pd.DataFrame({
        "Risk": risk_values,
        "Expected Return": pred_values,
        "Weight": weights,
        "Investment Amount": allocation
    })

    st.write("### 📋 Allocation Table")
    st.dataframe(result_df.style.format("{:.4f}"))

    # ------------------------------
    # Charts
    # ------------------------------
    col3, col4 = st.columns(2)

    with col3:
        st.write("### 🥧 Allocation Chart")
        fig, ax = plt.subplots()
        ax.pie(allocation, labels=allocation.index, autopct="%1.1f%%")
        st.pyplot(fig)

    with col4:
        st.write("### 📉 Risk vs Return")
        fig2, ax2 = plt.subplots()
        ax2.scatter(risk_values, pred_values)
        for i, txt in enumerate(data.columns):
            ax2.annotate(txt, (risk_values[i], pred_values[i]))
        ax2.set_xlabel("Risk")
        ax2.set_ylabel("Return")
        st.pyplot(fig2)

    # ------------------------------
    # Save to Database
    # ------------------------------
    conn = sqlite3.connect("crypto_trends.db")
    result_df.to_sql("investment_result", conn, if_exists="replace")
    conn.close()

    # Save CSV
    result_df.to_csv("investment_report.csv")

    st.success("✅ Report Saved (CSV + Database)")

# ------------------------------
# Risk Checker Section
# ------------------------------
st.subheader("⚠️ Risk Checker")

risk_df = pd.DataFrame({"Risk": risk_values})
st.bar_chart(risk_df)

# ------------------------------
# Level Description
# ------------------------------
st.subheader("ℹ️ Investment Level Guide")

if level == "Low Risk":
    st.info("Focus on stable coins with low volatility.")
elif level == "Medium Risk":
    st.info("Balanced portfolio with moderate growth.")
else:
    st.warning("Aggressive strategy with higher volatility.")
