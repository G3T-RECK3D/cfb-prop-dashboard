import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. --- APP INITIALIZATION & SPORTSBOOK STYLING ---
st.set_page_config(page_title="CFB Prop Analyzer", layout="wide", page_icon="🏈")

# Inject Custom CSS to give the app a clean, cohesive sports platform theme
st.markdown("""
    <style>
        .reportview-container { background: #0f172a; }
        div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #f8fafc; }
        div[data-testid="stMetricLabel"] { font-size: 14px; color: #94a3b8; }
        .stSelectbox label, .stSlider label { font-weight: bold !important; color: #f1f5f9 !important; }
        h1, h2, h3 { color: #f1f5f9 !important; font-weight: 700 !important; }
        hr { border-top: 1px solid #334155 !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🏈 College Football Player Prop Co-Pilot")
st.markdown("##### *Advanced Historical Analysis & Fair Value Odds Engine*")
st.markdown("---")

# Secure connection setup to your live server database
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
# Using your verified live anon key token
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- HELPER FUNCTION: PERCENTAGE TO AMERICAN ODDS ---
def pct_to_american_odds(percentage):
    if percentage >= 100: return "-10000"
    if percentage <= 0: return "+10000"
    if percentage > 50:
        odds = int(-((percentage) / (100 - percentage)) * 100)
        return f"{odds}"
    else:
        odds = int(((100 - percentage) / percentage) * 100)
        return f"+{odds}"

# --- PROP MARKET DICTIONARY STRUCTURE ---
PROP_MARKETS = {
    "Passing Yards":   {"col": "pass_yards", "max": 500.0, "default": 249.5, "step": 1.0, "unit": "Yds"},
    "Passing TDs":     {"col": "pass_tds",   "max": 6.0,   "default": 1.5,   "step": 0.5, "unit": "TDs"},
    "Rushing Yards":   {"col": "rush_yards", "max": 250.0, "default": 79.5,  "step": 1.0, "unit": "Yds"},
    "Rushing TDs":     {"col": "rush_tds",   "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Receiving Yards": {"col": "rec_yards",  "max": 200.0, "default": 59.5,  "step": 1.0, "unit": "Yds"},
    "Receptions":      {"col": "receptions", "max": 12.0,  "default": 4.5,   "step": 0.5, "unit": "Rec"}
}

try:
    # 2. --- DATA ACQUISITION & INTEGRATION ---
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("⚠️ Connected to your database server, but your table appears to be empty! Head back to your notebook to inject initial data records.")
    else:
        # Fill missing statistical values with 0
        for m in PROP_MARKETS.values():
            if m["col"] in df.columns:
                df[m["col"]] = df[m["col"]].fillna(0)

        # 3. --- SIDEBAR CONTROLS ---
        st.sidebar.markdown("### 🎯 Filter Settings")
        
        available_players = sorted(df["player_name"].unique())
        selected_player = st.sidebar.selectbox(
            "Search / Select Player", 
            available_players,
            index=0
        )
        
        selected_market_name = st.sidebar.selectbox(
            "Select Prop Market",
            list(PROP_MARKETS.keys()),
            index=0
        )

        market_info = PROP_MARKETS[selected_market_name]
        stat_col = market_info["col"]

        # Intelligent Slider Configuration based on the chosen prop category
        prop_line = st.sidebar.slider(
            f"Set Prop Line Threshold",
            min_value=0.0,
            max_value=market_info["max"],
            value=market_info["default"],
            step=market_info["step"]
        )

        # Isolate target player entries sorted chronologically
        player_df = df[df["player_name"] == selected_player].sort_values(by="week")
        
        # 4. --- ADVANCED ANALYTICAL CALCULATIONS ---
        total_games = len(player_df)
        avg_stat = player_df[stat_col].mean() if total_games > 0 else 0
        median_stat = player_df[stat_col].median() if total_games > 0 else 0
        
        overs = player_df[player_df[stat_col] > prop_line]
        over_count = len(overs)
        under_count = total_games - over_count
        
        over_pct = (over_count / total_games * 100) if total_games > 0 else 0
        under_pct = (under_count / total_games * 100) if total_games > 0 else 0
        
        fair_over_odds = pct_to_american_odds(over_pct)
        fair_under_odds = pct_to_american_odds(under_pct)
        
        # 5. --- SUMMARY METRIC SCORECARDS RENDER ---
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Games Documented", f"{total_games}")
        with c2: st.metric("Season Mean/Average", f"{avg_stat:.1f} {market_info['unit']}")
        with c3: st.metric("Season Median (Mid)", f"{median_stat:.1f} {market_info['unit']}")
        with c4: st.metric("OVER Win Clip 📈", f"{over_pct:.1f}%", delta=f"{over_count} Matches")
        
        st.markdown("---")
        
        # 6. --- FAIR VALUE IMPLIED ODDS GRID ---
        st.subheader(f"💸 Fair Value Betting Odd Projections: {selected_market_name}")
        st.markdown("*Compare these model prices to sportsbook odds lines. If a sportsbook offers better numbers (+ value), you have found an expected advantage.*")
        
        col_odds1, col_odds2 = st.columns(2)
        with col_odds1:
            st.markdown(f"#### 📈 Target Over: **{prop_line} {market_info['unit']}**")
            st.metric(label="Model Implied Price", value=fair_over_odds, delta=f"Cleared line {over_count} times")
        with col_odds2:
            st.markdown(f"#### 📉 Target Under: **{prop_line} {market_info['unit']}**")
            st.metric(label="Model Implied Price", value=fair_under_odds, delta=f"Stayed under {under_count} times")
            
        st.markdown("---")
        
        # 7. --- VISUAL BAR CHART CHARTING ---
        st.subheader(f"📊 Historical Game-Log Breakdown: {selected_market_name}")
        player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")
        
        fig = px.bar(
            player_df, 
            x="opponent", 
            y=stat_col, 
            color="Result",
            color_discrete_map={"🟢 OVER": "#2ecc71", "🔴 UNDER": "#e74c3c"}, 
            text=stat_col,
            labels={stat_col: selected_market_name, "opponent": "Opponent Team"}
        )
        
        # Add visual reference benchmark cutoff line across chart frame
        fig.add_hline(y=prop_line, line_dash="dash", line_color="#cbd5e1", annotation_text=f"Line: {prop_line}")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#f1f5f9",
            legend_title_text="Game Outcome"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 8. --- SPREADSHEET DATAFRAME VIEW ---
        st.subheader("📄 Filtered Database Records")
        show_cols = [c for c in ["season", "week", "opponent", stat_col] if c in player_df.columns]
        st.dataframe(player_df[show_cols].style.format({stat_col: "{:.1f}"}), use_container_width=True)

except Exception as e:
    st.error("❌ The dashboard server encountered a structural obstacle handshaking with your database framework.")
    st.code(e)
