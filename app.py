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
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA" # <-- Put your real long 'eyJ...' key inside these quotes
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # 2. --- FETCH DATA FROM DATABASE ---
    response = supabase.table("player_game_logs").select("*").execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        st.warning("⚠️ Connected to Supabase, but your table appears to be empty! Make sure your loader pipeline ran successfully.")
    else:
        # 3. --- SIDEBAR FILTER CONTROLS ---
        st.sidebar.header("🎯 Analytics Controls")
        available_players = df["player_name"].unique()
        selected_player = st.sidebar.selectbox("Select Player", available_players)
        
        # Filter and sort data cleanly for the selected player
        player_df = df[df["player_name"] == selected_player].sort_values(by="week")
        
        # 4. --- DETECT PLAYER POSITION STAT TYPE ---
        # Isolate if they are primarily a QB or WR based on non-zero stats
        is_qb = any(player_df["pass_yards"] > 0) if "pass_yards" in player_df.columns else False
        is_wr = any(player_df["rec_yards"] > 0) if "rec_yards" in player_df.columns else False
        
        if is_qb:
            stat_col, label_name, max_val, default_val = "pass_yards", "Passing Yards", 500.0, 300.0
        elif is_wr:
            stat_col, label_name, max_val, default_val = "rec_yards", "Receiving Yards", 250.0, 85.5
        else:
            stat_col, label_name, max_val, default_val = "rush_yards", "Rushing Yards", 300.0, 120.5

        # Interactive line selection slider
        prop_line = st.sidebar.slider(f"Set Sportsbook Line ({label_name})", 0.0, max_val, default_val, 0.5)
        
        # 5. --- CALCULATE PERFORMANCE METRICS ---
        total_games = len(player_df)
        avg_stat = player_df[stat_col].mean()
        median_stat = player_df[stat_col].median()
        overs = player_df[player_df[stat_col] > prop_line]
        over_pct = (len(overs) / total_games * 100) if total_games > 0 else 0
        
        # Render Metrics Grid
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Games Logged", f"{total_games}")
        c2.metric("Season Average", f"{avg_stat:.1f} yds")
        c3.metric("Season Median", f"{median_stat:.1f} yds")
        c4.metric("OVER Hit Rate 📈", f"{over_pct:.1f}%", delta=f"{len(overs)} Games")
        
        # 6. --- RENDERING DETAILED CHART ---
        st.markdown(f"### 📊 Historical {label_name} vs Line")
        
        # Assign bright green for passing the line and red for going under
        player_df["Result"] = player_df[stat_col].apply(lambda x: "🟢 OVER" if x > prop_line else "🔴 UNDER")
        
        fig = px.bar(
            player_df, x="opponent", y=stat_col, color="Result",
            color_discrete_map={"🟢 OVER": "#2ecc71", "🔴 UNDER": "#e74c3c"}, text=stat_col,
            labels={stat_col: label_name, "opponent": "Opponent"}
        )
        
        # Draw a horizontal dash line at the sportsbook mark
        fig.add_hline(y=prop_line, line_dash="dash", line_color="#34495e", annotation_text=f"Line: {prop_line}")
        fig.update_layout(yaxis_range=[0, max(player_df[stat_col].max() + 30, prop_line + 30)])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 7. --- RAW DATA GRID SPREADSHEET ---
        st.markdown("### 📄 Raw Database Slice")
        st.dataframe(player_df[["season", "week", "opponent", stat_col]], use_container_width=True)

except Exception as e:
    st.error("❌ The dashboard server hit an obstacle while handshaking with Supabase.")
    st.info("Check your credential block key strings to ensure there are no missing characters.")
    st.code(e)
