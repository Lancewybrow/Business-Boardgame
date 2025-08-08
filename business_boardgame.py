
import streamlit as st
import pandas as pd
import random
import math

st.set_page_config(page_title="Business Boardgame", layout="wide", initial_sidebar_state="collapsed")

# --- Utilities ---
def reset_game():
    st.session_state.update({
        "initialized": True,
        "month": 1,
        "position": 0,
        "cash": 0,
        "revenue": 0,
        "expenses": 0,
        "paper_profit": 0,
        "valuation": 0,
        "archetype": None,
        "investment": None,
        "strategy_cards": [],
        "mentor_tips": [],
        "history": [],
        "energy": 50,  # for Hustler momentum
        "streak": 0,
        "unlocked": {"Strategic Thinker": True, "Hustler": True},
    })

def format_currency(x):
    return f"£{x:,.0f}"

# --- Tile definitions (60 months / tiles) ---
tile_templates = [
    {"type":"Revenue", "title":"Client Win", "desc":"Sign a new client, steady revenue boost."},
    {"type":"Revenue", "title":"Upsell", "desc":"Sell extra service to current client."},
    {"type":"Expense", "title":"Tax Bill", "desc":"A tax or VAT bill due this month."},
    {"type":"Expense", "title":"Unexpected Repair", "desc":"Equipment or platform cost."},
    {"type":"Strategy", "title":"Strategy Opportunity", "desc":"Choose a small strategic move."},
    {"type":"Mentor", "title":"Mentor Insight", "desc":"An insight is unlocked and added to Mentor Board."},
    {"type":"Investment", "title":"Asset Purchase", "desc":"Buy something that may generate long-term cash."},
    {"type":"Event", "title":"Market Event", "desc":"A random positive or negative market event."},
]

# Build a fixed board of 60 tiles with a probabilistic mix
def build_board(seed=42):
    random.seed(seed)
    board = []
    for i in range(60):
        t = random.choices(tile_templates, weights=[25,20,12,8,10,12,8,5])[0]
        tile = t.copy()
        tile["index"] = i+1
        board.append(tile)
    return board

# --- Init session state ---
if "initialized" not in st.session_state:
    reset_game()

board = build_board()

# --- Top: Setup / Archetype / Investment ---
with st.container():
    st.markdown("<h1 style='margin-bottom:6px'>🎲 Business Boardgame</h1>", unsafe_allow_html=True)
    cols = st.columns([1,1,1,1,1])
    with cols[0]:
        arche = st.selectbox("Choose Archetype", ["The Strategic Thinker","The Hustler","The Investor","The System Builder","The Creator"], index=0 if st.session_state["archetype"] is None else ["The Strategic Thinker","The Hustler","The Investor","The System Builder","The Creator"].index(st.session_state["archetype"]))
    with cols[1]:
        inv = st.selectbox("Starting Investment", ["£0","£3,000","£5,000","£10,000","£20,000","£30,000+"], index=2 if st.session_state["investment"] is None else ["£0","£3,000","£5,000","£10,000","£20,000","£30,000+"].index(st.session_state["investment"]))
    with cols[2]:
        company = st.selectbox("Business Type", ["Sole Trader","Limited Company"])
    with cols[3]:
        if st.button("Start / Restart Game"):
            reset_game()
            st.session_state["archetype"] = arche
            st.session_state["investment"] = inv
            # set starting cash based on selection
            mapping = {"£0":0,"£3,000":3000,"£5,000":5000,"£10,000":10000,"£20,000":20000,"£30,000+":35000}
            st.session_state["cash"] = mapping.get(inv,0)
            st.session_state["valuation"] = st.session_state["cash"] * 2
            st.experimental_rerun()
    with cols[4]:
        st.markdown("**Game Length:** 60 months (turns)")

