import time

import streamlit as st

st.set_page_config(page_title="Universal Paperclips Mockup", page_icon="📎", layout="centered")

if "paperclips" not in st.session_state:
    st.session_state.paperclips = 0
if "funds" not in st.session_state:
    st.session_state.funds = 0.0
if "wire" not in st.session_state:
    st.session_state.wire = 1000
if "price" not in st.session_state:
    st.session_state.price = 0.25
if "marketing" not in st.session_state:
    st.session_state.marketing = 0
if "auto_clippers" not in st.session_state:
    st.session_state.auto_clippers = 0
if "last_tick" not in st.session_state:
    st.session_state.last_tick = time.time()


BEAT_SECONDS = 0.35


def run_tick():
    now = time.time()
    elapsed = now - st.session_state.last_tick
    if elapsed < BEAT_SECONDS:
        return

    ticks = int(elapsed / BEAT_SECONDS)
    for _ in range(ticks):
        if st.session_state.auto_clippers > 0 and st.session_state.wire > 0:
            produced = min(st.session_state.auto_clippers, st.session_state.wire)
            st.session_state.paperclips += produced
            st.session_state.funds += produced * st.session_state.price
            st.session_state.wire -= produced
    st.session_state.last_tick = now


run_tick()

st.markdown(
    """
    <style>
    .title {
        font-size: 2rem;
        font-weight: 800;
        color: #111111;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #666666;
        margin-bottom: 1rem;
    }
    .panel {
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1rem;
        background: #ffffff;
        margin-bottom: 1rem;
    }
    .big {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }
    .label {
        color: #6b7280;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>Universal Paperclips</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>A tiny playable mockup of the opening game state.</div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 0.9])

with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Paperclips</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big'>{st.session_state.paperclips}</div>", unsafe_allow_html=True)
    if st.button("Make Paperclip", use_container_width=True, disabled=st.session_state.wire <= 0):
        st.session_state.paperclips += 1
        st.session_state.funds += st.session_state.price
        st.session_state.wire -= 1
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Available Funds</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big'>${st.session_state.funds:,.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Price per Clip</div>", unsafe_allow_html=True)
    price_value = st.text_input("", value=f"${st.session_state.price:.2f}", label_visibility="collapsed")
    try:
        st.session_state.price = max(0.01, float(price_value.replace("$", "").strip()))
    except ValueError:
        pass
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Marketing</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big'>{st.session_state.marketing}</div>", unsafe_allow_html=True)
    if st.button("Buy Marketing", use_container_width=True, disabled=st.session_state.funds < 100):
        st.session_state.funds -= 100
        st.session_state.marketing += 1
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Cost: $100.00</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Wire Inventory</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='big'>{st.session_state.wire:,} inches</div>", unsafe_allow_html=True)
    if st.button("Buy Wire", use_container_width=True, disabled=st.session_state.funds < 20):
        st.session_state.funds -= 20
        st.session_state.wire += 1000
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Cost: $20.00</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='label'>Automatic Wire Cutters</div>", unsafe_allow_html=True)
st.markdown(f"<div class='big'>{st.session_state.auto_clippers}</div>", unsafe_allow_html=True)
if st.button("Buy AutoClippers", use_container_width=True, disabled=st.session_state.funds < 5):
    st.session_state.funds -= 5
    st.session_state.auto_clippers += 1
st.caption("Each AutoClipper makes 1 paperclip per beat if wire is available.")
st.markdown("</div>", unsafe_allow_html=True)

demand = min(100, st.session_state.paperclips // 2 + st.session_state.marketing * 10)

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='label'>Public Demand</div>", unsafe_allow_html=True)
st.progress(demand)
if demand == 0:
    st.caption("No demand yet. You have not sold any clips.")
else:
    st.caption(f"Demand is building. Current interest level: {demand}%")
st.markdown("</div>", unsafe_allow_html=True)

time.sleep(BEAT_SECONDS)
st.rerun()
