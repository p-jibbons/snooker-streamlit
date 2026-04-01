import streamlit as st

st.set_page_config(
    page_title="OpenClaw Setup Guide",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.18), transparent 28%),
                radial-gradient(circle at left top, rgba(167, 139, 250, 0.16), transparent 30%),
                linear-gradient(180deg, #0b1020 0%, #111827 45%, #0f172a 100%);
            color: #e5eefc;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }
        .hero {
            padding: 2rem 2rem 1.5rem 2rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.75));
            backdrop-filter: blur(10px);
            border-radius: 24px;
            box-shadow: 0 18px 60px rgba(0, 0, 0, 0.32);
            margin-bottom: 1.2rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.5rem;
            line-height: 1.05;
            color: #f8fafc;
        }
        .hero p {
            margin: 0.8rem 0 0 0;
            font-size: 1.05rem;
            color: #cbd5e1;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.65rem;
            margin-top: 1rem;
        }
        .pill {
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(96, 165, 250, 0.24);
            color: #dbeafe;
            font-size: 0.9rem;
        }
        .glass {
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 20px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
        }
        .step-card {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(15, 23, 42, 0.72));
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 20px;
            padding: 1rem 1rem 0.65rem 1rem;
            margin-bottom: 0.95rem;
        }
        .step-title {
            font-weight: 700;
            font-size: 1.05rem;
            color: #f8fafc;
            margin-bottom: 0.3rem;
        }
        .muted {
            color: #94a3b8;
            font-size: 0.92rem;
        }
        .code-chip {
            display: inline-block;
            margin-top: 0.35rem;
            padding: 0.42rem 0.7rem;
            border-radius: 10px;
            background: rgba(2, 6, 23, 0.82);
            border: 1px solid rgba(71, 85, 105, 0.7);
            color: #bfdbfe;
            font-family: Consolas, Monaco, monospace;
            font-size: 0.9rem;
        }
        .section-header {
            margin: 0.35rem 0 0.8rem 0;
            color: #f8fafc;
        }
        .small-note {
            font-size: 0.86rem;
            color: #94a3b8;
        }
        .progress-wrap {
            margin-top: 0.35rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stCheckbox"] label p {
            color: #e2e8f0 !important;
            font-size: 0.98rem !important;
        }
        .footer-card {
            margin-top: 1rem;
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(14, 165, 233, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.22);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

steps = [
    {
        "title": "Install Node.js LTS",
        "body": "Download and install the current LTS release of Node.js for Windows. Accept the default installer options so npm is installed too.",
        "check": "Node.js installed",
        "command": "node -v",
    },
    {
        "title": "Open PowerShell as your normal user",
        "body": "Use a regular PowerShell window first. Only elevate later if Windows prompts you during setup.",
        "check": "PowerShell open",
        "command": "powershell",
    },
    {
        "title": "Install OpenClaw globally",
        "body": "Install OpenClaw from npm so the command is available anywhere on the machine.",
        "check": "OpenClaw installed",
        "command": "npm install -g openclaw",
    },
    {
        "title": "Confirm the install works",
        "body": "Verify the CLI responds before doing any configuration.",
        "check": "CLI verified",
        "command": "openclaw --help",
    },
    {
        "title": "Start the gateway service",
        "body": "Launch the OpenClaw gateway so the local services, web dashboard, and connectors can run.",
        "check": "Gateway started",
        "command": "openclaw gateway start",
    },
    {
        "title": "Open the dashboard in a browser",
        "body": "Once the gateway is up, open the local web dashboard and keep it bookmarked.",
        "check": "Dashboard opened",
        "command": "http://localhost:3000",
    },
    {
        "title": "Create or sign in to the OpenAI-compatible provider account used by OpenClaw",
        "body": "Have the API key ready before wiring up chats. If your company uses a specific provider/model, use that one.",
        "check": "API key ready",
        "command": "Paste the key into OpenClaw settings when prompted",
    },
    {
        "title": "Configure the model/provider in OpenClaw",
        "body": "Open the dashboard settings and add the API key plus the preferred default model. Save before moving on.",
        "check": "Model configured",
        "command": "Use the Settings page in the dashboard",
    },
    {
        "title": "Create a Telegram bot with BotFather",
        "body": "In Telegram, message @BotFather, run /newbot, choose a name, and copy the bot token it gives you.",
        "check": "Telegram bot token created",
        "command": "Telegram → @BotFather → /newbot",
    },
    {
        "title": "Add Telegram credentials to OpenClaw",
        "body": "In the OpenClaw dashboard or config, enable Telegram and paste the bot token so the chat connector can come online.",
        "check": "Telegram connected",
        "command": "Use the dashboard integrations/config for Telegram",
    },
    {
        "title": "Message the bot from Telegram",
        "body": "Send the bot a test message like /start or hello and confirm OpenClaw receives it.",
        "check": "Telegram test passed",
        "command": "Send a Telegram message to the bot",
    },
    {
        "title": "Verify web chat works too",
        "body": "Use the dashboard chat interface to send a test prompt and confirm both Telegram and the web UI are working.",
        "check": "Web dashboard chat tested",
        "command": "Send a test prompt in the dashboard",
    },
]

completed = 0
for i, step in enumerate(steps):
    if st.session_state.get(f"step_{i}", False):
        completed += 1

progress = completed / len(steps)

st.markdown(
    """
    <div class="hero">
        <h1>OpenClaw setup for a new Windows machine</h1>
        <p>
            A clean, boss-friendly walkthrough for getting OpenClaw installed and working with
            <strong>Telegram</strong> plus the <strong>web dashboard</strong>.
        </p>
        <div class="pill-row">
            <div class="pill">Windows setup</div>
            <div class="pill">Telegram chat</div>
            <div class="pill">Web dashboard</div>
            <div class="pill">Step-by-step checklist</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.45, 0.9], gap="large")

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("Checklist progress")
    st.markdown(
        f"<div class='small-note'>{completed} of {len(steps)} steps complete</div>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="progress-wrap">', unsafe_allow_html=True)
    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### What your boss needs ready")
    st.markdown(
        """
        - A Windows machine with internet access
        - Permission to install apps
        - An API key for the AI provider
        - A Telegram account for bot setup
        """
    )

    st.markdown("### Quick commands")
    st.code(
        "npm install -g openclaw\nopenclaw gateway start\nopenclaw --help",
        language="powershell",
    )

    if completed == len(steps):
        st.success("Everything on the list is checked. The machine should be ready for Telegram and dashboard chat.")
    else:
        st.info("Work top to bottom. If something fails, stop there and fix that step before continuing.")

    st.markdown("</div>", unsafe_allow_html=True)

with left:
    st.markdown("## Step-by-step walkthrough")
    for i, step in enumerate(steps, start=1):
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown(
            f"<div class='step-title'>Step {i}. {step['title']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='muted'>{step['body']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='code-chip'>{step['command']}</div>",
            unsafe_allow_html=True,
        )
        st.checkbox(step["check"], key=f"step_{i-1}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("## Final handoff")
st.markdown(
    """
    <div class="footer-card">
        After setup, your boss should be able to:<br><br>
        ✅ open the local OpenClaw dashboard<br>
        ✅ chat through the web interface<br>
        ✅ send messages to the Telegram bot<br>
        ✅ manage the local gateway from the CLI if needed
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Troubleshooting notes"):
    st.markdown(
        """
        - If `openclaw` is not recognized, close and reopen PowerShell after the npm install.
        - If the dashboard does not load, run `openclaw gateway status` and restart it if needed.
        - If Telegram does not respond, double-check the bot token and whether Telegram was enabled in config.
        - Keep the guide simple: install first, provider second, Telegram third, test everything last.
        """
    )
