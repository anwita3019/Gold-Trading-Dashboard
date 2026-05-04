import streamlit as st
import yfinance as yf
import time
import datetime
# --- CONFIG ---
st.set_page_config(page_title="Gold Strategy Bot", layout="centered")
st.title("💰 Gold Strategy Dashboard")
# Create a timestamp and status log
current_time = datetime.datetime.now().strftime("%H:%M:%S")
st.sidebar.info(f"Last Data Sync: {current_time}")
st.sidebar.write("Status: Connected to Yahoo Finance API")
ui_placeholder = st.empty()

SYMBOL = "GC=F"
CURRENCY_SYMBOL = "USDINR=X"


def fetch_and_calculate():
    # 1. Fetching
    df = yf.download(SYMBOL, period="1mo", interval="1h", progress=False)
    fx = yf.download(CURRENCY_SYMBOL, period="1d", interval="1m", progress=False)

    # 2. Extracting Numbers
    usd_price = df['Close'].iloc[-1].item()
    usd_inr = fx['Close'].iloc[-1].item()
    inr_price = (usd_price / 31.1035) * usd_inr * 10

    # 3. RSI Logic (Wilder's)
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(alpha=1 / 14, adjust=False).mean()
    ema_down = down.ewm(alpha=1 / 14, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1].item()

    return usd_price, inr_price, current_rsi


# --- THE LOOP ---
while True:
    usd, inr, rsi_val = fetch_and_calculate()

    with ui_placeholder.container():
        # Display Prices in neat columns
        c1, c2 = st.columns(2)
        c1.metric("Gold (USD)", f"${usd:,.2f}")
        # Assuming you want to see how far you are from a target or previous price
        c2.metric("Gold (INR)", f"₹{inr:,.0f}")

        st.divider()
        st.subheader(f"Current RSI: {rsi_val:.2f}")

        # Color-coded Alerts
        if rsi_val > 65:
            st.error("🚨 SELL SIGNAL (Overbought)")
        elif rsi_val < 42:
            st.success("✅ BUY SIGNAL (Oversold)")
        else:
            st.warning("⏳ NEUTRAL (Hold)")

    time.sleep(15)
