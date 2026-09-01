import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. --- APP INITIALIZATION & THEME CONFIG ---
st.set_page_config(page_title="CFB Prop Analyzer", layout="wide", page_icon="🏈")

st.markdown("""
    <style>
        div[data-testid="stMetricValue"] { font-size: 36px; font-weight: bold; }
        .stSelectbox label, .stSlider label { font-weight: bold !important; color: #f1f5f9 !important; }
        h1, h2, h3, h4 { color: #f1f5f9 !important; font-weight: 700 !important; }
        hr { border-top: 1px solid #334155 !important; }
        .matchup-card { background-color: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #475569; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Secure connection setup
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# BRANDING DICTIONARY MAP
TEAM_BRANDING = {
    "Alabama": {"primary": "#9E1B32", "emoji": "🐘"}, "Georgia": {"primary": "#BA0C2F", "emoji": "🐶"},
    "Texas": {"primary": "#BF5700", "emoji": "🤘"}, "Ohio State": {"primary": "#BB0000", "emoji": "🌰"},
    "Oregon": {"primary": "#154734", "emoji": "🦆"}, "Penn State": {"primary": "#041E42", "emoji": "🦁"},
    "Miami": {"primary": "#F47321", "emoji": "🙌"}, "Clemson": {"primary": "#F56600", "emoji": "🐅"},
    "Tennessee": {"primary": "#FF8200", "emoji": "🍊"}, "LSU": {"primary": "#582C83", "emoji": "🐯"},
    "Ole Miss": {"primary": "#CE1126", "emoji": "🦈"}, "Colorado": {"primary": "#CFB87C", "emoji": "🦬"},
    "Boise State": {"primary": "#0033A0", "emoji": "🐴"}, "Notre Dame": {"primary": "#0C2340", "emoji": "🍀"},
    "USC": {"primary": "#990000", "emoji": "⚔️"}, "Stanford": {"primary": "#8C1515", "emoji": "🌲"},
    "Hawaii": {"primary": "#024731", "emoji": "🌈"}, "Iowa State": {"primary": "#C8102E", "emoji": "🌪️"},
    "Kansas State": {"primary": "#512888", "emoji": "😼"}, "Kansas": {"primary": "#0051BA", "emoji": "🐦"},
    "Fresno State": {"primary": "#D31145", "emoji": "🐾"}, "UNLV": {"primary": "#CF142B", "emoji": "⚔️"},
    "Sam Houston": {"primary": "#F05A28", "emoji": "🍊"}, "Western Kentucky": {"primary": "#E31837", "emoji": "🔴"},
    "Eastern Michigan": {"primary": "#006633", "emoji": "🦅"}, "New Mexico State": {"primary": "#862633", "emoji": "🤠"},
    "San Jose State": {"primary": "#0055A5", "emoji": "⚔️"}, "North Carolina": {"primary": "#7BAFD4", "emoji": "🐏"},
    "Memphis": {"primary": "#003087", "emoji": "🐯"}, "Sacramento State": {"primary": "#004B49", "emoji": "🐝"},
    "Florida State": {"primary": "#78243C", "emoji": "🏹"}, "TCU": {"primary": "#4D1979", "emoji": "🐸"},
    "North Dakota State": {"primary": "#0A5640", "emoji": "🦬"}, "Virginia": {"primary": "#232D4B", "emoji": "⚔️"},
    "Jacksonville State": {"primary": "#CC0000", "emoji": "🐓"}, "NC State": {"primary": "#CC0000", "emoji": "🐺"}
}
DEFAULT_BRAND = {"primary": "#1e293b", "emoji": "🏈"}

def pct_to_american_odds(percentage):
    if percentage >= 100: return "-10000"
    if percentage <= 0: return "+10000"
    if percentage > 50:
        return f"{int(-((percentage) / (100 - percentage)) * 100)}"
    return f"+{int(((100 - percentage) / percentage) * 100)}"

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
        st.warning("🔄 Awaiting data from your collection loops...")
    else:
        for m in PROP_MARKETS.values():
            if m["col"] in df.columns:
                df[m["col"]] = df[m["col"]].fillna(0)

        # 🗺️ --- MULTI-PAGE NAVIGATION CONTROLS ---
        st.sidebar.markdown("### 🗺️ Navigation Controls")
        app_page = st.sidebar.radio("Go To Dashboard Page:", [
            "🎯 Single Player Analysis", 
            "🏆 National Stat Leaderboards",
            "⚔️ Team Offense vs Defense Ranker"
        ])
        st.sidebar.markdown("---")

        available_years = sorted(df["season"].unique(), reverse=True) if "season" in df.columns else [2026]
        selected_year = st.sidebar.selectbox("📅 Select Season Year", available_years)
        year_df = df[df["season"] == selected_year]

        # ==========================================
        # ⚔️ NEW PAGE: TEAM OFFENSE VS DEFENSE RANKER
        # ==========================================
        if app_page == "⚔️ Team Offense vs Defense Ranker":
            st.header(f"⚔️ {selected_year} Team Efficiency Matchup Board")
            st.markdown("---")
            
            selected_mode = st.selectbox("Select Matchup Market Category:", ["Passing Efficiency", "Rushing Efficiency"])
            metric_col = "pass_yards" if selected_mode == "Passing Efficiency" else "rush_yards"
            
            # --- 1. COMPUTE TOTAL OFFENSIVE RANKS ---
            off_df = year_df.groupby("team")[metric_col].sum().reset_index()
            off_df = off_df.sort_values(by=metric_col, ascending=False).reset_index(drop=True)
            off_df.index += 1
            off_df["off_rank"] = off_df.index
            
            # --- 2. COMPUTE TOTAL DEFENSIVE RANKS (Total yards allowed to opposing teams) ---
            def_df = year_df.groupby("opponent")[metric_col].sum().reset_index()
            def_df = def_df.rename(columns={"opponent": "team", metric_col: "yards_allowed"})
            # Fewer yards allowed = Better Defense (Ascending Sort)
            def_df = def_df.sort_values(by="yards_allowed", ascending=True).reset_index(drop=True)
            def_df.index += 1
            def_df["def_rank"] = def_df.index

            # Merge tables cleanly
            team_master_ranks = pd.merge(off_df, def_df, on="team", how="outer").fillna(99)
            
            # --- 3. INTERACTIVE MATCHUP SPLIT ---
            st.subheader("🏈 Evaluate Upcoming Gridiron Advantages")
            col_teamA, col_teamB = st.columns(2)
            
            all_teams_list = sorted(year_df["team"].unique()) if not year_df.empty else []
            
            with col_teamA:
                st.markdown("### 🏟️ Team A (Offense)")
                team_a = st.selectbox("Select Offensive Team:", all_teams_list, index=0 if len(all_teams_list) > 0 else 0, key="team_a_sel")
                
                a_data = team_master_ranks[team_master_ranks["team"] == team_a]
                if not a_data.empty:
                    st.markdown(f"""
                    <div class="matchup-card">
                        <h4>{team_a} Metrics</h4>
                        <p>📈 <b>Offensive National Rank:</b> #{int(a_data['off_rank'].values[0])}</p>
                        <p>📊 Total Gained: {int(a_data[metric_col].values[0])} Yds</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with col_teamB:
                st.markdown("### 🛡️ Team B (Defense)")
                team_b = st.selectbox("Select Defensive Team:", all_teams_list, index=min(1, len(all_teams_list)-1), key="team_b_sel")
                
                b_data = team_master_ranks[team_master_ranks["team"] == team_b]
                if not b_data.empty:
                    st.markdown(f"""
                    <div class="matchup-card">
                        <h4>{team_b} Metrics</h4>
                        <p>🛡️ <b>Defensive National Rank:</b> #{int(b_data['def_rank'].values[0])}</p>
                        <p>🛑 Total Allowed: {int(b_data['yards_allowed'].values[0])} Yds</p>
                    </div>
                    """, unsafe_allow_html=True)

            # --- 4. DATA MATRIX DISPLAY ---
            st.markdown("---")
            st.subheader(f"📄 Full National Efficiency Standing Sheet ({selected_year})")
            
            display_rank_df = team_master_ranks.rename(columns={
                "team": "School/Program",
                metric_col: "Total Offense Gained (Yds)",
                "off_rank": "Offense Rank",
                "yards_allowed": "Total Defense Allowed (Yds)",
                "def_rank": "Defense Rank"
            })
            st.dataframe(display_rank_df[["School/Program", "Offense Rank", "Total Offense Gained (Yds)", "Defense Rank", "Total Defense Allowed (Yds)"]], use_container_width=True)

        # ==========================================
        # 🏆 PAGE: NATIONAL LEADERBOARDS RANKINGS
        # ==========================================
        elif app_page == "🏆 National Stat Leaderboards":
            st.header(f"🏆 {selected_year} National Player Rankings & Leaderboards")
            st.markdown("---")
            
            selected_rank_market = st.selectbox("Select Stat Category to Rank:", list(PROP_MARKETS.keys()), index=0)
            rank_col = PROP_MARKETS[selected_rank_market]["col"]
            rank_unit = PROP_MARKETS[selected_rank_market]["unit"]
            
            leader_df = year_df.groupby(["player_name", "team"])[rank_col].sum().reset_index()
            leader_df = leader_df[leader_df[rank_col] > 0]
