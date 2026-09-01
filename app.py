import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. --- APP INITIALIZATION & STYLING ---
st.set_page_config(page_title="CFB Prop Analyzer", layout="wide", page_icon="🏈")

st.title("🏈 College Football Player Prop Co-Pilot")
st.markdown("##### *Advanced Historical Analysis & Fair Value Odds Engine*")
st.markdown("---")

# Secure connection setup
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# BRANDING DICTIONARY MAP
TEAM_BRANDING = {
    "Alabama": {"primary": "#9E1B32", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Georgia": {"primary": "#BA0C2F", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Texas": {"primary": "#BF5700", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Ohio State": {"primary": "#BB0000", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Oregon": {"primary": "#154734", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Penn State": {"primary": "#041E42", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Miami": {"primary": "#F47321", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Clemson": {"primary": "#F56600", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Tennessee": {"primary": "#FF8200", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "LSU": {"primary": "#582C83", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Ole Miss": {"primary": "#CE1126", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Colorado": {"primary": "#CFB87C", "text": "#000000", "logo": "https://espncdn.com"},
    "Boise State": {"primary": "#0033A0", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Notre Dame": {"primary": "#0C2340", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "USC": {"primary": "#990000", "text": "#FFFFFF", "logo": "https://espncdn.com"}
}
DEFAULT_BRAND = {"primary": "#1e293b", "text": "#f8fafc", "logo": "https://espncdn.com"}

# HELPER FUNCTION: PERCENTAGE TO AMERICAN ODDS
def pct_to_american_odds(percentage):
    if percentage >= 100: return "-10000"
    if percentage <= 0: return "+10000"
    if percentage > 50:
        odds = int(-((percentage) / (100 - percentage)) * 100)
        return f"{odds}"
    else:
        odds = int(((100 - percentage) / percentage) * 100)
        return f"+{odds}"

PROP_MARKETS = {
    "Passing Yards":   {"col": "pass_yards", "max": 500.0, "default": 249.5, "step": 1.0, "unit": "Yds"},
    "Passing TDs":     {"col": "pass_tds",   "max": 6.0,   "default": 1.5,   "step": 0.5, "unit": "TDs"},
    "Rushing Yards":   {"col": "rush_yards", "max": 250.0, "default": 79.5,  "step": 1.0, "unit": "Yds"},
    "Rushing TDs":     {"col": "rush_tds",   "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Receiving Yards": {"col": "rec_yards",  "max": 200.0, "default": 59.5,  "step": 1.0, "unit": "Yds"},
    "Receptions":      {"col": "receptions", "max": 12.0,  "default": 4.5,   "step": 0.5, "unit": "Rec"}
}

try:
    # 2. --- RETRIEVE BASE ROWS ---
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("⚠️ Connected to your database server, but your table appears to be empty!")
    else:
        for m in PROP_MARKETS.values():
            if m["col"] in df.columns:
                df[m["col"]] = df[m["col"]].fillna(0)

        # 3. --- SIDEBAR CONTROLS ---
        st.sidebar.markdown("### 🎯 Filter Settings")
        
        # Step 1: Select Team first
        available_teams = sorted(df["team"].unique()) if "team" in df.columns else []
        selected_team = st.sidebar.selectbox("1️⃣ Select Program/Team", available_teams)
        
        # Step 2: Select Prop Market next
        selected_market_name = st.sidebar.selectbox("2️⃣ Select Prop Market", list(PROP_MARKETS.keys()))
        market_info = PROP_MARKETS[selected_market_name]
        stat_col = market_info["col"]

        # Step 3: DYNAMICALLY SORT AND FILTER PLAYERS BY STAT VOLUME
        filtered_team_df = df[df["team"] == selected_team]
        player_totals = filtered_team_df.groupby("player_name")[stat_col].sum().reset_index()
        
        # Remove players with 0 volume in this category
        player_totals = player_totals[player_totals[stat_col] > 0]
        player_totals = player_totals.sort_values(by=stat_col, ascending=False)
        ranked_players = player_totals["player_name"].tolist()

        if not ranked_players:
            st.sidebar.error(f"⚠️ No active players found with logged {selected_market_name} stats on this team.")
        else:
            # Map clean option formatting strings
            display_options = {}
            for _, r in player_totals.iterrows():
                display_options[r["player_name"]] = f"{r['player_name']} ({r[stat_col]:.0f} Total {market_info['unit']})"
            
            selected_player = st.sidebar.selectbox(
                "3️⃣ Select Player Profile", 
                ranked_players,
                format_func=lambda x: display_options.get(x, x)
            )

            prop_line = st.sidebar.slider("Sportsbook Line Mark", min_value=0.0, max_value=market_info["max"], value=market_info["default"], step=market_info["step"])

            # 4. --- BRANDED TOP BANNER HEADER ---
            brand = TEAM_BRANDING.get(selected_team, DEFAULT_BRAND)
            
            # Use a weighted structural ratio layout to isolate the logo container box cleanly
            col_logo, col_title = st.columns([1, 7])
            with col_logo:
                st.image(brand["logo"], width=80)
            with col_title:
                st.subheader(f"🏈 {selected_player.upper()}")
                st.markdown(f"*{selected_team} | Season 2025 Analytics Dataset*")


            # 5. --- ANALYTICS MATHEMATICS ---
            player_df = df[df["player_name"] == selected_player].sort_values(by="week")
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
            
            # Metrics Row Display
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Games Documented", f"{total_games}")
            c2.metric("Season Average", f"{avg_stat:.1f} {market_info['unit']}")
            c3.metric("Season Median", f"{median_stat:.1f} {market_info['unit']}")
            c4.metric("OVER Hit Rate 📈", f"{over_pct:.1f}%", delta=f"{over_count} Matches")
            
            st.markdown("---")
            
            # 6. --- FAIR VALUE PROJECTIONS ---
            st.subheader(f"💸 Fair Value Implied Odds Calculation: {selected_market_name}")
            col_odds1, col_odds2 = st.columns(2)
            with col_odds1:
                st.markdown(f"#### 📈 Target Over: **{prop_line} {market_info['unit']}**")
                st.metric(label="Model Implied Price", value=fair_over_odds)
            with col_odds2:
                st.markdown(f"#### 📉 Target Under: **{prop_line} {market_info['unit']}**")
                st.metric(label="Model Implied Price", value=fair_under_odds)
                
            st.markdown("---")
            
            # 7. --- CHARTING ---
            st.subheader(f"📊 Historical Game Breakdown: {selected_market_name}")
            player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")
            
            fig = px.bar(
                player_df, 
                x="opponent", 
                y=stat_col, 
                color="Result",
                color_discrete_map={"🟢 OVER": brand["primary"], "🔴 UNDER": "#475569"}, 
                text=stat_col, 
                labels={stat_col: selected_market_name, "opponent": "Opponent"}
            )
            fig.add_hline(y=prop_line, line_dash="dash", line_color="#cbd5e1")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
            st.plotly_chart(fig, use_container_width=True)
            
            # 8. --- SPREADSHEET TABLE ---
            st.subheader("📄 Filtered Database Records")
            show_cols = [c for c in ["season", "week", "opponent", stat_col] if c in player_df.columns]
            st.dataframe(player_df[show_cols], use_container_width=True)

except Exception as e:
    st.error("❌ The dashboard server encountered an obstacle connecting to your database.")
    st.code(e)
