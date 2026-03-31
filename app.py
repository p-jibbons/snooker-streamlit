import streamlit as st

st.set_page_config(page_title="Universal Paperclips Mockup", page_icon="📎", layout="centered")

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
st.markdown("<div class='subtitle'>A tiny mockup of the opening game state.</div>", unsafe_allow_html=True)

left, right = st.columns([1.1, 0.9])

with left:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Paperclips</div>", unsafe_allow_html=True)
    st.markdown("<div class='big'>0</div>", unsafe_allow_html=True)
    st.button("Make Paperclip", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Available Funds</div>", unsafe_allow_html=True)
    st.markdown("<div class='big'>$0.00</div>", unsafe_allow_html=True)
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Price per Clip</div>", unsafe_allow_html=True)
    st.text_input("", value="$0.25", label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Marketing</div>", unsafe_allow_html=True)
    st.markdown("<div class='big'>0</div>", unsafe_allow_html=True)
    st.button("Buy Marketing", use_container_width=True, disabled=True)
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Cost: $100.00</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Wire Inventory</div>", unsafe_allow_html=True)
    st.markdown("<div class='big'>1,000 inches</div>", unsafe_allow_html=True)
    st.button("Buy Wire", use_container_width=True, disabled=True)
    st.markdown("<div class='label' style='margin-top:0.75rem;'>Cost: $20.00</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.markdown("<div class='label'>Public Demand</div>", unsafe_allow_html=True)
st.progress(0)
st.caption("No demand yet. You have not sold any clips.")
st.markdown("</div>", unsafe_allow_html=True)
