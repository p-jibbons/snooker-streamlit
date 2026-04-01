import random

import streamlit as st

st.set_page_config(
    page_title="Moonmilk Ranch",
    page_icon="🐮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(253, 224, 71, 0.15), transparent 25%),
                radial-gradient(circle at top right, rgba(45, 212, 191, 0.12), transparent 30%),
                linear-gradient(180deg, #0f172a 0%, #152238 45%, #1e293b 100%);
            color: #f8fafc;
        }
        .block-container {
            max-width: 1120px;
            padding-top: 1.6rem;
            padding-bottom: 2.5rem;
        }
        .hero {
            border-radius: 28px;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.92), rgba(15, 23, 42, 0.82));
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.8rem;
            color: #fff7ed;
        }
        .hero p {
            margin-top: 0.7rem;
            color: #dbeafe;
            font-size: 1.02rem;
            max-width: 750px;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }
        .pill {
            padding: 0.42rem 0.82rem;
            border-radius: 999px;
            background: rgba(251, 191, 36, 0.12);
            border: 1px solid rgba(251, 191, 36, 0.25);
            color: #fde68a;
            font-size: 0.9rem;
        }
        .panel {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        }
        .metric-card {
            border-radius: 20px;
            padding: 1rem;
            background: linear-gradient(180deg, rgba(30,41,59,0.92), rgba(15,23,42,0.85));
            border: 1px solid rgba(148, 163, 184, 0.15);
            min-height: 110px;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.88rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-value {
            color: #fef3c7;
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.35rem;
        }
        .metric-sub {
            color: #cbd5e1;
            font-size: 0.92rem;
            margin-top: 0.18rem;
        }
        .cow-card {
            background: linear-gradient(180deg, rgba(22, 30, 46, 0.95), rgba(15, 23, 42, 0.82));
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 0.85rem;
        }
        .cow-name {
            font-size: 1.12rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .cow-meta {
            color: #cbd5e1;
            font-size: 0.92rem;
        }
        .barn-log {
            padding: 0.9rem 1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.12);
            color: #dbeafe;
            margin-bottom: 0.55rem;
        }
        .tip {
            margin-top: 0.9rem;
            padding: 0.85rem 1rem;
            border-radius: 16px;
            background: rgba(16, 185, 129, 0.09);
            border: 1px solid rgba(52, 211, 153, 0.22);
            color: #d1fae5;
        }
        .stButton > button {
            background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
            color: #0f172a !important;
            border: 1px solid rgba(148, 163, 184, 0.5) !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.22) !important;
        }
        .stButton > button:hover {
            background: linear-gradient(180deg, #ffffff 0%, #dbeafe 100%) !important;
            color: #020617 !important;
            border-color: rgba(96, 165, 250, 0.6) !important;
        }
        .stButton > button:focus,
        .stButton > button:focus-visible {
            color: #020617 !important;
            outline: none !important;
            box-shadow: 0 0 0 0.2rem rgba(96, 165, 250, 0.28) !important;
        }
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: #0f172a !important;
            font-weight: 700 !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #fbbf24 0%, #f59e0b 100%) !important;
            color: #1f2937 !important;
            border: 1px solid rgba(245, 158, 11, 0.7) !important;
        }
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span,
        .stButton > button[kind="primary"] div {
            color: #1f2937 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

COW_NAMES = [
    "Bessie", "Mochi", "Daisy", "Nugget", "Pepper", "Luna", "Butters", "Clover",
    "Pudding", "Maple", "Junebug", "Truffle", "Hazel", "Toffee", "Mabel", "Sprout",
]
MOODS = ["sleepy", "bouncy", "dramatic", "focused", "chaotic", "delighted"]
EVENTS = [
    ("A local café placed a surprise milk order.", 18),
    ("One of the cows kicked over a bucket in protest.", -10),
    ("A golden patch of clover boosted the herd's mood.", 12),
    ("The moon glowed weirdly and milk output got extra frothy.", 15),
    ("A raccoon snuck into the barn and stole snacks.", -8),
    ("Tourists stopped by and tipped for selfies with the cows.", 14),
]
UPGRADES = {
    "Comfy Barn": {"cost": 60, "effect": "Cows gain +1 happiness each turn."},
    "Turbo Milker": {"cost": 90, "effect": "Milking yields +6 extra milk."},
    "Fancy Feed": {"cost": 45, "effect": "Feeding restores +2 extra happiness."},
}


def init_game():
    if "game" in st.session_state:
        return
    st.session_state.game = {
        "day": 1,
        "coins": 120,
        "milk": 20,
        "hay": 12,
        "score": 0,
        "upgrades": [],
        "log": ["Welcome to Moonmilk Ranch. The barn smells like ambition and hay."],
        "cows": [
            {"name": "Bessie", "happiness": 7, "energy": 6, "milk_ready": 8, "mood": "sleepy"},
            {"name": "Mochi", "happiness": 8, "energy": 7, "milk_ready": 6, "mood": "bouncy"},
            {"name": "Daisy", "happiness": 6, "energy": 8, "milk_ready": 7, "mood": "dramatic"},
        ],
    }


def add_log(message: str):
    st.session_state.game["log"].insert(0, message)
    st.session_state.game["log"] = st.session_state.game["log"][:8]


def next_day():
    game = st.session_state.game
    game["day"] += 1
    bonus_happiness = 1 if "Comfy Barn" in game["upgrades"] else 0

    for cow in game["cows"]:
        cow["energy"] = max(2, min(10, cow["energy"] + random.randint(-1, 2)))
        cow["happiness"] = max(1, min(10, cow["happiness"] + random.randint(-1, 1) + bonus_happiness))
        cow["milk_ready"] = max(2, min(12, cow["milk_ready"] + random.randint(1, 3)))
        cow["mood"] = random.choice(MOODS)

    event_text, coin_delta = random.choice(EVENTS)
    game["coins"] = max(0, game["coins"] + coin_delta)
    add_log(f"Day {game['day']}: {event_text} ({coin_delta:+} coins)")


init_game()
game = st.session_state.game

st.markdown(
    """
    <div class="hero">
        <h1>🐮 Moonmilk Ranch</h1>
        <p>
            Run a tiny, slightly ridiculous dairy empire. Keep your cows happy, manage hay,
            milk the herd, buy upgrades, and see how absurdly prosperous your ranch becomes.
        </p>
        <div class="pill-row">
            <div class="pill">Farm management</div>
            <div class="pill">Cow moods</div>
            <div class="pill">Milk economy</div>
            <div class="pill">Tiny chaos</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5 = st.columns(5)
metrics = [
    ("Day", game["day"], "Another sunrise over the barn"),
    ("Coins", game["coins"], "Spend these on supplies and upgrades"),
    ("Milk", game["milk"], "Freshly collected inventory"),
    ("Hay", game["hay"], "Cow-approved snacks on hand"),
    ("Score", game["score"], "Your ranching legend"),
]
for col, (label, value, sub) in zip([m1, m2, m3, m4, m5], metrics):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

left, right = st.columns([1.2, 0.95], gap="large")

with left:
    st.markdown("## Herd status")
    for idx, cow in enumerate(game["cows"]):
        st.markdown('<div class="cow-card">', unsafe_allow_html=True)
        st.markdown(
            f"<div class='cow-name'>{cow['name']} <span style='font-size:0.95rem'>· {cow['mood']}</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='cow-meta'>Happiness: {cow['happiness']}/10 · Energy: {cow['energy']}/10 · Milk ready: {cow['milk_ready']}</div>",
            unsafe_allow_html=True,
        )
        st.progress(cow["happiness"] / 10, text=f"{cow['name']} happiness")
        st.progress(cow["energy"] / 10, text=f"{cow['name']} energy")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## Barn actions")
    a1, a2, a3, a4 = st.columns(4)

    with a1:
        if st.button("🌾 Feed herd", use_container_width=True):
            if game["hay"] < len(game["cows"]):
                add_log("Not enough hay. The cows stared at you like disappointed landlords.")
            else:
                bonus = 2 if "Fancy Feed" in game["upgrades"] else 0
                game["hay"] -= len(game["cows"])
                for cow in game["cows"]:
                    cow["happiness"] = min(10, cow["happiness"] + 2 + bonus)
                    cow["energy"] = min(10, cow["energy"] + 1)
                game["score"] += 5
                add_log("You fed the herd. Spirits rose. Chewing sounds became majestic.")

    with a2:
        if st.button("🥛 Milk cows", use_container_width=True):
            milk_gain = 0
            bonus = 6 if "Turbo Milker" in game["upgrades"] else 0
            for cow in game["cows"]:
                collected = max(0, int(cow["milk_ready"] * (0.6 + cow["happiness"] / 20)))
                milk_gain += collected
                cow["milk_ready"] = max(1, cow["milk_ready"] - collected // 2)
                cow["energy"] = max(1, cow["energy"] - 1)
            milk_gain += bonus
            game["milk"] += milk_gain
            game["score"] += milk_gain
            add_log(f"You milked the herd and collected {milk_gain} units. The buckets are thriving.")

    with a3:
        if st.button("🛒 Sell milk", use_container_width=True):
            if game["milk"] < 8:
                add_log("You need at least 8 milk to make a proper market run.")
            else:
                sold = min(game["milk"], 20)
                price = random.randint(3, 5)
                earnings = sold * price
                game["milk"] -= sold
                game["coins"] += earnings
                game["score"] += earnings // 2
                add_log(f"You sold {sold} milk for {earnings} coins at {price} each. Capitalism, but pastoral.")

    with a4:
        if st.button("🌙 Next day", use_container_width=True):
            next_day()

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("## Supplies and upgrades")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Buy 5 hay · 15 coins", use_container_width=True):
            if game["coins"] >= 15:
                game["coins"] -= 15
                game["hay"] += 5
                add_log("You bought 5 hay. The barn now feels responsibly stocked.")
            else:
                add_log("Not enough coins for hay. The feed store clerk looked unimpressed.")

    with c2:
        if st.button("Adopt mystery cow · 80 coins", use_container_width=True):
            if game["coins"] >= 80:
                game["coins"] -= 80
                used_names = {cow["name"] for cow in game["cows"]}
                choices = [name for name in COW_NAMES if name not in used_names] or COW_NAMES
                new_name = random.choice(choices)
                game["cows"].append(
                    {
                        "name": new_name,
                        "happiness": random.randint(5, 9),
                        "energy": random.randint(5, 9),
                        "milk_ready": random.randint(4, 8),
                        "mood": random.choice(MOODS),
                    }
                )
                game["score"] += 20
                add_log(f"A new cow named {new_name} joined the ranch. Morale and hoof traffic increased.")
            else:
                add_log("Not enough coins to adopt a new cow yet.")

    st.markdown("### Upgrades")
    for name, details in UPGRADES.items():
        owned = name in game["upgrades"]
        col_a, col_b = st.columns([1.8, 0.9])
        with col_a:
            st.markdown(f"**{name}**  ")
            st.caption(f"{details['effect']} Cost: {details['cost']} coins.")
        with col_b:
            if owned:
                st.success("Owned")
            else:
                if st.button(f"Buy {name}", key=f"buy_{name}", use_container_width=True):
                    if game["coins"] >= details["cost"]:
                        game["coins"] -= details["cost"]
                        game["upgrades"].append(name)
                        game["score"] += 15
                        add_log(f"Upgrade unlocked: {name}. The ranch feels suspiciously professional.")
                    else:
                        add_log(f"Not enough coins for {name}.")

    st.markdown("### Barn gossip")
    for item in game["log"][:6]:
        st.markdown(f"<div class='barn-log'>{item}</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="tip">
            <strong>How to win:</strong> keep the herd happy, milk often, sell at good moments,
            and stack upgrades before your little dairy kingdom descends into beautiful nonsense.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("## Ranch goals")
goal1, goal2, goal3 = st.columns(3)
with goal1:
    st.checkbox("Reach 250 coins", value=game["coins"] >= 250, disabled=True)
with goal2:
    st.checkbox("Own 5 cows", value=len(game["cows"]) >= 5, disabled=True)
with goal3:
    st.checkbox("Score 500 points", value=game["score"] >= 500, disabled=True)

if game["coins"] >= 250 and len(game["cows"]) >= 5 and game["score"] >= 500:
    st.success("You built a thriving moonlit milk empire. Frankly, the cows expect a statue.")

with st.expander("Restart game"):
    if st.button("Reset Moonmilk Ranch", type="primary"):
        del st.session_state["game"]
        st.rerun()
