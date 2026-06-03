import streamlit as st
import pandas as pd
# Make sure helper.py exists in the same folder or remove/replace its usage
try:
    import helper 
except ImportError:
    st.warning("Warning: 'helper.py' not found. Some functions might be unavailable.")
    helper = None # Set helper to None to avoid errors later

from PIL import Image
import os
import json
import logging
from pathlib import Path
import plotly.express as px

# --- Page & Path Configuration ---
st.set_page_config(page_title="IPL Data Analysis", layout="wide", initial_sidebar_state="expanded")

# --- Directory Paths (Cleaned) ---
CWD = Path.cwd() 
CSV_DIR = CWD / "csv"
IMAGE_DIR = CWD / "images"
AUDIO_FILE = CWD / "audio" / "IPL-theme-RMX.wav"
PLAYER_DATA_DIR = CWD / "IPL - Player Performance Dataset"

# CSV file paths (Cleaned)
MATCHES_CSV_PATH = CSV_DIR / "matches.csv"
TEAMS_CSV_PATH = CSV_DIR / "teams_info.csv"

# --- Session State for Login ---
if 'login' not in st.session_state:
    st.session_state['login'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

# --- Users (username: password) ---
users = {
    "samarth": "samarth123",
    "tejashree": "tejashree",
    "ramesh": "ramesh123",
    "priya": "priya123",
    "amit": "amit123"
}

# --- Data Loading Functions ---
# @st.cache_resource # This function is likely not needed if you provide matches.csv
# def run_data_processing():
#     # ... (code for processing JSON files - commented out as likely unused)
#     pass

@st.cache_data
def load_data(matches_path, teams_path):
    matches_df = None # Initialize
    teams_df = None # Initialize

    try:
        # --- TRY SPECIFYING ENCODING ---
        try:
            # Try UTF-8 first
            matches_df = pd.read_csv(matches_path, engine='python', encoding='utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try Latin-1 (common on Windows)
            st.warning("UTF-8 encoding failed for matches.csv, trying Latin-1...")
            matches_df = pd.read_csv(matches_path, engine='python', encoding='latin-1')
        # --- End of Encoding Fix ---
            
    except FileNotFoundError:
        st.error(f"❌ CRITICAL ERROR: 'matches.csv' not found at {matches_path}.")
        return None, None # Must return two values
    except Exception as e:
        st.error(f"Error loading matches.csv: {e}")
        return None, None # Must return two values

    try:
        if teams_path.is_file(): # Check if the teams file exists
             try:
                 teams_df = pd.read_csv(teams_path, engine='python', encoding='utf-8')
             except UnicodeDecodeError:
                 st.warning("UTF-8 encoding failed for teams_info.csv, trying Latin-1...")
                 teams_df = pd.read_csv(teams_path, engine='python', encoding='latin-1')
        else:
             st.warning(f"Note: 'teams_info.csv' not found at {teams_path}. Team logos will not be shown.")
    except Exception as e:
        st.warning(f"Error loading teams_info.csv: {e}. Team logos may not show.")
        
    # Proceed only if matches_df was loaded successfully
    if matches_df is None:
        return None, None 

    try:
        # --- Data Cleaning & Preparation ---
        if 'date' not in matches_df.columns and 'Date' in matches_df.columns:
             matches_df.rename(columns={'Date': 'date'}, inplace=True)
        elif 'date' not in matches_df.columns:
             st.error("CRITICAL ERROR: Could not find a 'date' or 'Date' column in matches.csv.")
             return None, None # Cannot proceed without date

        # Handle mixed date formats robustly
        try:
            # Clean strings first (remove extra spaces)
            matches_df['date'] = matches_df['date'].astype(str).str.strip() 
            # --- DATE PARSING FIX ---
            matches_df['date'] = pd.to_datetime(matches_df['date'], format='mixed', dayfirst=True, errors='coerce')
            # --- End of Date Parsing Fix ---
        except Exception as date_err: # Catch broader errors during conversion
             st.error(f"Error parsing dates in 'matches.csv' even with mixed format: {date_err}")
             st.info("Please check the CSV file for unexpected characters or formats in the date column.")
             return None, None

        # Check for rows where date conversion failed AFTER attempting conversion
        failed_dates = matches_df['date'].isna().sum()
        if failed_dates > 0:
            st.warning(f"{failed_dates} rows had date values that could not be parsed and were ignored.")

        if 'Season' not in matches_df.columns:
            # Create Season based on year, handle NaT dates
            valid_mask = matches_df['date'].notna()
            matches_df.loc[valid_mask, 'Season_Year'] = matches_df.loc[valid_mask, 'date'].dt.year
            matches_df['Season_Year'] = matches_df['Season_Year'].fillna(0).astype(int) 
            matches_df['Season'] = 'IPL-' + matches_df['Season_Year'].astype(str)
            matches_df.loc[matches_df['Season_Year'] == 0, 'Season'] = 'IPL-UnknownDate' 
            matches_df.drop(columns=['Season_Year'], inplace=True)
        
        return matches_df, teams_df
        
    except Exception as e:
        st.error(f"Error processing data after loading: {e}")
        return None, None

# --- Custom CSS (Cleaned Up) ---
st.markdown(
    """
    <style>
    /* --- HIDE STREAMLIT UI ELEMENTS --- */
    [data-testid="stDeployButton"] { display: none; }
    [data-testid="stToolbar"] { visibility: hidden !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* --- Global Styles --- */
    :root {
        --primary-blue: #19388A; --accent-blue: #4F91CD; --accent-orange: #FF5722;
        --accent-yellow: #FFCA28; --background-light: #F0F2F5; --text-color: #333333;
        --font-family: 'Roboto', sans-serif;
    }
    .main { background-color: var(--background-light); color: var(--text-color); font-family: var(--font-family); }
    
    /* --- Top Navigation Bar --- */
    .top-nav { background: linear-gradient(135deg, var(--primary-blue), var(--accent-blue)); padding: 10px 20px;
        display: flex; justify-content: space-between; align-items: center; color: white; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
    .top-nav h1 { margin: 0; font-size: 1.8em; }
    .top-nav .user-info { font-size: 1em; }
    
    /* --- Sidebar Styles --- */
    .sidebar .sidebar-content { background-color: var(--primary-blue); color: white; }
    .sidebar h2 { color: var(--accent-yellow); }
    
    /* --- Stat Cards --- */
    .stat-card { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; margin: 10px; }
    .stat-card h3 { color: var(--primary-blue); margin: 0 0 10px; }
    .stat-card p { font-size: 2em; color: var(--accent-yellow); margin: 0; }
    .stat-card .win-percentage { font-size: 1em; color: var(--text-color); display: block; margin-top: 2px; }
    
    /* --- Chart Containers --- */
    .chart-container { background: white; border-radius: 8px; padding: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin: 20px 0; }
    
    /* --- Responsive Grid --- */
    @media (min-width: 768px) { .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; } }
    
    /* --- Login Page Styles --- */
    .login-container { width: 100%; padding: 10px; background: linear-gradient(135deg, var(--primary-blue), var(--accent-orange)); border-radius: 15px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); text-align: center; color: #fff; margin-bottom: 10px; }
    .stTextInput > div > div > input { border-radius: 5px; padding: 5px; background-color: #fff; border: 1px solid #ccc; color: #333; font-size: 0.9em; }
    
    /* Styles all buttons */
    .stButton > button { background-color: var(--accent-orange); color: white; border-radius: 8px; padding: 8px 16px; font-weight: bold; width: 100%; margin-top: 8px; }
    .stButton > button:hover { background-color: #E64A19; }
    
    </style>
    """,
    unsafe_allow_html=True
)

# --- LOGIN PAGE ---
if not st.session_state['login']:
    
    col1, col2, col3 = st.columns([1, 1, 1]) 

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #fff; font-size: 1.3em;'>🔐 IPL Login</h1>", unsafe_allow_html=True)
        # Check if login image exists
        login_img_path = IMAGE_DIR / "1.png"
        if login_img_path.is_file():
            st.image(str(login_img_path), width=120)
        else:
            st.warning("Login image 'images/1.png' not found.")
        st.markdown("</div>", unsafe_allow_html=True) 
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("Login")

    if login_btn:
        if username in users and password == users[username]:
            st.session_state['login'] = True
            st.session_state['username'] = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            with col2:
                st.error("❌ Username or password is incorrect")
else:
    # --- DASHBOARD PAGE ---

    # --- Top Navigation Bar ---
    st.markdown(
        f"""
        <div class='top-nav'>
            <h1>🏆 IPL Cricket Dashboard</h1>
            <div class='user-info'>Welcome, {st.session_state['username']}!</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Data Loading ---
    # run_data_processing() # Commented out - assuming CSVs exist
    df, teams_df = load_data(MATCHES_CSV_PATH, TEAMS_CSV_PATH)
    if df is None: 
        # Error message is already shown in load_data
        st.stop() # Stop the script if data loading fails

    # --- Pre-calculate lists for sidebar ---
    try:
        team_names_list = sorted(pd.concat([df['team1'], df['team2']]).dropna().unique())
        seasons_list = sorted(df['Season'].unique(), reverse=True)
    except KeyError as e:
         st.error(f"CRITICAL ERROR: Missing expected column in 'matches.csv': {e}. Cannot build sidebar filters.")
         st.stop()
         
    player_stat_categories = [
        "Most Runs", "Most Wickets", "Fastest Fifties", "Fastest Centuries",
        "Best Bowling Economy Innings", "Best Bowling Strike Rate Innings",
        "Most Dot Balls Innings", "Most Fours Innings", "Most Sixes Innings",
        "Most Runs Conceded Innings", "Most Runs Over"
    ]
    # Ensure the PLAYER_DATA_DIR exists before listing years based on it
    player_data_years = []
    if PLAYER_DATA_DIR.is_dir():
         # Dynamically find years based on subfolder contents if possible, otherwise use fixed range
         # For simplicity, using fixed range for now
         player_data_years = [str(y) for y in range(2022, 2007, -1)] 
    else:
         st.sidebar.warning(f"Player data directory not found at: {PLAYER_DATA_DIR}")


    # --- Sidebar ---
    with st.sidebar:
        # Check if sidebar image exists
        sidebar_img_path = IMAGE_DIR / "1.png"
        if sidebar_img_path.is_file():
             st.image(str(sidebar_img_path), width=150)
        #st.header("Navigation")
        
        # --- Main Navigation ---
        analysis_type = st.radio(
            "Choose Analysis Type",
            ("Overall Analysis", "Season-wise Analysis", "Team-wise Analysis", "Player Analysis"),
            key="main_nav"
        )
        
        st.markdown("---") # Separator

        # --- Conditional Filters ---
        # Initialize variables to avoid NameError if a section isn't selected first
        options = []
        selected_season = None
        selected_team = None
        selected_team_season = None
        selected_player_stat = None
        selected_player_year = None
        
        if analysis_type == "Overall Analysis":
            st.header("Overall Filters")
            options = st.multiselect(
                "Select analyses to display:",
                ["Total Matches Per Season", "Team Performance", "Top Players", "Toss Statistics"],
                default=["Total Matches Per Season", "Team Performance"]
            )
        
        if analysis_type == "Season-wise Analysis":
            st.header("Season Filters")
            if seasons_list:
                 selected_season = st.selectbox("Select a Season", seasons_list, key="season_select")
            else:
                 st.warning("No seasons found in data.")

        if analysis_type == "Team-wise Analysis":
            st.header("Team Filters")
            if team_names_list:
                selected_team = st.selectbox("Select a Team", team_names_list, key="team_select")
            else:
                 st.warning("No teams found in data.")
            if seasons_list:
                selected_team_season = st.selectbox("Select a Season", seasons_list, key="team_season_select")
            else:
                 st.warning("No seasons found for team filtering.")


        if analysis_type == "Player Analysis":
            st.header("Player Filters")
            if player_stat_categories:
                 selected_player_stat = st.selectbox("Select a Statistic", player_stat_categories, key="player_stat_select")
            else:
                 st.warning("No player stat categories defined.")
            if player_data_years:
                 selected_player_year = st.selectbox("Select a Year", player_data_years, key="player_year_select")
            else:
                 st.warning("Could not determine years for player data. Check PLAYER_DATA_DIR.")


        # --- Logout and Audio ---
        st.markdown("---")
        if st.button('▶️ Play Theme Song'):
            if AUDIO_FILE.is_file(): 
                 st.audio(str(AUDIO_FILE))
            else: 
                 st.sidebar.warning(f"Audio file not found at {AUDIO_FILE}")
            
        if st.button("Logout"):
            st.session_state['login'] = False
            st.session_state['username'] = None
            st.rerun()

    # --- Main Content Area ---
    st.header(f"IPL Dashboard: {analysis_type}") # Dynamic Header

    # --- Render Main Content Based on Navigation ---
    
    if analysis_type == "Overall Analysis":
        
        # Key Stats Cards
        st.markdown("<div class='grid'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            total_matches = df.shape[0]
            st.markdown(f"<div class='stat-card'><h3>Total Matches</h3><p>{total_matches}</p></div>", unsafe_allow_html=True)
        with col2:
            # Calculate total unique teams that have ever won
            total_unique_winners = df['winner'].nunique() if 'winner' in df.columns else 0
            st.markdown(f"<div class='stat-card'><h3>Unique Winning Teams (All Time)</h3><p>{total_unique_winners}</p></div>", unsafe_allow_html=True)

        with col3:
            top_player = "N/A" # Default
            if 'player_of_match' in df.columns and helper and callable(getattr(helper, "pom", None)):
                 pom_series = helper.pom(df)
                 if not pom_series.empty:
                     top_player = pom_series.index[0]
            st.markdown(f"<div class='stat-card'><h3>Top Player (Most Awards)</h3><p>{top_player}</p></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Charts based on multiselect
        st.subheader("Overall IPL Statistics")
        if "Total Matches Per Season" in options:
             if helper and callable(getattr(helper, "match_per_season", None)):
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(helper.match_per_season(df), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
             else: st.warning("'helper.match_per_season' function not found.")
        if "Team Performance" in options:
            if helper and callable(getattr(helper, "winners", None)):
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(helper.winners(df), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else: st.warning("'helper.winners' function not found.")
        if "Top Players" in options:
            if 'player_of_match' in df.columns and helper and callable(getattr(helper, "pom", None)):
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.dataframe(helper.pom(df).head(15))
                st.markdown("</div>", unsafe_allow_html=True)
            elif 'player_of_match' not in df.columns:
                 st.warning("Cannot show 'Top Players' as 'player_of_match' column is missing from matches.csv.")
            else:
                 st.warning("'helper.pom' function not found.")

        if "Toss Statistics" in options:
            if ('toss_winner' in df.columns and 'toss_decision' in df.columns and 
                helper and callable(getattr(helper, "toss_winner_count", None)) and 
                helper and callable(getattr(helper, "toss_decision", None))):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    st.plotly_chart(helper.toss_winner_count(df), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                    st.plotly_chart(helper.toss_decision(df), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            elif 'toss_winner' not in df.columns or 'toss_decision' not in df.columns:
                 st.warning("Cannot show 'Toss Statistics' as 'toss_winner' or 'toss_decision' column is missing.")
            else:
                 st.warning("Missing 'helper.toss_winner_count' or 'helper.toss_decision' function.")


    if analysis_type == "Season-wise Analysis" and selected_season:
        st.subheader(f"{selected_season} Analysis")
        season_df = df[df['Season'] == selected_season].copy()
        col1, col2 = st.columns(2)
        with col1:
            if helper and callable(getattr(helper, "winners", None)):
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(helper.winners(season_df), use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else: st.warning("'helper.winners' function not found.")
        with col2:
            if 'city' in season_df.columns and helper and callable(getattr(helper, "matches_hosted_by_city", None)):
                city_df = helper.matches_hosted_by_city(season_df)
                fig = px.bar(city_df, x='City', y='Matches Hosted', title="Matches Hosted by City")
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            elif 'city' not in season_df.columns:
                st.warning("Cannot show 'Matches Hosted by City' as 'city' column is missing.")
            else:
                 st.warning("'helper.matches_hosted_by_city' function not found.")


    if analysis_type == "Team-wise Analysis" and selected_team and selected_team_season:
        
        # --- Logic uses selected_team_season directly ---
        title_subheader = f"{selected_team} Profile ({selected_team_season} Stats)"
        season_df = df[df['Season'] == selected_team_season].copy()
        st.subheader(title_subheader) 
        # --- End of logic ---

        if teams_df is not None:
            try:
                # Find the logo filename, case-insensitive match for team name might be safer
                team_info = teams_df[teams_df['team_name'].str.lower() == selected_team.lower()]
                if not team_info.empty:
                     logo_filename = team_info['logo_filename'].iloc[0]
                     logo_path = IMAGE_DIR / logo_filename
                     if logo_path.is_file(): 
                          st.image(str(logo_path), width=100)
                     else: 
                          st.warning(f"Logo image '{logo_filename}' not found in {IMAGE_DIR}")
                # else: No logo info for this team name
            except Exception as logo_err: 
                # Ignore if logo not found for a team or other error
                # st.warning(f"Could not display logo: {logo_err}") 
                pass 
        # else: teams_df was not loaded, warning already shown

        # Use the filtered season_df
        team_df = season_df[(season_df['team1']==selected_team) | (season_df['team2']==selected_team)]
        total_matches = team_df.shape[0]
        
        wins = 0
        if 'winner' in team_df.columns:
            wins = team_df[team_df['winner']==selected_team].shape[0]
        
        toss_wins = 0
        if 'toss_winner' in team_df.columns:
            toss_wins = team_df[team_df['toss_winner']==selected_team].shape[0]
        
        st.markdown("<div class='grid'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='stat-card'><h3>Total Matches Played</h3><p>{total_matches}</p></div>", unsafe_allow_html=True)
        with col2:
            win_pct_str = "(0.0%)" 
            if total_matches > 0:
                win_pct = (wins / total_matches) * 100
                win_pct_str = f"({win_pct:.1f}%)"
            
            st.markdown(f"""
            <div class='stat-card'>
                <h3>Total Wins</h3>
                <p>{wins}</p> 
                <span class='win-percentage'>{win_pct_str}</span>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='stat-card'><h3>Toss Wins</h3><p>{toss_wins}</p></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if analysis_type == "Player Analysis" and selected_player_stat and selected_player_year:
        st.subheader(f"Player Stats: {selected_player_stat} for {selected_player_year}")
        
        file_path = PLAYER_DATA_DIR / selected_player_stat / f"{selected_player_stat} - {selected_player_year}.csv"
        
        # --- ADDED: Check if the constructed file path exists ---
        if file_path.is_file():
            try:
                # Specify encoding='utf-8' or 'latin-1' if needed
                player_df = pd.read_csv(file_path, engine='python') 
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.dataframe(player_df)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"An error occurred while loading the data file '{file_path}': {e}")
        else:
             st.warning(f"Data file not found at the expected location: {file_path}")
             st.info(f"Please ensure the folder '{PLAYER_DATA_DIR}' exists in the same directory as app.py and contains the necessary subfolders and CSV files.")
