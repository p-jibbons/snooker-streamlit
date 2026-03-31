import math
from datetime import date, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Lucius Demo", page_icon="✨", layout="wide")

st.markdown(
    """
    <style>
    .hero {
        padding: 1.25rem 1.5rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, #111827 0%, #1f2937 60%, #374151 100%);
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }
    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
    }
    .hero p {
        margin: 0.5rem 0 0 0;
        color: #d1d5db;
        font-size: 1rem;
    }
    .soft-card {
        border: 1px solid rgba(100,116,139,0.18);
        border-radius: 0.9rem;
        padding: 1rem;
        background: #ffffff;
        box-shadow: 0 6px 20px rgba(15,23,42,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Lucius Demo</h1>
        <p>A small polished Streamlit app: quick metrics, interactive forecasting, and a clean status dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    baseline = st.slider("Baseline daily users", 100, 5000, 1200, step=50)
    growth = st.slider("Weekly growth %", 0.0, 25.0, 6.5, step=0.5)
    conversion = st.slider("Conversion rate %", 1.0, 20.0, 6.0, step=0.5)
    avg_value = st.slider("Average value ($)", 5, 200, 42, step=1)
    days = st.slider("Forecast days", 7, 60, 21, step=7)

col1, col2, col3, col4 = st.columns(4)
projected_users = int(baseline * ((1 + growth / 100) ** (days / 7)))
projected_conversions = int(projected_users * conversion / 100)
projected_revenue = projected_conversions * avg_value
momentum = growth * conversion

col1.metric("Projected users", f"{projected_users:,}")
col2.metric("Projected conversions", f"{projected_conversions:,}")
col3.metric("Projected revenue", f"${projected_revenue:,}")
col4.metric("Momentum score", f"{momentum:.1f}")

st.subheader("Forecast view")
rows = []
start = date.today()
for i in range(days):
    daily_users = baseline * ((1 + growth / 100) ** (i / 7))
    daily_conversions = daily_users * conversion / 100
    daily_revenue = daily_conversions * avg_value
    rows.append(
        {
            "date": start + timedelta(days=i),
            "users": round(daily_users),
            "conversions": round(daily_conversions),
            "revenue": round(daily_revenue, 2),
        }
    )

df = pd.DataFrame(rows)

chart_cols = st.columns(2)
with chart_cols[0]:
    st.markdown("**User growth**")
    peak_users = max(df["users"].max(), 1)
    for _, row in df.tail(min(days, 12)).iterrows():
        width_pct = max(8, int((row["users"] / peak_users) * 100))
        st.markdown(
            f"<div style='margin-bottom:0.35rem'><div style='font-size:0.82rem;color:#6b7280'>{row['date']}</div>"
            f"<div style='background:#e5e7eb;border-radius:999px;height:14px;overflow:hidden'>"
            f"<div style='width:{width_pct}%;background:linear-gradient(90deg,#2563eb,#60a5fa);height:14px'></div></div>"
            f"<div style='font-size:0.82rem;font-weight:600'>{int(row['users']):,} users</div></div>",
            unsafe_allow_html=True,
        )

with chart_cols[1]:
    st.markdown("**Revenue growth**")
    peak_revenue = max(df["revenue"].max(), 1)
    for _, row in df.tail(min(days, 12)).iterrows():
        width_pct = max(8, int((row["revenue"] / peak_revenue) * 100))
        st.markdown(
            f"<div style='margin-bottom:0.35rem'><div style='font-size:0.82rem;color:#6b7280'>{row['date']}</div>"
            f"<div style='background:#e5e7eb;border-radius:999px;height:14px;overflow:hidden'>"
            f"<div style='width:{width_pct}%;background:linear-gradient(90deg,#059669,#34d399);height:14px'></div></div>"
            f"<div style='font-size:0.82rem;font-weight:600'>${row['revenue']:,.0f}</div></div>",
            unsafe_allow_html=True,
        )

left, right = st.columns([1.3, 1])
with left:
    st.subheader("Data table")
    st.dataframe(df, use_container_width=True, hide_index=True)

with right:
    st.subheader("What this demonstrates")
    st.markdown(
        """
        <div class="soft-card">
        <ul>
          <li>Custom styling without overcomplicating the app</li>
          <li>Live controls with immediate recalculation</li>
          <li>Charts, metrics, and table output together</li>
          <li>A layout that feels more like a product than a toy</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Quick assessment")
if projected_revenue > 10000:
    st.success("This scenario looks healthy: the current settings project meaningful revenue over the selected horizon.")
elif projected_revenue > 4000:
    st.info("This is a decent middle-ground scenario. A small lift in conversion or value would make it much stronger.")
else:
    st.warning("This setup is viable as a test, but not yet compelling. Improving either growth or conversion would move the needle fast.")
