import math
import random
import time

import streamlit as st

st.set_page_config(
    page_title="Idle Moo Empire",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

REFRESH_SECONDS = 1.0

st.markdown(
    f"""
    <meta http-equiv="refresh" content="{REFRESH_SECONDS}">
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(253, 224, 71, 0.22), transparent 24%),
                radial-gradient(circle at top right, rgba(34, 197, 94, 0.18), transparent 30%),
                linear-gradient(180deg, #d9f99d 0%, #86efac 30%, #4ade80 62%, #22c55e 100%);
            color: #1f2937;
        }
        .block-container {
            max-width: 1150px;
            padding-top: 1.4rem;
            padding-bottom: 2.8rem;
        }
        .hero {
            border-radius: 28px;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(254, 249, 195, 0.95), rgba(187, 247, 208, 0.92));
            border: 1px solid rgba(34, 197, 94, 0.25);
            box-shadow: 0 18px 60px rgba(34, 197, 94, 0.18);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2.9rem;
            color: #14532d;
        }
        .hero p {
            margin-top: 0.7rem;
            color: #166534;
            font-size: 1.02rem;
            max-width: 800px;
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
            background: rgba(254, 240, 138, 0.7);
            border: 1px solid rgba(234, 179, 8, 0.35);
            color: #854d0e;
            font-size: 0.9rem;
        }
        .panel {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(34, 197, 94, 0.18);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 14px 36px rgba(0,0,0,0.12);
        }
        .metric-card {
            border-radius: 20px;
            padding: 1rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.9), rgba(236,253,245,0.9));
            border: 1px solid rgba(34, 197, 94, 0.16);
            min-height: 112px;
        }
        .metric-label {
            color: #15803d;
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.09em;
        }
        .metric-value {
            color: #854d0e;
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.32rem;
        }
        .metric-sub {
            color: #166534;
            font-size: 0.92rem;
            margin-top: 0.15rem;
        }
        .cow-card, .upgrade-card, .log-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.88), rgba(240,253,244,0.92));
            border: 1px solid rgba(34, 197, 94, 0.14);
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        .section-title {
            color: #14532d;
            margin-bottom: 0.8rem;
        }
        .cow-name {
            font-size: 1.08rem;
            font-weight: 700;
            color: #14532d;
        }
        .cow-meta, .upgrade-meta {
            color: #166534;
            font-size: 0.92rem;
        }
        .barn-log {
            padding: 0.85rem 0.95rem;
            border-radius: 16px;
            background: rgba(254, 252, 232, 0.92);
            border: 1px solid rgba(234, 179, 8, 0.18);
            color: #365314;
            margin-bottom: 0.5rem;
        }
        .tip {
            margin-top: 0.9rem;
            padding: 0.85rem 1rem;
            border-radius: 16px;
            background: rgba(250, 204, 21, 0.12);
            border: 1px solid rgba(234, 179, 8, 0.25);
            color: #713f12;
        }
        .stButton > button {
            background: linear-gradient(180deg, #fef08a 0%, #facc15 100%) !important;
            color: #365314 !important;
            border: 1px solid rgba(234, 179, 8, 0.55) !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12) !important;
        }
        .stButton > button:hover {
            background: linear-gradient(180deg, #fde047 0%, #eab308 100%) !important;
            color: #365314 !important;
            border-color: rgba(132, 204, 22, 0.8) !important;
        }
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: #365314 !important;
            font-weight: 700 !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(180deg, #86efac 0%, #4ade80 100%) !important;
            color: #14532d !important;
            border: 1px solid rgba(34, 197, 94, 0.7) !important;
        }
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] span,
        .stButton > button[kind="primary"] div {
            color: #14532d !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

COW_NAMES = [
    "Bessie", "Mochi", "Daisy", "Maple", "Clover", "Pepper", "Truffle", "Toffee",
    "Pudding", "Sprout", "Mabel", "Hazel", "Junebug", "Butters", "Nugget", "Luna",
]
MOODS = ["sleepy", "content", "chaotic", "focused", "dramatic", "sparkly"]

UPGRADES = {
    "extra_stall": {
        "label": "Extra Stall",
        "base_cost": 25,
        "desc": "+1 cow capacity and +0.3 milk/sec.",
    },
    "auto_milker": {
        "label": "Auto-Milker",
        "base_cost": 18,
        "desc": "+2.4 milk/sec from early automation and score pressure.",
    },
    "premium_feed": {
        "label": "Premium Feed",
        "base_cost": 40,
        "desc": "+15% milk production.",
    },
    "barn_robot": {
        "label": "Barn Robot",
        "base_cost": 120,
        "desc": "+2.0 milk/sec and happier cows.",
    },
    "moon_silo": {
        "label": "Moon Silo",
        "base_cost": 220,
        "desc": "+35% milk production.",
    },
}


def format_num(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value/1_000:.2f}K"
    if value >= 100:
        return f"{value:.0f}"
    return f"{value:.1f}"


def next_upgrade_cost(key: str, level: int) -> int:
    base = UPGRADES[key]["base_cost"]
    return math.ceil(base * (1.55 ** level))


def add_log(message: str):
    game = st.session_state.game
    game["log"].insert(0, message)
    game["log"] = game["log"][:10]


def add_cow(auto: bool = False):
    game = st.session_state.game
    used = {cow["name"] for cow in game["cows"]}
    choices = [name for name in COW_NAMES if name not in used] or COW_NAMES
    name = random.choice(choices)
    game["cows"].append(
        {
            "name": name,
            "base_rate": round(random.uniform(0.7, 1.4), 2),
            "mood": random.choice(MOODS),
            "happiness": random.randint(5, 9),
        }
    )
    if auto:
        add_log(f"A new cow, {name}, wandered in and decided to stay.")
    else:
        add_log(f"You bought {name}. The herd immediately started judging your management style.")


def initial_game():
    return {
        "milk": 0.0,
        "coins": 20.0,
        "lifetime_milk": 0.0,
        "click_power": 1.0,
        "capacity": 4,
        "upgrades": {key: 0 for key in UPGRADES},
        "cows": [
            {"name": "Bessie", "base_rate": 1.0, "mood": "content", "happiness": 8},
            {"name": "Mochi", "base_rate": 0.9, "mood": "sleepy", "happiness": 7},
        ],
        "last_tick": time.time(),
        "log": ["Moonlight hits the barn roof. The idle milk empire begins."],
        "tick_count": 0,
        "theme_msg": "The herd is calm. Suspiciously calm.",
    }


def ensure_game():
    if "game" not in st.session_state:
        st.session_state.game = initial_game()


def milk_per_second() -> float:
    game = st.session_state.game
    herd_rate = sum(cow["base_rate"] * (0.65 + cow["happiness"] / 10) for cow in game["cows"])
    auto = game["upgrades"]["auto_milker"] * 2.4 + game["upgrades"]["barn_robot"] * 2.0
    multiplier = 1 + game["upgrades"]["premium_feed"] * 0.15 + game["upgrades"]["moon_silo"] * 0.35
    return (herd_rate + auto) * multiplier


def tick_game():
    game = st.session_state.game
    now = time.time()
    elapsed = max(0.0, min(now - game["last_tick"], 30.0))
    rate = milk_per_second()
    gained = elapsed * rate
    game["milk"] += gained
    game["lifetime_milk"] += gained
    game["last_tick"] = now
    game["tick_count"] += 1

    if game["tick_count"] % 8 == 0:
        for cow in game["cows"]:
            cow["happiness"] = max(3, min(10, cow["happiness"] + random.choice([-1, 0, 1])))
            cow["mood"] = random.choice(MOODS)
        mood_pool = [
            "A cow stared at the horizon like she understood the stock market.",
            "The milking pipes hummed like a tiny space station.",
            "Someone in the herd is clearly unionizing, but production is still up.",
            "A perfect patch of clover was discovered near the fence.",
        ]
        game["theme_msg"] = random.choice(mood_pool)

    extra_capacity = game["upgrades"]["extra_stall"]
    game["capacity"] = 4 + extra_capacity

    while len(game["cows"]) < min(game["capacity"], 2 + game["upgrades"]["extra_stall"]):
        add_cow(auto=True)


ensure_game()
tick_game()
game = st.session_state.game
rate = milk_per_second()
game_score = game["lifetime_milk"] + game["upgrades"]["auto_milker"] * 120 + game["upgrades"]["barn_robot"] * 220

st.markdown(
    """
    <div class="hero">
        <h1>🐄 Idle Moo Empire</h1>
        <p>
            Build a bright, cheerful dairy empire. Tap to milk, unlock the auto-milker almost
            immediately, expand the barn, stack upgrades, and watch your farm score climb on its own.
        </p>
        <div class="pill-row">
            <div class="pill">Idle game</div>
            <div class="pill">Passive milk income</div>
            <div class="pill">Cow upgrades</div>
            <div class="pill">Barn automation</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4, m5, m6 = st.columns(6)
metrics = [
    ("Milk", format_num(game["milk"]), "Current liquid glory"),
    ("Coins", format_num(game["coins"]), "Spend to scale the ranch"),
    ("Milk / sec", format_num(rate), "Passive production rate"),
    ("Farm score", format_num(game_score), "Your overall idle progress"),
    ("Cows", f"{len(game['cows'])}/{game['capacity']}", "Occupied stalls"),
    ("Lifetime milk", format_num(game["lifetime_milk"]), "All-time output"),
]
for col, (label, value, sub) in zip([m1, m2, m3, m4, m5, m6], metrics):
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

left, right = st.columns([1.1, 1.0], gap="large")

with left:
    st.markdown("## Milking floor")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f"**Barn status:** {game['theme_msg']}")
    st.caption(f"The farm loop updates automatically every {int(REFRESH_SECONDS)} second.")

    if st.button(f"🥛 Milk the herd manually (+{format_num(game['click_power'])})", use_container_width=True, type="primary"):
        game["milk"] += game["click_power"]
        game["lifetime_milk"] += game["click_power"]
        add_log("You did a hands-on milk run. The buckets salute you.")

    sell_cols = st.columns(3)
    with sell_cols[0]:
        if st.button("Sell 25 milk", use_container_width=True):
            if game["milk"] >= 25:
                game["milk"] -= 25
                game["coins"] += 15
                add_log("Sold 25 milk for 15 coins. A respectable moo-vement.")
            else:
                add_log("Not enough milk for that sale.")
    with sell_cols[1]:
        if st.button("Sell 100 milk", use_container_width=True):
            if game["milk"] >= 100:
                game["milk"] -= 100
                game["coins"] += 68
                add_log("Sold 100 milk in bulk for 68 coins. The market loves your cows.")
            else:
                add_log("You need 100 milk for the bulk buyer.")
    with sell_cols[2]:
        if st.button("Sell all milk", use_container_width=True):
            if game["milk"] >= 1:
                sold = game["milk"]
                earnings = sold * 0.62
                game["milk"] = 0
                game["coins"] += earnings
                add_log(f"Liquidated {format_num(sold)} milk for {format_num(earnings)} coins.")
            else:
                add_log("There is no milk to sell. The truck left empty.")

    st.markdown("### Herd")
    for cow in game["cows"]:
        st.markdown('<div class="cow-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='cow-name'>{cow['name']} · {cow['mood']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='cow-meta'>Base rate: {cow['base_rate']:.2f}/sec · Happiness: {cow['happiness']}/10 · Effective contribution: {cow['base_rate'] * (0.65 + cow['happiness'] / 10):.2f}/sec</div>",
            unsafe_allow_html=True,
        )
        st.progress(cow["happiness"] / 10, text=f"{cow['name']} happiness")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown("## Upgrades")
    for key, details in UPGRADES.items():
        level = game["upgrades"][key]
        cost = next_upgrade_cost(key, level)
        st.markdown('<div class="upgrade-card">', unsafe_allow_html=True)
        st.markdown(f"**{details['label']}** · Level {level}")
        st.markdown(f"<div class='upgrade-meta'>{details['desc']}</div>", unsafe_allow_html=True)
        u1, u2 = st.columns([1.6, 0.9])
        with u1:
            st.caption(f"Next cost: {cost} coins")
        with u2:
            if st.button(f"Buy {details['label']}", key=f"buy_{key}", use_container_width=True):
                if game["coins"] >= cost:
                    game["coins"] -= cost
                    game["upgrades"][key] += 1
                    if key == "extra_stall" and len(game["cows"]) < game["capacity"]:
                        add_cow(auto=True)
                    if key == "premium_feed":
                        for cow in game["cows"]:
                            cow["happiness"] = min(10, cow["happiness"] + 1)
                    if key == "barn_robot":
                        game["click_power"] += 1.5
                    if key == "auto_milker":
                        add_log("The auto-milker clanks to life. Your farm score starts sprinting upward.")
                    else:
                        add_log(f"Purchased {details['label']} level {game['upgrades'][key]}.")
                else:
                    add_log(f"Need {cost} coins for {details['label']}.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## Expansion")
    exp1, exp2 = st.columns(2)
    next_cow_cost = 35 + (len(game["cows"]) - 2) * 18
    with exp1:
        if st.button(f"Buy cow · {next_cow_cost} coins", use_container_width=True):
            if len(game["cows"]) >= game["capacity"]:
                add_log("No room in the barn. Buy Extra Stall first.")
            elif game["coins"] >= next_cow_cost:
                game["coins"] -= next_cow_cost
                add_cow(auto=False)
            else:
                add_log("Not enough coins for another cow.")
    with exp2:
        click_upgrade_cost = int(20 + game["click_power"] * 18)
        if st.button(f"Upgrade bucket hands · {click_upgrade_cost} coins", use_container_width=True):
            if game["coins"] >= click_upgrade_cost:
                game["coins"] -= click_upgrade_cost
                game["click_power"] += 1
                add_log(f"Manual milking improved. Click power is now {game['click_power']:.1f}.")
            else:
                add_log("Your arms remain ordinary for now.")

    st.markdown("## Barn log")
    st.markdown('<div class="log-card">', unsafe_allow_html=True)
    for item in game["log"]:
        st.markdown(f"<div class='barn-log'>{item}</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="tip">
            <strong>Idle strategy:</strong> grab the early auto-milker first, then add stall capacity,
            then scale with multipliers. Happy cows and lazy automation make the score explode.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("## Milestones")
milestone_cols = st.columns(4)
milestones = [
    ("100 milk", game["lifetime_milk"] >= 100),
    ("250 coins", game["coins"] >= 250),
    ("6 cows", len(game["cows"]) >= 6),
    ("50 milk/sec", rate >= 50),
]
for col, (label, reached) in zip(milestone_cols, milestones):
    with col:
        st.checkbox(label, value=reached, disabled=True)

with st.expander("Game controls"):
    ctrl1, ctrl2 = st.columns(2)
    with ctrl1:
        if st.button("Refresh idle progress", use_container_width=True):
            st.rerun()
    with ctrl2:
        if st.button("Reset empire", type="primary", use_container_width=True):
            del st.session_state["game"]
            st.rerun()