# --- Left column: Board visualization (mobile-first stacked layout) ---
left, right = st.columns([1,1.2])
with left:
    st.markdown("### 🗺️ Game Board (Click 'Advance Month' to roll)")
    # Display a simplified grid of 12 columns x 5 rows
    cols = st.columns(3)
    tiles_to_show = st.session_state["month"] if st.session_state["month"]<=60 else 60
    # render a compact board as a vertical list showing current month and nearby tiles
    view_start = max(0, st.session_state["position"]-4)
    view_end = min(60, st.session_state["position"]+5)
    for i in range(view_start, view_end):
        tile = board[i]
        is_current = (i == st.session_state["position"])
        if is_current:
            st.markdown(f"**▶ Month {tile['index']}: {tile['title']}** — {tile['desc']}")
        else:
            st.write(f"Month {tile['index']}: {tile['title']} — {tile['desc']}")

    st.markdown("---")
    st.markdown("#### 🎲 Turn Controls")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Advance Month (Roll Dice)"):
            # Advance position by 1 (one month per turn)
            if st.session_state["month"] < 61:
                st.session_state["position"] = min(59, st.session_state["position"] + 1)
                st.session_state["month"] += 1
                current_tile = board[st.session_state["position"]]
                # Resolve tile event
                outcome = resolve_tile(current_tile, st.session_state)
                st.session_state["history"].append(outcome)
                # small momentum effect
                if st.session_state["archetype"] == "The Hustler":
                    st.session_state["streak"] += 1 if random.random() > 0.2 else 0
                    if st.session_state["streak"]>=3:
                        st.session_state["energy"] = min(100, st.session_state["energy"]+10)
    with col2:
        if st.button("Take a Strategic Action"):
            st.session_state["strategy_cards"].append(random.choice(["80/20 Focus","Risk Reversal","Joint Venture Offer","Premium Upsell"]))
            st.success("You gained a Strategy Card!")
    with col3:
        if st.button("View Last Event"):
            if st.session_state["history"]:
                st.info(st.session_state["history"][-1])
            else:
                st.info("No events yet. Advance a month to start playing.")

# --- Right column: Dashboard & Mentor Board (tabs) ---
with right:
    tab = st.tabs(["Dashboard","Mentor Board","Strategy Cards","Monthly Log"])
    with tab[0]:
        st.markdown("### 📊 Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Month", f"{st.session_state['month']}/60")
        c2.metric("Cash in Bank", format_currency(st.session_state["cash"]))
        c3.metric("Valuation Estimate", format_currency(st.session_state["valuation"]))

        st.markdown("#### Cashflow Detail")
        df = pd.DataFrame([
            {"Metric":"Cash","Value":st.session_state["cash"]},
            {"Metric":"Revenue (sim)", "Value": st.session_state["revenue"]},
            {"Metric":"Expenses (sim)", "Value": st.session_state["expenses"]},
            {"Metric":"Paper Profit","Value": st.session_state["paper_profit"]},
        ])
        st.table(df)

        st.markdown("#### Archetype Strengths (Radar simplified)")
        strengths = {
            "Mindset": 60 if st.session_state["archetype"]=="The Hustler" else 40,
            "Strategy": 70 if st.session_state["archetype"]=="The Strategic Thinker" else 50,
            "Systems": 60 if st.session_state["archetype"]=="The System Builder" else 45,
            "Brand": 65 if st.session_state["archetype"]=="The Creator" else 45,
            "Investor": 70 if st.session_state["archetype"]=="The Investor" else 45,
        }
        st.write(strengths)

    with tab[1]:
        st.markdown("### 📘 Mentor Board")
        # Sample mentors and tips (anonymous)
        mentors = {
            "The Strategic Thinker": {
                "icon":"🧠","role":"Leverage, positioning, strategic advantage",
                "tips":[
                    "Look for partnerships that multiply reach without extra spend.",
                    "Create a premium offer for top clients to boost margins."
                ]
            },
            "The Hustler": {
                "icon":"🔥","role":"Momentum, energy, execution",
                "tips":[
                    "Small daily actions compound into big results—consistency matters.",
                    "Use quick imperfect launches to test offers fast."
                ]
            },
            "The Investor": {
                "icon":"💼","role":"Assets, cashflow, buying businesses",
                "tips":[
                    "Prioritise purchases that create recurring cashflow, not just status.",
                    "Keep a runway; never assume next month will be better."
                ]
            }
        }
        # Display mentor cards
        cols = st.columns(2)
        for i, (name, data) in enumerate(mentors.items()):
            with cols[i%2]:
                with st.expander(f"{data['icon']} {name} — {data['role']}", expanded=False):
                    for tip in data["tips"]:
                        st.write(f"- {tip}")

    with tab[2]:
        st.markdown("### 🃏 Strategy Cards")
        if st.session_state["strategy_cards"]:
            for i, c in enumerate(st.session_state["strategy_cards"]):
                st.info(f"{i+1}. {c}")
        else:
            st.write("No strategy cards yet. Take a Strategic Action to earn cards.")

    with tab[3]:
        st.markdown("### 🗂️ Monthly Log")
        if st.session_state["history"]:
            for ev in st.session_state["history"][-10:]:
                st.write(f"- {ev}")
        else:
            st.write("No history yet. Advance a month to start generating events.")

