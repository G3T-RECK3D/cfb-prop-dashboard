import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. --- APP CONFIGURATION & STYLE ---
st.set_page_config(page_title="CFB Prop Analyzer", layout="wide", page_icon="🏈")
st.title("🏈 College Football Player Prop Co-Pilot")
st.markdown("---")

# Secure connection setup to your live server database
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA" # <-- Paste your long 'eyJ...' key here
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- HELPER FUNCTION: PERCENTAGE TO AMERICAN ODDS ---
def pct_to_american_odds(percentage):
    if percentage >= 100:
        return "-∞"
    if percentage <= 0:
        return "+∞"
    if percentage > 50:
        odds = int(-((percentage) / (100 - percentage)) * 100)
        return f"{odds}"
    else:
        odds = int(((100 - percentage) / percentage) * 100)
        return f"+{odds}"

try:
    # 2. --- FETCH DATA FROM DATABASE ---
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("⚠️ Connected to Supabase, but your table appears to be empty!")
    else:
        # 3. --- SIDEBAR CONTROLS ---
        st.sidebar.header("🎯 Analytics Controls")
        available_players = df["player_name"].unique()
        selected_player = st.sidebar.selectbox("Select Player", available_players)
        
        player_df = df[df["player_name"] == selected_player].sort_values(by="week")
        
        # 4. --- DETECT POSITION ---
        is_qb = any(player_df["pass_yards"] > 0) if "pass_yards" in player_df.columns else False
        is_wr = any(player_df["rec_yards"] > 0) if "rec_yards" in player_df.columns else False
        
        if is_qb:
            stat_col, label_name, max_val, default_val = "pass_yards", "Passing Yards", 500.0, 300.0
        elif is_wr:
            stat_col, label_name, max_val, default_val = "rec_yards", "Receiving Yards", 250.0, 85.5
        else:
            stat_col, label_name, max_val, default_val = "rush_yards", "Rushing Yards", 300.0, 120.5

        prop_line = st.sidebar.slider(f"Set Sportsbook Line ({label_name})", 0.0, max_val, default_val, 0.5)
        
        # 5. --- CALCULATE METRICS & ODDS ---
        total_games = len(player_df)
        avg_stat = player_df[stat_col].mean()
        median_stat = player_df[stat_col].median()
        
        overs = player_df[player_df[stat_col] > prop_line]
        over_count = len(overs)
        under_count = total_games - over_count
        
        over_pct = (over_count / total_games * 100) if total_games > 0 else 0
        under_pct = (under_count / total_games * 100) if total_games > 0 else 0
        
        fair_over_odds = pct_to_american_odds(over_pct)
        fair_under_odds = pct_to_american_odds(under_pct)
        
        # Main Display
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Games Logged", f"{total_games}")
        c2.metric("Season Average", f"{avg_stat:.1f} yds")
        c3.metric("Season Median", f"{median_stat:.1f} yds")
        c4.metric("OVER Hit Rate 📈", f"{over_pct:.1f}%", delta=f"{over_count} Games")
        
        # Odds Calculator Row
        st.markdown("### 💸 Fair Value Implied Odds Calculator")
        col_odds1, col_odds2 = st.columns(2)
        with col_odds1:
            st.subheader(f"📈 OVER {prop_line} Odds")
            st.metric(label="Model Fair Value Line", value=fair_over_odds, delta=f"Hit {over_count}/{total_games} times")
        with col_odds2:
            st.subheader(f"📉 UNDER {prop_line} Odds")
            st.metric(label="Model Fair Value Line", value=fair_under_odds, delta=f"Hit {under_count}/{total_games} times")
        st.markdown("---")
        
        # Charting
        st.markdown(f"### 📊 Historical {label_name} vs Line")
        player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")
        fig = px.bar(player_df, x="opponent", y=stat_col, color="Result",
                     color_discrete_map={"🟢 OVER": "#2ecc71", "🔴 UNDER": "#e74c3c"}, text=stat_col)
        fig.add_hline(y=prop_line, line_dash="dash", line_color="#34495e")
        st.plotly_chart(fig, use_container_width=True)
        
        # Spreadsheet Table
        st.markdown("### 📄 Raw Database Slice")
        st.dataframe(player_df[["season", "week", "opponent", stat_col]], use_container_width=True)
        st.markdown("---")

    # 6. --- NEW! NO-CODE DATA ENTRY EXPANDER FORM ---
    with st.expander("➕ Click Here to Add New Game Log Stats manually"):
        st.subheader("📋 Manual Stat Entry Form")
        with st.form("stat_form", clear_on_submit=True):
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                new_name = st.text_input("Player Name")
                new_pos = st.selectbox("Position", ["QB", "RB", "WR"])
            with col_f2:
                new_team = st.text_input("Player's Team")
                new_opp = st.text_input("Opponent")
            with col_f3:
                new_year = st.number_input("Season", value=2026, step=1)
                new_wk = st.number_input("Week", value=1, step=1)
            with col_f4:
                # Dynamically provide the primary stat box based on selection
                if new_pos == "QB":
                    new_stat = st.number_input("Passing Yards", value=0, step=1)
                elif new_pos == "WR":
                    new_stat = st.number_input("Receiving Yards", value=0, step=1)
                else:
                    new_stat = st.number_input("Rushing Yards", value=0, step=1)
            
            submit_btn = st.form_submit_button("Save Game Log to Supabase Database")
            
            if submit_btn:
                if not new_name or not new_team or not new_opp:
                    st.error("Please fill out the Player Name, Team, and Opponent fields before saving.")
                else:
                    # Construct the data payload dynamically mapping correct position stats
                    payload = {
                        "player_name": new_name,
                        "position": new_pos,
                        "team": new_team,
                        "opponent": new_opp,
                        "season": int(new_year),
                        "week": int(new_wk),
                        "pass_yards": int(new_stat) if new_pos == "QB" else 0,
                        "rush_yards": int(new_stat) if new_pos == "RB" else 0,
                        "rec_yards": int(new_stat) if new_pos == "WR" else 0
                    }
                    # Send to Supabase
                    supabase.table("player_game_logs").insert(payload).execute()
                    st.success(f"🎉 Successfully saved stat log for {new_name} into your live database!")
                    st.toast("Database updated!")

except Exception as e:
    st.error("❌ The dashboard server hit an obstacle while handshaking with Supabase.")
    st.code(e)
