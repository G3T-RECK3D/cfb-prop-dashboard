import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. --- BRANDING DICTIONARY MAP ---
# Maps specific programs to their official HEX colors and clean high-res logo vectors
TEAM_BRANDING = {
    "Alabama": {"primary": "#9E1B32", "accent": "#FFFFFF", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Georgia": {"primary": "#BA0C2F", "accent": "#000000", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Texas": {"primary": "#BF5700", "accent": "#333333", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Ohio State": {"primary": "#BB0000", "accent": "#666666", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Oregon": {"primary": "#154734", "accent": "#FEE123", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Penn State": {"primary": "#041E42", "accent": "#FFFFFF", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Miami": {"primary": "#F47321", "accent": "#005030", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Clemson": {"primary": "#F56600", "accent": "#522D80", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Tennessee": {"primary": "#FF8200", "accent": "#58595B", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "LSU": {"primary": "#582C83", "accent": "#FDD023", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Ole Miss": {"primary": "#CE1126", "accent": "#006BB6", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Colorado": {"primary": "#CFB87C", "accent": "#000000", "text": "#000000", "logo": "https://espncdn.com"},
    "Boise State": {"primary": "#0033A0", "accent": "#FF671F", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "Notre Dame": {"primary": "#0C2340", "accent": "#C99700", "text": "#FFFFFF", "logo": "https://espncdn.com"},
    "USC": {"primary": "#990000", "accent": "#FFCC00", "text": "#FFFFFF", "logo": "https://espncdn.com"}
}
DEFAULT_BRAND = {"primary": "#1e293b", "accent": "#334155", "text": "#f8fafc", "logo": "https://espncdn.com"}

# Secure connection setup to your live server database
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
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

PROP_MARKETS = {
    "Passing Yards":   {"col": "pass_yards", "max": 500.0, "default": 249.5, "step": 1.0, "unit": "Yds"},
    "Passing TDs":     {"col": "pass_tds",   "max": 6.0,   "default": 1.5,   "step": 0.5, "unit": "TDs"},
    "Rushing Yards":   {"col": "rush_yards", "max": 250.0, "default": 79.5,  "step": 1.0, "unit": "Yds"},
    "Rushing TDs":     {"col": "rush_tds",   "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Receiving Yards": {"col": "rec_yards",  "max": 200.0, "default": 59.5,  "step": 1.0, "unit": "Yds"},
    "Receptions":      {"col": "receptions", "max": 12.0,  "default": 4.5,   "step": 0.5, "unit": "Rec"}
}

try:
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("⚠️ Database table is empty.")
    else:
        # Fill missing values with 0
        for m in PROP_MARKETS.values():
            if m["col"] in df.columns:
                df[m["col"]] = df[m["col"]].fillna(0)

        # 2. --- SIDEBAR CONTROLS ---
        st.sidebar.markdown("### 🎯 Filter Settings")
        available_players = sorted(df["player_name"].unique())
        selected_player = st.sidebar.selectbox("Search / Select Player", available_players, index=0)
        
        selected_market_name = st.sidebar.selectbox("Select Prop Market", list(PROP_MARKETS.keys()), index=0)
        market_info = PROP_MARKETS[selected_market_name]
        stat_col = market_info["col"]

        prop_line = st.sidebar.slider(f"Set Prop Line Threshold", min_value=0.0, max_value=market_info["max"], value=market_info["default"], step=market_info["step"])

        # Isolate player data
        player_df = df[df["player_name"] == selected_player].sort_values(by="week")
        
        # 3. --- DYNAMIC BRANDING EXTRACTION ---
        player_team = player_df["team"].iloc[0] if not player_df.empty and "team" in player_df.columns else "Unknown"
        brand = TEAM_BRANDING.get(player_team, DEFAULT_BRAND)

        # Inject Branded CSS based on selected player's school
        st.markdown(f"""
            <style>
                .reportview-container {{ background: #0f172a; }}
                div[data-testid="stMetricValue"] {{ color: {brand['primary']} !important; font-size: 36px; font-weight: 800; }}
                .branded-header {{ background-color: {brand['primary']}; color: {brand['text']}; padding: 20px; border-radius: 10px; margin-bottom: 25px; }}
            </style>
        """, unsafe_allow_html=True)

        # 4. --- BRANDED TOP BANNER HEADER ---
        col_logo, col_title = st.columns([1, 5])
        with col_logo:
            st.image(brand["logo"], width=110)
        with col_title:
            st.markdown(f"""
                <div class="branded-header">
                    <h1 style='margin:0; color:{brand['text']} !important;'>{selected_player.upper()}</h1>
                    <p style='margin:0; font-size:16px; opacity:0.9;'>Primary Program: {player_team} | Position Profile</p>
                </div>
            """, unsafe_allow_html=True)

        # Math Analytics
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
        
        # Metrics Display
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Games Documented", f"{total_games}")
        with c2: st.metric("Season Average", f"{avg_stat:.1f} {market_info['unit']}")
        with c3: st.metric("Season Median", f"{median_stat:.1f} {market_info['unit']}")
        with c4: st.metric("OVER Win Clip 📈", f"{over_pct:.1f}%", delta=f"{over_count} Matches")
        
        st.markdown("---")
        
        # Fair Value Projections
        st.subheader(f"💸 Fair Value Implied Odds Calculation: {selected_market_name}")
        col_odds1, col_odds2 = st.columns(2)
        with col_odds1:
            st.markdown(f"#### 📈 Target Over: **{prop_line} {market_info['unit']}**")
            st.metric(label="Model Implied Price", value=fair_over_odds)
        with col_odds2:
            st.markdown(f"#### 📉 Target Under: **{prop_line} {market_info['unit']}**")
            st.metric(label="Model Implied Price", value=fair_under_odds)
            
        st.markdown("---")
        
        # Branded Plotly Chart
        st.subheader(f"📊 Historical Game Breakdown: {selected_market_name}")
        player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")
        
        # Custom color map where the accent color represents clearing the benchmark
        fig = px.bar(
            player_df, x="opponent", y=stat_col, color="Result",
            color_discrete_map={"🟢 OVER": brand["primary"], "🔴 UNDER": "#64748b"}, 
            text=stat_col, labels={stat_col: selected_market_name, "opponent": "Opponent"}
        )
        fig.add_hline(y=prop_line, line_dash="dash", line_color="#cbd5e1")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
        st.plotly_chart(fig, use_container_width=True)
        
        # Data Grid Slice
        st.subheader("📄 Filtered Database Records")
        show_cols = [c for c in ["season", "week", "opponent", stat_col] if c in player_df.columns]
        st.dataframe(player_df[show_cols], use_container_width=True)

except Exception as e:
    st.error("❌ The dashboard server encountered a structural obstacle handshaking with your database framework.")
    st.code(e)