# --- Tile resolution logic ---
def resolve_tile(tile, state):
    """Apply effects of the tile to the session state and return a human-readable event string."""
    ttype = tile["type"]
    idx = tile["index"]
    outcome = ""
    # small simulated revenue/expense numbers
    if ttype == "Revenue":
        revenue = random.randint(500, 5000)
        state["revenue"] = revenue
        state["cash"] += revenue
        state["paper_profit"] += revenue
        outcome = f"Month {idx}: Revenue event (+{format_currency(revenue)})"
        # chance to unlock a mentor tip
        if random.random() < 0.15:
            tip = "New strategic option appears—consider a joint venture."
            state["mentor_tips"].append(tip)
            outcome += " — Mentor Insight unlocked."
    elif ttype == "Expense":
        expense = random.randint(300, 3500)
        state["expenses"] = expense
        state["cash"] -= expense
        state["paper_profit"] -= expense
        outcome = f"Month {idx}: Expense occurred (-{format_currency(expense)})"
    elif ttype == "Strategy":
        # give player choice: small win or long-term investment
        choice = random.choice(["Quick Win","Long Investment"])
        if choice == "Quick Win":
            gain = random.randint(400,2000)
            state["cash"] += gain
            outcome = f"Month {idx}: Strategy short-term win (+{format_currency(gain)})"
        else:
            invest = random.randint(800,3000)
            state["cash"] -= invest
            outcome = f"Month {idx}: Strategy long investment (-{format_currency(invest)})"
    elif ttype == "Mentor":
        tip = random.choice([
            "Increase perceived value by improving your offer structure.",
            "Focus on your top 20% of clients for faster growth.",
            "Experiment with pricing tiers to find premium buyers."
        ])
        state["mentor_tips"].append(tip)
        outcome = f"Month {idx}: Mentor Insight — {tip}"
    elif ttype == "Investment":
        cost = random.randint(1000,7000)
        # sometimes pays off later; immediate cash decrease
        state["cash"] -= cost
        state["valuation"] += int(cost * 1.2)
        outcome = f"Month {idx}: Bought asset (-{format_currency(cost)}), valuation up."
    elif ttype == "Event":
        r = random.random()
        if r < 0.4:
            gain = random.randint(500,6000)
            state["cash"] += gain
            outcome = f"Month {idx}: Positive market event (+{format_currency(gain)})"
        else:
            loss = random.randint(500,6000)
            state["cash"] -= loss
            outcome = f"Month {idx}: Negative market event (-{format_currency(loss)})"
    # Update valuation slightly based on cash and paper_profit
    state["valuation"] = max(0, int(state["cash"] * 2 + state["paper_profit"] * 5))
    # Simple bankruptcy check
    if state["cash"] < -10000:
        outcome += " | WARNING: Cash extremely negative. Consider resetting."
    return outcome
