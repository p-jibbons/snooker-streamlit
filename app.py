from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="HP Stock Report", page_icon="📈", layout="wide")

TICKER = "HPQ"
EVENTS = [
    {
        "date": "2025-05-29",
        "title": "Q2 FY25 earnings",
        "detail": "HP reported quarterly earnings and updated investors on cost discipline and market conditions.",
    },
    {
        "date": "2025-08-28",
        "title": "Q3 FY25 earnings",
        "detail": "Quarterly results highlighted printing/PC trends and AI PC commentary.",
    },
    {
        "date": "2025-11-26",
        "title": "Q4 / full-year update",
        "detail": "HP closed the fiscal year and provided its latest outlook.",
    },
    {
        "date": "2026-02-27",
        "title": "Q1 FY26 earnings window",
        "detail": "Typical period for the next major earnings-driven move and analyst reassessment.",
    },
]

@st.cache_data(ttl=3600)
def load_history():
    end = datetime.utcnow()
    start = end - timedelta(days=370)
    history = yf.download(TICKER, start=start, end=end, auto_adjust=True, progress=False)
    if history.empty:
        raise ValueError("No market data returned for HPQ.")

    if isinstance(history.columns, pd.MultiIndex):
        history.columns = [col[0] for col in history.columns]

    history = history.reset_index()
    history["Date"] = pd.to_datetime(history["Date"])
    return history


def nearest_close(history: pd.DataFrame, target_date: pd.Timestamp):
    idx = (history["Date"] - target_date).abs().idxmin()
    row = history.loc[idx]
    return row["Date"], float(row["Close"])


st.title("HP Stock Performance Report")
st.caption("One-year view of HP Inc. (NYSE: HPQ) with annotated major events.")

try:
    history = load_history()
except Exception as exc:
    st.error(f"Could not load HPQ data: {exc}")
    st.stop()

start_close = float(history.iloc[0]["Close"])
end_close = float(history.iloc[-1]["Close"])
change_pct = ((end_close / start_close) - 1) * 100
high_close = float(history["Close"].max())
low_close = float(history["Close"].min())
avg_volume = int(history["Volume"].mean())

m1, m2, m3, m4 = st.columns(4)
m1.metric("1Y change", f"{change_pct:+.1f}%")
m2.metric("Latest close", f"${end_close:.2f}")
m3.metric("1Y range", f"${low_close:.2f} - ${high_close:.2f}")
m4.metric("Avg volume", f"{avg_volume:,}")

st.subheader("Price trend")
recent_points = history[["Date", "Close"]].tail(18).copy()
peak_close = max(recent_points["Close"].max(), 1)
for _, row in recent_points.iterrows():
    width_pct = max(8, int((float(row["Close"]) / peak_close) * 100))
    st.markdown(
        f"<div style='margin-bottom:0.35rem'><div style='font-size:0.82rem;color:#6b7280'>{row['Date'].date()}</div>"
        f"<div style='background:#e5e7eb;border-radius:999px;height:14px;overflow:hidden'>"
        f"<div style='width:{width_pct}%;background:linear-gradient(90deg,#1d4ed8,#60a5fa);height:14px'></div></div>"
        f"<div style='font-size:0.82rem;font-weight:600'>${float(row['Close']):.2f}</div></div>",
        unsafe_allow_html=True,
    )

event_rows = []
for event in EVENTS:
    target = pd.Timestamp(event["date"])
    actual_date, actual_close = nearest_close(history, target)
    event_rows.append(
        {
            "Event date": actual_date.date().isoformat(),
            "Event": event["title"],
            "Close": round(actual_close, 2),
            "Notes": event["detail"],
        }
    )

events_df = pd.DataFrame(event_rows)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Annotated major events")
    st.dataframe(events_df, use_container_width=True, hide_index=True)

with right:
    st.subheader("Quick read")
    direction = "up" if change_pct >= 0 else "down"
    st.markdown(
        f"""
        - Over the last year, HPQ is **{direction} {abs(change_pct):.1f}%**.
        - The stock traded between **${low_close:.2f}** and **${high_close:.2f}**.
        - Major movement windows often line up with **earnings releases and guidance updates**.
        - This is a compact performance summary, not full investment advice.
        """
    )

st.subheader("Recent closes")
recent = history[["Date", "Close", "Volume"]].tail(20).copy()
recent["Date"] = recent["Date"].dt.date.astype(str)
recent["Close"] = recent["Close"].map(lambda x: f"${float(x):.2f}")
recent["Volume"] = recent["Volume"].map(lambda x: f"{int(x):,}")
st.dataframe(recent, use_container_width=True, hide_index=True)
