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

# Mapping of FBS College Football teams to logo URLs
FBS_LOGOS = {
    "Alabama": "https://a.espncdn.com/i/teamlogos/ncaa/500/333.png",
    # Add the rest of your 138 FBS team logo URLs here
}

def get_team_logo(team_name):
    return FBS_LOGOS.get(team_name, "")
# Secure connection setup
SUPABASE_URL = "https://parwalgtnfgzwaibjpoz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBhcndhbGd0bmZnendhaWJqcG96Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgyMDY2NDksImV4cCI6MjEwMzc4MjY0OX0.ZJmfo07gK_u4aEDPSDTipK3i1pG4Zju0HQa_bofVkDA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# BRANDING DICTIONARY MAP
# BRANDING DICTIONARY MAP
TEAM_BRANDING = {
    # SEC
    "Alabama": {"primary": "#9E1B32", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/333.png"},
    "Arkansas": {"primary": "#9D2235", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/8.png"},
    "Auburn": {"primary": "#0C2340", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2.png"},
    "Florida": {"primary": "#0021A5", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/57.png"},
    "Georgia": {"primary": "#BA0C2F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/61.png"},
    "Kentucky": {"primary": "#0033A0", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/96.png"},
    "LSU": {"primary": "#461D7C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/99.png"},
    "Mississippi State": {"primary": "#660000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/344.png"},
    "Missouri": {"primary": "#F1B82D", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/142.png"},
    "Oklahoma": {"primary": "#841617", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/201.png"},
    "Ole Miss": {"primary": "#CE1126", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/145.png"},
    "South Carolina": {"primary": "#73000A", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2579.png"},
    "Tennessee": {"primary": "#FF8200", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2633.png"},
    "Texas": {"primary": "#BF5700", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/251.png"},
    "Texas A&M": {"primary": "#500000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/245.png"},
    "Vanderbilt": {"primary": "#866D4B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/238.png"},

    # BIG TEN
    "Illinois": {"primary": "#13294B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/356.png"},
    "Indiana": {"primary": "#990000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/84.png"},
    "Iowa": {"primary": "#FFCD00", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2294.png"},
    "Maryland": {"primary": "#E21833", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/120.png"},
    "Michigan": {"primary": "#00274C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/130.png"},
    "Michigan State": {"primary": "#18453B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/127.png"},
    "Minnesota": {"primary": "#7A0019", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/135.png"},
    "Nebraska": {"primary": "#E31837", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/158.png"},
    "Northwestern": {"primary": "#4E2A84", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/77.png"},
    "Ohio State": {"primary": "#BB0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/194.png"},
    "Oregon": {"primary": "#154734", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2483.png"},
    "Penn State": {"primary": "#041E42", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/213.png"},
    "Purdue": {"primary": "#CEB888", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2509.png"},
    "Rutgers": {"primary": "#CC0033", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/164.png"},
    "UCLA": {"primary": "#2D68C4", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/26.png"},
    "USC": {"primary": "#990000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/30.png"},
    "Washington": {"primary": "#4B2E83", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/264.png"},
    "Wisconsin": {"primary": "#C5050C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/275.png"},

    # ACC
    "Boston College": {"primary": "#98002E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/103.png"},
    "California": {"primary": "#003262", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/25.png"},
    "Clemson": {"primary": "#F56600", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/228.png"},
    "Duke": {"primary": "#003087", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/150.png"},
    "Florida State": {"primary": "#78243C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/52.png"},
    "Georgia Tech": {"primary": "#B3A369", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/59.png"},
    "Louisville": {"primary": "#AD0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/97.png"},
    "Miami": {"primary": "#F47321", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2390.png"},
    "NC State": {"primary": "#CC0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/152.png"},
    "North Carolina": {"primary": "#7BAFD4", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/153.png"},
    "Pitt": {"primary": "#003594", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/221.png"},
    "SMU": {"primary": "#CC0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2567.png"},
    "Stanford": {"primary": "#8C1515", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/24.png"},
    "Syracuse": {"primary": "#D44500", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/183.png"},
    "Virginia": {"primary": "#232D4B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/258.png"},
    "Virginia Tech": {"primary": "#630031", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/259.png"},
    "Wake Forest": {"primary": "#9E7E38", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/154.png"},

    # BIG 12
    "Arizona": {"primary": "#CC0033", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/12.png"},
    "Arizona State": {"primary": "#8C1D40", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/9.png"},
    "Baylor": {"primary": "#154734", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/239.png"},
    "BYU": {"primary": "#002E5D", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/252.png"},
    "Cincinnati": {"primary": "#E00122", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2132.png"},
    "Colorado": {"primary": "#CFB87C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/38.png"},
    "Houston": {"primary": "#C8102E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/248.png"},
    "Iowa State": {"primary": "#C8102E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/66.png"},
    "Kansas": {"primary": "#0051BA", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2305.png"},
    "Kansas State": {"primary": "#512888", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2306.png"},
    "Oklahoma State": {"primary": "#FF6600", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/197.png"},
    "TCU": {"primary": "#4D1979", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2628.png"},
    "Texas Tech": {"primary": "#CC0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2641.png"},
    "UCF": {"primary": "#BA9B37", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2116.png"},
    "Utah": {"primary": "#CC0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/254.png"},
    "West Virginia": {"primary": "#002855", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/277.png"},

    # GROUP OF 5 / INDEPENDENTS
    "Air Force": {"primary": "#003087", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2005.png"},
    "Akron": {"primary": "#041E42", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2006.png"},
    "Appalachian State": {"primary": "#222222", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2026.png"},
    "Arkansas State": {"primary": "#E81018", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2032.png"},
    "Army": {"primary": "#D4BF91", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/349.png"},
    "Ball State": {"primary": "#BA0C2F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2050.png"},
    "Boise State": {"primary": "#0033A0", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/68.png"},
    "Bowling Green": {"primary": "#4F2C1D", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2084.png"},
    "Buffalo": {"primary": "#005BBB", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2083.png"},
    "Central Michigan": {"primary": "#6A0032", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2117.png"},
    "Charlotte": {"primary": "#005035", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2429.png"},
    "Coastal Carolina": {"primary": "#006F71", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/324.png"},
    "Colorado State": {"primary": "#1E4D2B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/36.png"},
    "East Carolina": {"primary": "#592A8A", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/151.png"},
    "Eastern Michigan": {"primary": "#006633", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2199.png"},
    "FAU": {"primary": "#003366", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2226.png"},
    "FIU": {"primary": "#081E3F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2229.png"},
    "Fresno State": {"primary": "#DB0032", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/278.png"},
    "Georgia Southern": {"primary": "#011E41", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/290.png"},
    "Georgia State": {"primary": "#0039A6", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2247.png"},
    "Hawaii": {"primary": "#024731", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/62.png"},
    "Jacksonville State": {"primary": "#CC0000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/55.png"},
    "James Madison": {"primary": "#450084", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/256.png"},
    "Kennesaw State": {"primary": "#FFC629", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/338.png"},
    "Kent State": {"primary": "#002664", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2309.png"},
    "Liberty": {"primary": "#00205B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2335.png"},
    "Louisiana": {"primary": "#CE181E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/202.png"},
    "Louisiana Tech": {"primary": "#002F6C", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2348.png"},
    "Marshall": {"primary": "#00B140", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/276.png"},
    "Memphis": {"primary": "#003087", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/235.png"},
    "Miami (OH)": {"primary": "#B80000", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/193.png"},
    "Middle Tennessee": {"primary": "#0066CC", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2393.png"},
    "Navy": {"primary": "#00205B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2426.png"},
    "Nevada": {"primary": "#003366", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2440.png"},
    "New Mexico": {"primary": "#BA0C2F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/167.png"},
    "New Mexico State": {"primary": "#862633", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/166.png"},
    "North Texas": {"primary": "#00853D", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/249.png"},
    "Northern Illinois": {"primary": "#BA0C2F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2459.png"},
    "Notre Dame": {"primary": "#0C2340", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/87.png"},
    "Ohio": {"primary": "#00693E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/195.png"},
    "Old Dominion": {"primary": "#003057", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/295.png"},
    "Oregon State": {"primary": "#DC4405", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/204.png"},
    "Rice": {"primary": "#00205B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/242.png"},
    "Sam Houston": {"primary": "#F05A28", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2534.png"},
    "San Diego State": {"primary": "#A6192E", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/21.png"},
    "San Jose State": {"primary": "#0055A5", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/23.png"},
    "South Alabama": {"primary": "#00205B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/6.png"},
    "South Florida": {"primary": "#006747", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/58.png"},
    "Southern Miss": {"primary": "#FFAA00", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2572.png"},
    "Temple": {"primary": "#9D2235", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/218.png"},
    "Texas State": {"primary": "#501214", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/326.png"},
    "Toledo": {"primary": "#152B52", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2649.png"},
    "Troy": {"primary": "#8A2432", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2653.png"},
    "Tulane": {"primary": "#006747", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2655.png"},
    "Tulsa": {"primary": "#002D62", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2020.png"},
    "UAB": {"primary": "#006341", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/5.png"},
    "UConn": {"primary": "#000E2F", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/41.png"},
    "UL Monroe": {"primary": "#231F20", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2433.png"},
    "UNLV": {"primary": "#CF142B", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2439.png"},
    "UTEP": {"primary": "#FF6600", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2638.png"},
    "UTSA": {"primary": "#F15A22", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2636.png"},
    "Utah State": {"primary": "#00263A", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/328.png"},
    "Washington State": {"primary": "#981E32", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/265.png"},
    "Western Kentucky": {"primary": "#E31837", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/98.png"},
    "Western Michigan": {"primary": "#5C1300", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2711.png"},
    "Wyoming": {"primary": "#492F24", "logo": "http://a.espncdn.com/i/teamlogos/ncaa/500/2751.png"},
}

DEFAULT_BRAND = {"primary": "#1e293b", "logo": "https://a.espncdn.com/i/teamlogos/ncaa/500/ncaa.png"}

def get_team_logo(team_name):
    brand = TEAM_BRANDING.get(team_name, DEFAULT_BRAND)
    return brand.get("logo", DEFAULT_BRAND["logo"])

def pct_to_american_odds(percentage):
    if percentage >= 100: return "-10000"
    if percentage <= 0: return "+10000"
    if percentage > 50:
        return f"{int(-((percentage) / (100 - percentage)) * 100)}"
    return f"+{int(((100 - percentage) / percentage) * 100)}"

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
    def fetch_all_player_game_logs():
        all_rows = []
        page_size = 10000
        start = 0

        while True:
            response = (
                supabase.table("player_game_logs")
                .select("*")
                .range(start, start + page_size - 1)
                .execute()
            )
            rows = response.data or []
            if not rows:
                break

            all_rows.extend(rows)
            if len(rows) < page_size:
                break

            start += page_size

        return pd.DataFrame(all_rows)

    df = fetch_all_player_game_logs()

    if df.empty:
        st.warning("🔄 Table layout established on live server. Awaiting records...")
    else:
        raw_cols = ["pass_yards", "pass_cmp", "pass_att", "pass_tds", "pass_int", "rush_att", "rush_yards", "rush_tds", "rec_yards", "receptions", "rec_tds"]
        for c in raw_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c]).fillna(0).astype(int)
            else:
                df[c] = 0

        df["total_offense"] = df["pass_yards"] + df["rush_yards"]
        df["total_scrimmage"] = df["rush_yards"] + df["rec_yards"]

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

            # ==================== ADD BLOCK 2 HERE ====================
            if selected_team:
                col_logo, col_title = st.columns([1, 6])
                with col_logo:
                    logo_url = get_team_logo(selected_team)
                    if logo_url:
                        st.image(logo_url, width=60)
                with col_title:
                    st.subheader(f"{selected_team} Performance Analysis")
            # =========================================================
            
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
                    brand_color = brand.get("primary", "#1e293b")
                    logo_url = brand.get("logo", DEFAULT_BRAND["logo"])
                    
                    col_logo, col_title = st.columns([1, 8])
                    with col_logo:
                        st.image(logo_url, width=45)
                    with col_title:
                        st.markdown(f"<h3 style='color: {brand_color}; margin:0;'>{selected_player.upper()}</h3>", unsafe_allow_html=True)
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
                # Fetch upcoming matchups directly from the normalized SQL View
                sched_resp = supabase.table("normalized_upcoming_schedule").select("*").limit(10000).execute()
                sched_df = pd.DataFrame(sched_resp.data)
        
                if sched_df.empty:
                    st.warning("⚠️ No upcoming games logged in your 'normalized_upcoming_schedule' view yet.")
                else:
                    c_year, c_week = st.columns(2)
                    
                    with c_year:
                        sched_years = sorted(sched_df["season"].unique(), reverse=True) if "season" in sched_df.columns else [selected_year]
                        slate_year = st.selectbox("📅 Schedule Season", sched_years, key="slate_year_sel")
                    
                    season_sched = sched_df[sched_df["season"] == slate_year] if "season" in sched_df.columns else sched_df
                    
                    with c_week:
                        available_weeks = sorted(season_sched["week"].unique()) if "week" in season_sched.columns else []
                        selected_week = st.selectbox("🏈 Upcoming Slate Week", available_weeks, key="slate_week_sel") if available_weeks else 1
                    
                    # Filter schedule down to the selected slate week
                    normalized_schedule = season_sched[season_sched["week"] == selected_week] if "week" in season_sched.columns else season_sched

                    # Common CFB Team Name Abbreviations Mapping
                    name_map = {
                        "Fresno St": "Fresno State", "Fresno St.": "Fresno State",
                        "Florida St": "Florida State", "Florida St.": "Florida State",
                        "Ohio St": "Ohio State", "Ohio St.": "Ohio State",
                        "Penn St": "Penn State", "Penn St.": "Penn State",
                        "Mich St": "Michigan State", "Mich St.": "Michigan State",
                        "App St": "Appalachian State", "App St.": "Appalachian State",
                        "San Jose St": "San Jose State", "San Jose St.": "San Jose State",
                        "Boise St": "Boise State", "Boise St.": "Boise State",
                        "N.C. State": "NC State", "North Carolina St": "NC State",
                        "Usc": "USC", "Ucla": "UCLA", "Smu": "SMU", "Ucf": "UCF", "Lsu": "LSU", "Ole Miss": "Mississippi"
                    }

                    def clean_team_name(series):
                        s = series.astype(str).str.strip().str.title()
                        return s.replace(name_map)

                    # Standardize team strings before selecting historical fallbacks.
                    normalized_schedule["team_clean"] = clean_team_name(normalized_schedule["team"])
                    normalized_schedule["opponent_clean"] = clean_team_name(normalized_schedule["opponent"])
        
                    # --- SEASON FALLBACK LOGIC ---
                    # Use the selected season where available, then fall back per scheduled team.
                    current_hist_df = df[df["season"] == slate_year].copy() if "season" in df.columns else pd.DataFrame()
                    historical_frames = [current_hist_df]
                    fallback_years = {}
                    scheduled_teams = set(normalized_schedule["team_clean"]).union(normalized_schedule["opponent_clean"])

                    for scheduled_team in scheduled_teams:
                        has_current_data = (
                            clean_team_name(current_hist_df["team"]).eq(scheduled_team).any()
                            or clean_team_name(current_hist_df["opponent"]).eq(scheduled_team).any()
                        ) if not current_hist_df.empty else False
                        if has_current_data:
                            continue

                        team_history = df[
                            clean_team_name(df["team"]).eq(scheduled_team)
                            | clean_team_name(df["opponent"]).eq(scheduled_team)
                        ] if "season" in df.columns else pd.DataFrame()
                        if not team_history.empty:
                            fallback_year = team_history["season"].max()
                            historical_frames.append(team_history[team_history["season"] == fallback_year])
                            fallback_years[scheduled_team] = fallback_year

                    hist_df = pd.concat(historical_frames, ignore_index=True).drop_duplicates()
                    if fallback_years:
                        fallback_details = ", ".join(f"{team}: {year}" for team, year in sorted(fallback_years.items()))
                        st.info(f"ℹ️ Using selected-season logs where available; team-specific historical fallbacks: {fallback_details}.")
        
                   # Calculate Offensive and Defensive averages per game from player logs
                    if not hist_df.empty:
                        # Standardize team strings across logs and schedule
                        hist_df["team_clean"] = clean_team_name(hist_df["team"])
                        hist_df["opp_clean"] = clean_team_name(hist_df["opponent"])
        
                        # 1. Offensive Production per game
                        game_offense = hist_df.groupby(["team_clean", "opp_clean", "week"]).agg(
                            total_pass_yds=("pass_yards", "sum"),
                            total_rush_yds=("rush_yards", "sum")
                        ).reset_index()
        
                        off_df = game_offense.groupby("team_clean").agg(
                            pass_yds_gained=("total_pass_yds", "mean"),
                            rush_yds_gained=("total_rush_yds", "mean")
                        ).reset_index()
        
                        # 2. Defensive Yards Surrendered per game
                        def_df = game_offense.groupby("opp_clean").agg(
                            pass_yds_allowed=("total_pass_yds", "mean"),
                            rush_yds_allowed=("total_rush_yds", "mean")
                        ).reset_index().rename(columns={"opp_clean": "opponent_clean"})
                    else:
                        off_df = pd.DataFrame(columns=["team_clean", "pass_yds_gained", "rush_yds_gained"])
                        def_df = pd.DataFrame(columns=["opponent_clean", "pass_yds_allowed", "rush_yds_allowed"])
        
                    # Rank teams
                    def_df["Pass_Def_Rank"] = def_df["pass_yds_allowed"].rank(ascending=True).fillna(99).astype(int)
                    def_df["Rush_Def_Rank"] = def_df["rush_yds_allowed"].rank(ascending=True).fillna(99).astype(int)
                    off_df["Pass_Off_Rank"] = off_df["pass_yds_gained"].rank(ascending=False).fillna(99).astype(int)
                    off_df["Rush_Off_Rank"] = off_df["rush_yds_gained"].rank(ascending=False).fillna(99).astype(int)
        
                    # Join schedule with team rankings
                    matchup_summary = pd.merge(normalized_schedule, def_df, on="opponent_clean", how="left")
                    matchup_summary = pd.merge(matchup_summary, off_df, on="team_clean", how="left")
        
                    # Fallbacks for FCS/Unmatched teams using median values
                    avg_pass_def = def_df["pass_yds_allowed"].median() if not def_df.empty else 220
                    avg_rush_def = def_df["rush_yds_allowed"].median() if not def_df.empty else 150
        
                    matchup_summary["pass_yds_allowed"] = matchup_summary["pass_yds_allowed"].fillna(avg_pass_def)
                    matchup_summary["rush_yds_allowed"] = matchup_summary["rush_yds_allowed"].fillna(avg_rush_def)
                    matchup_summary["pass_yds_gained"] = matchup_summary["pass_yds_gained"].fillna(0)
                    matchup_summary["rush_yds_gained"] = matchup_summary["rush_yds_gained"].fillna(0)
        
                    matchup_summary["Pass_Def_Rank"] = matchup_summary["Pass_Def_Rank"].fillna(65).astype(int)
                    matchup_summary["Rush_Def_Rank"] = matchup_summary["Rush_Def_Rank"].fillna(65).astype(int)
                    matchup_summary["Pass_Off_Rank"] = matchup_summary["Pass_Off_Rank"].fillna(65).astype(int)
                    matchup_summary["Rush_Off_Rank"] = matchup_summary["Rush_Off_Rank"].fillna(65).astype(int)
        
                    # Calculate Net Advantage Scores
                    matchup_summary["Net_Pass_Edge"] = matchup_summary["Pass_Def_Rank"] - matchup_summary["Pass_Off_Rank"]
                    matchup_summary["Net_Rush_Edge"] = matchup_summary["Rush_Def_Rank"] - matchup_summary["Rush_Off_Rank"]
        
                    # Clean null values for unranked teams
                    fill_cols = ["pass_yds_allowed", "rush_yds_allowed", "pass_yds_gained", "rush_yds_gained"]
                    for col in fill_cols:
                        if col in matchup_summary.columns:
                            matchup_summary[col] = matchup_summary[col].fillna(0)
                    
                    matchup_summary["Pass_Def_Rank"] = matchup_summary["Pass_Def_Rank"].fillna(99).astype(int)
                    matchup_summary["Rush_Def_Rank"] = matchup_summary["Rush_Def_Rank"].fillna(99).astype(int)
                    matchup_summary["Pass_Off_Rank"] = matchup_summary["Pass_Off_Rank"].fillna(99).astype(int)
                    matchup_summary["Rush_Off_Rank"] = matchup_summary["Rush_Off_Rank"].fillna(99).astype(int)
        
                    # Calculate Net Advantage Scores (Higher Net Edge = Weak Defense vs Strong Offense)
                    matchup_summary["Net_Pass_Edge"] = matchup_summary["Pass_Def_Rank"] - matchup_summary["Pass_Off_Rank"]
                    matchup_summary["Net_Rush_Edge"] = matchup_summary["Rush_Def_Rank"] - matchup_summary["Rush_Off_Rank"]
        
                    # UI Display - Top Mismatch Cards
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
                            st.info("No prior passing statistics available for this slate's teams.")
        
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
                            st.info("No prior rushing statistics available for this slate's teams.")
        
                    # UI Display - Full Matrix Table
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
                st.error("⚠️ An unexpected issue occurred while rendering the slate scanner.")
                st.code(e)

except Exception as global_e:
    st.error("⚠️ Failed to load database logs.")
    st.code(global_e)
