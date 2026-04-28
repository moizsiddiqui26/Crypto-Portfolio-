
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import smtplib
from concurrent.futures import ThreadPoolExecutor

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Crypto Investment Manager", layout="wide")
st.title("🪙 Crypto Investment Manager")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("preprocessed_data.csv", index_col=0, parse_dates=True)

data = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.header("📥 Investment Inputs")

amount = st.sidebar.number_input("Enter Investment Amount (₹)", min_value=1000, value=10000, step=500)

level = st.sidebar.selectbox(
    "Select Investment Level",
    ["Low Risk", "Medium Risk", "High Risk"]
)

email_option = st.sidebar.checkbox("Enable Email Alert")

# ---------------- EDA ----------------
st.subheader("📊 Market Overview")

col1, col2 = st.columns(2)

with col1:
    st.write("### Price Trends")
    st.line_chart(data)

with col2:
    st.write("### Average Returns")
    returns = data.pct_change().dropna()
    st.bar_chart(returns.mean())

# ---------------- RISK + PREDICTOR ----------------

def risk_checker(df):
    return df.pct_change().std()

def predictor(df):
    return df.pct_change().mean()

with ThreadPoolExecutor() as executor:
    risk_future = executor.submit(risk_checker, data)
    pred_future = executor.submit(predictor, data)

risk_vals = risk_future.result()
pred_vals = pred_future.result()

# ---------------- MIX CALCULATOR ----------------
st.subheader("📈 Investment Mix Calculator")

if st.button("Calculate Strategy"):

    weights = pred_vals / risk_vals

    if level == "Low Risk":
        weights = weights / weights.sum()
    elif level == "Medium Risk":
        weights = (weights * 1.2) / (weights * 1.2).sum()
    else:
        weights = (weights * 1.5) / (weights * 1.5).sum()

    allocation = weights * amount

    result_df = pd.DataFrame({
        "Risk": risk_vals,
        "Expected Return": pred_vals,
        "Weight": weights,
        "Investment Amount": allocation
    })

    # -------- TABLE --------
    st.write("### 📋 Allocation Table")
    st.dataframe(result_df.style.format("{:.4f}"))

    # -------- CHARTS --------
    col3, col4 = st.columns(2)

    with col3:
        st.write("### 🥧 Allocation Chart")
        fig, ax = plt.subplots()
        ax.pie(allocation, labels=allocation.index, autopct="%1.1f%%")
        st.pyplot(fig)

    with col4:
        st.write("### 📉 Risk vs Return")
        fig2, ax2 = plt.subplots()
        ax2.scatter(risk_vals, pred_vals)
        for i, txt in enumerate(data.columns):
            ax2.annotate(txt, (risk_vals[i], pred_vals[i]))
        ax2.set_xlabel("Risk")
        ax2.set_ylabel("Return")
        st.pyplot(fig2)

    # -------- SAVE CSV --------
    result_df.to_csv("investment_report.csv")

    # -------- SAVE DATABASE --------
    conn = sqlite3.connect("crypto_trends.db")
    result_df.to_sql("investment_result", conn, if_exists="replace")
    conn.close()

    # -------- EMAIL ALERT --------
    if email_option:
        try:
            sender = "your_email@gmail.com"
            password = "your_app_password"
            receiver = "receiver_email@gmail.com"

            message = f"Subject: Crypto Alert\n\nNew strategy generated:\n{result_df}"

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, message)
            server.quit()

            st.success("📧 Email Sent Successfully!")

        except:
            st.error("Email sending failed")

    st.success("✅ Strategy Generated & Saved")

# ---------------- RISK CHECKER ----------------
st.subheader("⚠️ Risk Checker")
st.bar_chart(pd.DataFrame({"Risk": risk_vals}))

# ---------------- LEVEL GUIDE ----------------
st.subheader("ℹ️ Investment Level Guide")

if level == "Low Risk":
    st.info("Focus on stable coins with low volatility.")
elif level == "Medium Risk":
    st.info("Balanced portfolio with moderate growth.")
else:
    st.warning("Aggressive strategy with higher volatility.")
