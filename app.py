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
    </style>
""", unsafe_allow_html=True)

st.title("🏈 College Football Player Prop Co-Pilot")
st.markdown("##### *Advanced Historical Analysis & Fair Value Odds Engine*")
st.markdown("---")

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
    "Jacksonville State": {"primary": "#CC0000", "emoji": "Camp"}, "NC State": {"primary": "#CC0000", "emoji": "🐺"}
}
DEFAULT_BRAND = {"primary": "#1e293b", "emoji": "🏈"}

def pct_to_american_odds(percentage):
    if percentage >= 100: return "-10000"
    if percentage <= 0: return "+10000"
    if percentage > 50:
        return f"{int(-((percentage) / (100 - percentage)) * 100)}"
    return f"+{int(((100 - percentage) / percentage) * 100)}"

# EXPANDED PROP MARKETS TO MATCH NEW COLUMNS AND AUTO-CALCULATED TOTAL MARGINS
PROP_MARKETS = {
    "Passing Yards":       {"col": "pass_yards", "max": 500.0, "default": 249.5, "step": 1.0, "unit": "Yds"},
    "Pass Completions":    {"col": "pass_cmp",   "max": 40.0,  "default": 19.5,  "step": 0.5, "unit": "Cmp"},
    "Passing TDs":         {"col": "pass_tds",   "max": 6.0,   "default": 1.5,   "step": 0.5, "unit": "TDs"},
    "Interceptions Thrown":{"col": "pass_int",   "max": 5.0,   "default": 0.5,   "step": 0.5, "unit": "Int"},
    "Rushing Yards":       {"col": "rush_yards", "max": 250.0, "default": 79.5,  "step": 1.0, "unit": "Yds"},
    "Rushing Attempts":    {"col": "rush_att",   "max": 35.0,  "default": 14.5,  "step": 0.5, "unit": "Att"},
    "Rushing TDs":         {"col": "rush_tds",   "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Receiving Yards":     {"col": "rec_yards",  "max": 200.0, "default": 59.5,  "step": 1.0, "unit": "Yds"},
    "Receptions":          {"col": "receptions", "max": 12.0,  "default": 4.5,   "step": 0.5, "unit": "Rec"},
    "Receiving TDs":       {"col": "rec_tds",    "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Total Offense Yds":   {"col": "total_offense", "max": 600.0, "default": 299.5, "step": 1.0, "unit": "Yds"},
    "Total Scrimmage Yds": {"col": "total_scrimmage", "max": 300.0, "default": 99.5, "step": 1.0, "unit": "Yds"}
}

try:
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("🔄 Table layout established on live server. Awaiting records...")
    else:
        # Fill missing values and handle auto-calculations securely
        raw_cols = ["pass_yards", "pass_cmp", "pass_att", "pass_tds", "pass_int", "rush_att", "rush_yards", "rush_tds", "rec_yards", "receptions", "rec_tds"]
        for c in raw_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c]).fillna(0).astype(int)
            else:
                df[c] = 0

        # LIVE MATHEMATICAL AUTO-CALCULATIONS FOR COMBINED MARKETS
        df["total_offense"] = df["pass_yards"] + df["rush_yards"]
        df["total_scrimmage"] = df["rush_yards"] + df["rec_yards"]

        # Structural UI Multi-tab separation
        tab_analysis, tab_blank = st.tabs(["🎯 Single Player Analysis", "📈 Opportunity & Opponent Matchup Matrix"])

        # Global Sidebar Filter Settings
        st.sidebar.markdown("### 🎯 Filter Settings")
        available_years = sorted(df["season"].unique(), reverse=True) if "season" in df.columns else []
        selected_year = st.sidebar.selectbox("📅 Select Season Year", available_years)
        year_df = df[df["season"] == selected_year]

        with tab_analysis:
            available_teams = sorted(year_df["team"].unique()) if "team" in year_df.columns else []
            selected_team = st.sidebar.selectbox("1️⃣ Select Program/Team", available_teams)
            
            selected_market_name = st.sidebar.selectbox("2️⃣ Select Prop Market", list(PROP_MARKETS.keys()))
            market_info = PROP_MARKETS[selected_market_name]
            stat_col = market_info["col"]

            filtered_team_df = year_df[year_df["team"] == selected_team]
            
            if filtered_team_df.empty:
                st.error("⚠️ No active team profiles recorded for this parameters selection.")
            else:
                player_totals = filtered_team_df.groupby("player_name")[stat_col].sum().reset_index()
                player_totals = player_totals.sort_values(by=stat_col, ascending=False)
                ranked_players = player_totals["player_name"].tolist()

                if not ranked_players:
                    st.warning(f"⚠️ No active lines with logged {selected_market_name} stats.")
                else:
                    display_options = {r["player_name"]: f"{r['player_name']} ({r[stat_col]:.0f} {market_info['unit']})" for _, r in player_totals.iterrows()}
                    selected_player = st.sidebar.selectbox("3️⃣ Select Player Profile", ranked_players, format_func=lambda x: display_options.get(x, x))

                    prop_line = st.sidebar.slider("Sportsbook Line Mark", min_value=0.0, max_value=market_info["max"], value=market_info["default"], step=market_info["step"])

                    brand = TEAM_BRANDING.get(selected_team, DEFAULT_BRAND)
                    st.subheader(f"{brand['emoji']} {selected_player.upper()}")
                    st.markdown(f"*{selected_team} | Season {selected_year} Analytics Dataset*")

                    player_df = year_df[year_df["player_name"] == selected_player].sort_values(by="week")
                    total_games = len(player_df)
                    avg_stat = player_df[stat_col].mean() if total_games > 0 else 0
                    median_stat = player_df[stat_col].median() if total_games > 0 else 0
                    
                    overs = player_df[player_df[stat_col] > prop_line]
                    over_count = len(overs)
                    under_count = total_games - over_count
                    over_pct = (over_count / total_games * 100) if total_games > 0 else 0
                    
                    fair_over_odds = pct_to_american_odds(over_pct)
                    fair_under_odds = pct_to_american_odds(100 - over_pct)
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Games Documented", f"{total_games}")
                    c2.metric("Season Average", f"{avg_stat:.1f} {market_info['unit']}")
                    c3.metric("Season Median", f"{median_stat:.1f} {market_info['unit']}")
                    c4.metric("OVER Hit Rate 📈", f"{over_pct:.1f}%", delta=f"{over_count} Matches")
                    
                    st.markdown("---")
                    st.subheader(f"💸 Fair Value Implied Odds Calculation: {selected_market_name}")
                    col_odds1, col_odds2 = st.columns(2)
                    with col_odds1:
                        st.markdown(f"#### 📈 Target Over: **{prop_line} {market_info['unit']}**")
                        st.metric(label="Model Implied Price", value=fair_over_odds)
                    with col_odds2:
                        st.markdown(f"#### 📉 Target Under: **{prop_line} {market_info['unit']}**")
                        st.metric(label="Model Implied Price", value=fair_under_odds)
                    
                    st.markdown("---")
                    st.subheader(f"📊 Historical Game Breakdown: {selected_market_name}")
                    player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")    
                    
                    fig = px.bar(
                        player_df, x="opponent", y=stat_col, color="Result",
                        color_discrete_map={"🟢 OVER": brand["primary"], "🔴 UNDER": "#475569"},
                        text=stat_col, labels={stat_col: selected_market_name, "opponent": "Opponent"}
                    )
                    fig.add_hline(y=prop_line, line_dash="dash", line_color="#cbd5e1")
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("📄 Filtered Database Records")
                    show_cols = [c for c in ["season", "week", "opponent", stat_col] if c in player_df.columns]
                    st.dataframe(player_df[show_cols], use_container_width=True)
                    
        with tab_blank:
            st.header("📈 Opportunity & Opponent Matchup Matrix")
            st.markdown("##### *Analyze player volume metrics and compare stats against defensive matchups.*")
            st.markdown("---")

            # 1. First sum player stats per game to get total team output per game
            game_defense = year_df.groupby(["opponent", "season", "week"]).agg(
                total_pass_yds=("pass_yards", "sum"),
                total_rush_yds=("rush_yards", "sum"),
                total_pass_att=("pass_att", "sum"),
                total_rush_att=("rush_att", "sum")
            ).reset_index()

            # 2. Now calculate the true per-game defensive averages
            def_df = game_defense.groupby("opponent").agg(
                games_played=("week", "count"),
                pass_yds_allowed=("total_pass_yds", "mean"),
                rush_yds_allowed=("total_rush_yds", "mean"),
                pass_att_allowed=("total_pass_att", "mean"),
                rush_att_allowed=("total_rush_att", "mean")
            ).reset_index()

            # 3. Add Defensive Ranks (Worst Defenses = 1st rank for Over betting opportunities)
            def_df["Pass Yds Rank"] = def_df["pass_yds_allowed"].rank(ascending=True).astype(int)
            def_df["Rush Yds Rank"] = def_df["rush_yds_allowed"].rank(ascending=True).astype(int)

            # 2. Controls & Selectors
            col_ctrl1, col_ctrl2 = st.columns(2)
            with col_ctrl1:
                selected_opp = st.selectbox("🛡️ Select Upcoming Opponent Defense", sorted(year_df["team"].unique()))
            with col_ctrl2:
                # Reuse player selected from main sidebar or pick locally
                opp_player = st.selectbox("👤 Target Player for Matchup", ranked_players, index=0)

            st.markdown("---")

            # 3. Player Usage & Volume Metrics
            st.subheader(f"📊 Volume & Usage Profile: {opp_player}")
            p_df = year_df[year_df["player_name"] == opp_player].sort_values("week")
            t_name = p_df["team"].iloc[0] if not p_df.empty else selected_team

            # Compute Team Totals per week to calculate true Target & Carry Share
            team_game_totals = year_df[year_df["team"] == t_name].groupby("week").agg(
                team_pass_att=("pass_att", "sum"),
                team_rush_att=("rush_att", "sum")
            ).reset_index()

            p_merged = pd.merge(p_df, team_game_totals, on="week", how="left")
            p_merged["carry_share"] = (p_merged["rush_att"] / p_merged["team_rush_att"].replace(0, 1)) * 100
            p_merged["pass_att_share"] = (p_merged["pass_att"] / p_merged["team_pass_att"].replace(0, 1)) * 100

            u1, u2, u3, u4 = st.columns(4)
            avg_carries = p_merged["rush_att"].mean()
            avg_carry_share = p_merged["carry_share"].mean()
            avg_pass_att = p_merged["pass_att"].mean()
            avg_pass_share = p_merged["pass_att_share"].mean()

            u1.metric("Avg Rush Att / Game", f"{avg_carries:.1f}")
            u2.metric("Team Carry Share %", f"{avg_carry_share:.1f}%")
            u3.metric("Avg Pass Att / Game", f"{avg_pass_att:.1f}")
            u4.metric("Team Pass Att Share %", f"{avg_pass_share:.1f}%")

            # Usage Visualization Chart
            fig_usage = px.bar(
                p_merged, x="opponent", y=["rush_att", "pass_att"],
                barmode="group", title="Weekly Touches & Attempts Breakdown",
                labels={"value": "Volume Count", "variable": "Metric", "opponent": "Opponent"}
            )
            fig_usage.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
            st.plotly_chart(fig_usage, use_container_width=True)

            st.markdown("---")

            # 4. Opponent Defense Matchup Analysis
            st.subheader(f"🛡️ Matchup Profile: {t_name} vs. {selected_opp} Defense")
            
            opp_stats = def_df[def_df["opponent"] == selected_opp]
            
            if not opp_stats.empty:
                d_pass_yds = opp_stats["pass_yds_allowed"].values[0]
                d_rush_yds = opp_stats["rush_yds_allowed"].values[0]

                # Defensive Context Metrics
                m1, m2 = st.columns(2)
                m1.metric("Opponent Pass Yds Allowed / Game", f"{d_pass_yds:.1f} Yds")
                m2.metric("Opponent Rush Yds Allowed / Game", f"{d_rush_yds:.1f} Yds")

                # Opponent Ranking Heatmap across all logged defenses
                st.markdown("##### 🏆 Defensive Rank Matrix (All Logged Opponents)")
                def_df["Pass Yds Rank"] = def_df["pass_yds_allowed"].rank(ascending=True).astype(int)
                def_df["Rush Yds Rank"] = def_df["rush_yds_allowed"].rank(ascending=True).astype(int)

                # Change the sort_values to sort by your new Rank column (1, 2, 3...)
                st.dataframe(
                    def_df.sort_values("Pass Yds Rank", ascending=True),
                    column_config={
                        "opponent": "Defense Program",
                        "pass_yds_allowed": st.column_config.NumberColumn("Avg Pass Yds Allowed", format="%.1f"),
                        "rush_yds_allowed": st.column_config.NumberColumn("Avg Rush Yds Allowed", format="%.1f")
                    },
                    use_container_width=True
                )
            else:
                st.info(f"ℹ️ No defensive game records logged for {selected_opp} yet.")
                    
except Exception as e:
    st.error("❌ The dashboard server encountered an obstacle connecting to your database.")
    st.code(e)
                    

