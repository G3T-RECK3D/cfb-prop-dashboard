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
    "Passing Yards":        {"col": "pass_yards", "max": 500.0, "default": 249.5, "step": 1.0, "unit": "Yds"},
    "Pass Completions":     {"col": "pass_cmp",   "max": 40.0,  "default": 19.5,  "step": 0.5, "unit": "Cmp"},
    "Passing TDs":          {"col": "pass_tds",   "max": 6.0,   "default": 1.5,   "step": 0.5, "unit": "TDs"},
    "Interceptions Thrown":{"col": "pass_int",   "max": 5.0,   "default": 0.5,   "step": 0.5, "unit": "Int"},
    "Rushing Yards":        {"col": "rush_yards", "max": 250.0, "default": 79.5,  "step": 1.0, "unit": "Yds"},
    "Rushing Attempts":     {"col": "rush_att",   "max": 35.0,  "default": 14.5,  "step": 0.5, "unit": "Att"},
    "Rushing TDs":          {"col": "rush_tds",   "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Receiving Yards":      {"col": "rec_yards",  "max": 200.0, "default": 59.5,  "step": 1.0, "unit": "Yds"},
    "Receptions":           {"col": "receptions", "max": 12.0,  "default": 4.5,   "step": 0.5, "unit": "Rec"},
    "Receiving TDs":        {"col": "rec_tds",    "max": 4.0,   "default": 0.5,   "step": 0.5, "unit": "TDs"},
    "Total Offense Yds":    {"col": "total_offense", "max": 600.0, "default": 299.5, "step": 1.0, "unit": "Yds"},
    "Total Scrimmage Yds":  {"col": "total_scrimmage", "max": 300.0, "default": 99.5, "step": 1.0, "unit": "Yds"}
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
        tab_analysis, tab_blank, tab_slate = st.tabs([
            "🎯 Single Player Analysis", 
            "📈 Opportunity & Opponent Matchup Matrix",
            "📅 Pre-Game Slate Mismatch Scanner"
        ])

        # Global Sidebar Filter Settings
        st.sidebar.markdown("### 🎯 Filter Settings")
        available_years = sorted(df["season"].unique(), reverse=True) if "season" in df.columns else []
        selected_year = st.sidebar.selectbox("📅 Select Season Year", available_years)
        year_df = df[df["season"] == selected_year]

        # ==========================================
        # TAB 1: 🎯 SINGLE PLAYER ANALYSIS
        # ==========================================
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

        # ==========================================
        # TAB 2: 📈 OPPORTUNITY & MATCHUP MATRIX
        # ==========================================
        with tab_blank:
            st.header("📈 Opportunity & Opponent Matchup Matrix")
            st.markdown("##### *Analyze player volume metrics and compare stats against defensive matchups.*")
            st.markdown("---")

            # Defensive Aggregations
            game_defense = year_df.groupby(["opponent", "season", "week"]).agg(
                total_pass_yds=("pass_yards", "sum"),
                total_rush_yds=("rush_yards", "sum"),
                total_pass_att=("pass_att", "sum"),
                total_rush_att=("rush_att", "sum")
            ).reset_index()

            def_df = game_defense.groupby("opponent").agg(
                games_played=("week", "count"),
                pass_yds_allowed=("total_pass_yds", "mean"),
                rush_yds_allowed=("total_rush_yds", "mean"),
                pass_att_allowed=("total_pass_att", "mean"),
                rush_att_allowed=("total_rush_att", "mean")
            ).reset_index()

            def_df["Pass Yds Rank"] = def_df["pass_yds_allowed"].rank(ascending=True).astype(int)
            def_df["Rush Yds Rank"] = def_df["rush_yds_allowed"].rank(ascending=True).astype(int)

            col_ctrl1, col_ctrl2 = st.columns(2)
            
            # Fetch all distinct teams and players directly for independent tab selection
            all_teams = sorted(year_df["team"].unique()) if "team" in year_df.columns else []
            all_players = sorted(year_df["player_name"].unique()) if "player_name" in year_df.columns else []

            with col_ctrl1:
                selected_opp = st.selectbox("🛡️ Select Upcoming Opponent Defense", all_teams if all_teams else ["No Data"], key="matrix_opp_sel")
            with col_ctrl2:
                opp_player = st.selectbox("👤 Target Player for Matchup", all_players if all_players else ["No Data"], key="matrix_player_sel")

            st.markdown("---")

            if opp_player != "No Data":
                st.subheader(f"📊 Volume & Usage Profile: {opp_player}")
                p_df = year_df[year_df["player_name"] == opp_player].sort_values("week")
                t_name = p_df["team"].iloc[0] if not p_df.empty else "Unknown"

                # Calculate Usage Shares
                team_game_totals = year_df[year_df["team"] == t_name].groupby("week").agg(
                    team_pass_att=("pass_att", "sum"),
                    team_rush_att=("rush_att", "sum")
                ).reset_index()

                p_merged = pd.merge(p_df, team_game_totals, on="week", how="left")
                p_merged["carry_share"] = (p_merged["rush_att"] / p_merged["team_rush_att"].replace(0, 1)) * 100
                p_merged["pass_att_share"] = (p_merged["pass_att"] / p_merged["team_pass_att"].replace(0, 1)) * 100

                u1, u2, u3, u4 = st.columns(4)
                u1.metric("Avg Rush Att / Game", f"{p_merged['rush_att'].mean():.1f}")
                u2.metric("Team Carry Share %", f"{p_merged['carry_share'].mean():.1f}%")
                u3.metric("Avg Pass Att / Game", f"{p_merged['pass_att'].mean():.1f}")
                u4.metric("Team Pass Att Share %", f"{p_merged['pass_att_share'].mean():.1f}%")

                fig_usage = px.bar(
                    p_merged, x="opponent", y=["rush_att", "pass_att"],
                    barmode="group", title="Weekly Touches & Attempts Breakdown",
                    labels={"value": "Volume Count", "variable": "Metric", "opponent": "Opponent"}
                )
                fig_usage.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#f1f5f9")
                st.plotly_chart(fig_usage, use_container_width=True)

                st.markdown("---")
                st.subheader(f"🛡️ Matchup Profile: {t_name} vs. {selected_opp} Defense")

            opp_stats = def_df[def_df["opponent"] == selected_opp]
            
            if not opp_stats.empty:
                d_pass_yds = opp_stats["pass_yds_allowed"].values[0]
                d_rush_yds = opp_stats["rush_yds_allowed"].values[0]

                m1, m2 = st.columns(2)
                m1.metric("Opponent Pass Yds Allowed / Game", f"{d_pass_yds:.1f} Yds")
                m2.metric("Opponent Rush Yds Allowed / Game", f"{d_rush_yds:.1f} Yds")

                st.markdown("##### 🏆 Defensive Rank Matrix (All Logged Opponents)")
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

        # ==========================================
# TAB 3: 📅 PRE-GAME SLATE MISMATCH SCANNER
# ==========================================
with tab_slate:
    st.header("📅 Pre-Game Slate Mismatch Scanner")
    st.markdown("##### *Identify deep offensive and defensive advantages for the upcoming board.*")
    st.markdown("---")

    try:
        sched_resp = supabase.table("upcoming_schedule").select("*").limit(10000).execute()
        sched_df = pd.DataFrame(sched_resp.data)

        if sched_df.empty:
            st.warning("⚠️ No upcoming games logged in your 'upcoming_schedule' table yet.")
        else:
            c_year, c_week = st.columns(2)
            
            with c_year:
                sched_years = sorted(sched_df["season"].unique(), reverse=True) if "season" in sched_df.columns else [selected_year]
                slate_year = st.selectbox("📅 Schedule Season", sched_years, key="slate_year_sel")
            
            season_sched = sched_df[sched_df["season"] == slate_year] if "season" in sched_df.columns else sched_df
            
            with c_week:
                available_weeks = sorted(season_sched["week"].unique()) if "week" in season_sched.columns else []
                selected_week = st.selectbox("🏈 Upcoming Slate Week", available_weeks, key="slate_week_sel") if available_weeks else 1
            
            week_sched = season_sched[season_sched["week"] == selected_week] if "week" in season_sched.columns else season_sched

            # 👇 PASTE/REPLACE THE NEW LOGIC HERE 👇
            home_games = week_sched[['season', 'week', 'home_team', 'away_team']].rename(
                columns={'home_team': 'team', 'away_team': 'opponent'}
            )

            away_games = week_sched[['season', 'week', 'away_team', 'home_team']].rename(
                columns={'away_team': 'team', 'home_team': 'opponent'}
            )

            # Stack them to give every team a row for their match
            normalized_schedule = pd.concat([home_games, away_games], ignore_index=True)
            # 👆 END OF REPLACEMENT 👆

            # Build defensive and offensive stats from player_game_logs
            hist_df = df[df["season"] == slate_year] if ("season" in df.columns and slate_year in df["season"].unique()) else df

            if not hist_df.empty:
                game_defense = hist_df.groupby(["opponent", "week"]).agg(
                    total_pass_yds=("pass_yards", "sum"),
                    total_rush_yds=("rush_yards", "sum")
                ).reset_index()

                def_df = game_defense.groupby("opponent").agg(
                    pass_yds_allowed=("total_pass_yds", "mean"),
                    rush_yds_allowed=("total_rush_yds", "mean")
                ).reset_index()

                game_offense = hist_df.groupby(["team", "week"]).agg(
                    total_pass_yds=("pass_yards", "sum"),
                    total_rush_yds=("rush_yards", "sum")
                ).reset_index()

                off_df = game_offense.groupby("team").agg(
                    pass_yds_gained=("total_pass_yds", "mean"),
                    rush_yds_gained=("total_rush_yds", "mean")
                ).reset_index()
            else:
                def_df = pd.DataFrame(columns=["opponent", "pass_yds_allowed", "rush_yds_allowed"])
                off_df = pd.DataFrame(columns=["team", "pass_yds_gained", "rush_yds_gained"])

            def_df["Pass_Def_Rank"] = def_df["pass_yds_allowed"].rank(ascending=True).fillna(99).astype(int)
            def_df["Rush_Def_Rank"] = def_df["rush_yds_allowed"].rank(ascending=True).fillna(99).astype(int)
            off_df["Pass_Off_Rank"] = off_df["pass_yds_gained"].rank(ascending=False).fillna(99).astype(int)
            off_df["Rush_Off_Rank"] = off_df["rush_yds_gained"].rank(ascending=False).fillna(99).astype(int)

            # Merge normalized schedule with team & defensive stats
            matchup_summary = pd.merge(normalized_schedule, def_df, on="opponent", how="left")
            matchup_summary = pd.merge(matchup_summary, off_df, on="team", how="left")

            fill_cols = ["pass_yds_allowed", "rush_yds_allowed", "pass_yds_gained", "rush_yds_gained"]
            for col in fill_cols:
                if col in matchup_summary.columns:
                    matchup_summary[col] = matchup_summary[col].fillna(0)
            
            matchup_summary["Pass_Def_Rank"] = matchup_summary["Pass_Def_Rank"].fillna(99).astype(int)
            matchup_summary["Rush_Def_Rank"] = matchup_summary["Rush_Def_Rank"].fillna(99).astype(int)
            matchup_summary["Pass_Off_Rank"] = matchup_summary["Pass_Off_Rank"].fillna(99).astype(int)
            matchup_summary["Rush_Off_Rank"] = matchup_summary["Rush_Off_Rank"].fillna(99).astype(int)

            matchup_summary["Net_Pass_Edge"] = matchup_summary["Pass_Def_Rank"] - matchup_summary["Pass_Off_Rank"]
            matchup_summary["Net_Rush_Edge"] = matchup_summary["Rush_Def_Rank"] - matchup_summary["Rush_Off_Rank"]

            # UI Display
            st.subheader(f"🔥 Top Projected Passing & Rushing Mismatches — Season {slate_year} Week {selected_week}")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🎯 Passing Advantages")
                pass_mismatches = matchup_summary.sort_values(by="Net_Pass_Edge", ascending=False).head(3)
                
                if not pass_mismatches.empty and (pass_mismatches["pass_yds_gained"].sum() > 0 or pass_mismatches["pass_yds_allowed"].sum() > 0):
                    for _, row in pass_mismatches.iterrows():
                        st.success(
                            f"🏈 **{row['team']}** vs. **{row['opponent']}**\n\n"
                            f"• Offense Passing Rank: **#{row['Pass_Off_Rank']}** ({row['pass_yds_gained']:.0f} Gained/G)\n\n"
                            f"• Defense Allowed Rank: **#{row['Pass_Def_Rank']}** ({row['pass_yds_allowed']:.0f} Allowed/G)\n\n"
                            f"• **Net Pass Advantage Score: +{row['Net_Pass_Edge']}**"
                        )
                else:
                    st.info("No prior passing statistics available yet for this slate's teams.")

            with col2:
                st.markdown("#### 🚜 Rushing Advantages")
                rush_mismatches = matchup_summary.sort_values(by="Net_Rush_Edge", ascending=False).head(3)
                
                if not rush_mismatches.empty and (rush_mismatches["rush_yds_gained"].sum() > 0 or rush_mismatches["rush_yds_allowed"].sum() > 0):
                    for _, row in rush_mismatches.iterrows():
                        st.success(
                            f"🚜 **{row['team']}** vs. **{row['opponent']}**\n\n"
                            f"• Offense Rushing Rank: **#{row['Rush_Off_Rank']}** ({row['rush_yds_gained']:.0f} Gained/G)\n\n"
                            f"• Defense Allowed Rank: **#{row['Rush_Def_Rank']}** ({row['rush_yds_allowed']:.0f} Allowed/G)\n\n"
                            f"• **Net Rush Advantage Score: +{row['Net_Rush_Edge']}**"
                        )
                else:
                    st.info("No prior rushing statistics available yet for this slate's teams.")

            st.markdown("---")
            st.subheader("📋 Scheduled Games & Defensive Matchup Matrix")
            
            display_matrix = matchup_summary.rename(columns={
                "team": "Offense Team", "opponent": "Defensive Opponent",
                "Pass_Off_Rank": "Off Pass Rank", "Pass_Def_Rank": "Opp Def Pass Rank",
                "Net_Pass_Edge": "Net Pass Edge", "Rush_Off_Rank": "Off Rush Rank",
                "Rush_Def_Rank": "Opp Def Rush Rank", "Net_Rush_Edge": "Net Rush Edge"
            })
            
            show_cols = ["Offense Team", "Off Pass Rank", "Defensive Opponent", "Opp Def Pass Rank", "Net Pass Edge", "Off Rush Rank", "Opp Def Rush Rank", "Net Rush Edge"]
            valid_cols = [c for c in show_cols if c in display_matrix.columns]
            st.dataframe(display_matrix[valid_cols], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("⚠️ Server encountered an issue querying the 'upcoming_schedule' table.")
        st.code(e)

except Exception as global_e:
    st.error("⚠️ Failed to load database logs.")
    st.code(global_e)
