import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st # Import streamlit for warnings

# --- Team Name Mapping for Consistency ---
TEAM_NAME_MAP = {
    'Kings XI Punjab': 'Punjab Kings',
    'Delhi Daredevils': 'Delhi Capitals',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Rising Pune Supergiant': 'Rising Pune Supergiants', # Note: Might need singular 'Supergiant' depending on source data
    'Deccan Chargers': 'Sunrisers Hyderabad' 
    # Add other mappings if needed, e.g., 'Gujarat Lions': 'Gujarat Lions' (if you want to keep it)
}

def map_team_names(series):
    """Apply team name mapping to standardize names."""
    # Ensure input is a Series
    if isinstance(series, pd.Series):
        return series.replace(TEAM_NAME_MAP)
    # Handle single string input if necessary
    elif isinstance(series, str):
        return TEAM_NAME_MAP.get(series, series)
    return series # Return unchanged if not Series or string

# --- Overall Stats ---
def match_per_season(df):
    if 'Season' not in df.columns:
        st.warning("Cannot plot matches per season: 'Season' column missing.")
        return px.bar(title="Matches Per Season (Data Missing)") # Return empty plot
        
    season_df = df['Season'].value_counts().reset_index()
    season_df.columns = ['Season', 'Matches']
    season_df = season_df.sort_values(by='Season')
    return px.bar(season_df, x='Season', y='Matches', title="Matches Per Season")

def winners(df):
    if 'winner' not in df.columns:
        st.warning("Cannot plot winners: 'winner' column missing.")
        return px.bar(title="Total Wins by Team (Data Missing)")

    df_copy = df.copy()
    df_copy['winner'] = map_team_names(df_copy['winner']) # Apply mapping
    winners_df = df_copy['winner'].dropna().value_counts().reset_index()
    winners_df.columns = ['Team', 'Wins']
    return px.bar(winners_df, x='Team', y='Wins', title="Total Wins by Team (Standardized Names)")

def pom(df):
    if 'player_of_match' not in df.columns:
         st.warning("Cannot calculate Player of Match: 'player_of_match' column missing.")
         # Return an empty Series with index name for consistency
         return pd.Series(dtype='int64', name='Awards', index=pd.Index([], name='Player')) 

    # Return Series with Player as index and Awards as values, sorted
    pom_series = df['player_of_match'].dropna().value_counts()
    pom_series.index.name = 'Player' # Set the index name
    pom_series.name = 'Awards' # Set the series name
    return pom_series

def toss_decision(df):
    if 'toss_decision' not in df.columns:
         st.warning("Cannot plot toss decisions: 'toss_decision' column missing.")
         return px.pie(title="Toss Decisions (Data Missing)")
         
    toss_counts = df['toss_decision'].dropna().value_counts().reset_index()
    toss_counts.columns = ['Decision', 'Count']
    return px.pie(toss_counts, names='Decision', values='Count', title='Toss Decisions')

def toss_winner_count(df):
    if 'toss_winner' not in df.columns:
         st.warning("Cannot plot toss winners: 'toss_winner' column missing.")
         return px.bar(title="Toss Wins by Team (Data Missing)")
         
    df_copy = df.copy()
    df_copy['toss_winner'] = map_team_names(df_copy['toss_winner']) # Apply mapping
    toss_stats = df_copy['toss_winner'].dropna().value_counts().reset_index()
    toss_stats.columns = ['Team', 'Toss Wins']
    return px.bar(toss_stats, x='Team', y='Toss Wins', title="Toss Wins by Team (Standardized Names)")

def matches_hosted_by_city(df):
    if 'city' not in df.columns:
        st.warning("Cannot show matches by city: 'city' column missing.")
        # Return empty DataFrame or handle differently
        return pd.DataFrame({'City': [], 'Matches Hosted': []}) 
        
    city_df = df['city'].dropna().value_counts().reset_index()
    city_df.columns = ['City', 'Matches Hosted']
    return city_df.sort_values(by='Matches Hosted', ascending=False)

def get_team_list(df):
    if 'team1' not in df.columns or 'team2' not in df.columns:
        st.warning("Cannot get team list: 'team1' or 'team2' columns missing.")
        return []

    all_teams = pd.concat([df['team1'], df['team2']]).dropna()
    all_teams = map_team_names(all_teams) # Apply mapping
    return sorted(all_teams.unique())

def head_to_head(df, team1, team2):
    # This function isn't currently used in app.py, but keeping it here
    if not all(col in df.columns for col in ['team1', 'team2', 'winner']):
        st.warning("Cannot calculate head-to-head: Required columns missing.")
        return {'team1_wins': 0, 'team2_wins': 0, 'total_matches': 0}

    df_copy = df.copy()
    # Apply mapping to team1, team2, and winner for comparison
    df_copy['team1'] = map_team_names(df_copy['team1'])
    df_copy['team2'] = map_team_names(df_copy['team2'])
    df_copy['winner'] = map_team_names(df_copy['winner'])
    
    # Map the input team names as well for consistent comparison
    mapped_team1 = map_team_names(team1)
    mapped_team2 = map_team_names(team2)

    h2h_df = df_copy[((df_copy['team1'] == mapped_team1) & (df_copy['team2'] == mapped_team2)) |
                     ((df_copy['team1'] == mapped_team2) & (df_copy['team2'] == mapped_team1))]
    
    team1_wins = h2h_df[h2h_df['winner'] == mapped_team1].shape[0]
    team2_wins = h2h_df[h2h_df['winner'] == mapped_team2].shape[0]
    total_matches = h2h_df.shape[0]
    return {'team1_wins': team1_wins, 'team2_wins': team2_wins, 'total_matches': total_matches}

# --- Player Stats (Requires ball_by_ball.csv) ---
# These functions will only work if you load ball_by_ball data somewhere
def get_player_list(ball_df):
     if not isinstance(ball_df, pd.DataFrame) or not all(col in ball_df.columns for col in ['batsman', 'bowler']):
         st.warning("Cannot get player list: Invalid or missing ball-by-ball data.")
         return []
     players = set(ball_df['batsman'].dropna().unique()) | set(ball_df['bowler'].dropna().unique())
     return sorted(list(players)) # Convert set to list before sorting

def player_stats(ball_df, player):
    # Basic structure, assumes ball_df is loaded and valid
    batting_stats = { 'Total Runs': 0, 'Balls Faced': 0, 'Strike Rate': 0.0, 
                      'Fours': 0, 'Sixes': 0, 'Matches': 0 }
    bowling_stats = { 'Total Wickets': 0, 'Runs Conceded': 0, 'Economy Rate': 0.0 }

    if not isinstance(ball_df, pd.DataFrame):
        st.warning("Ball-by-ball data not available for player stats.")
        return {'Batting': batting_stats, 'Bowling': bowling_stats}

    # Batting
    if 'batsman' in ball_df.columns and 'runs_off_bat' in ball_df.columns and 'match_id' in ball_df.columns:
        batting_df = ball_df[ball_df['batsman'] == player]
        if not batting_df.empty:
            total_runs = batting_df['runs_off_bat'].sum()
            balls_faced = batting_df[(batting_df['wide_runs'] == 0) & (batting_df['noball_runs']==0)].shape[0] # Exclude extras from balls faced
            strike_rate = (total_runs / balls_faced * 100) if balls_faced > 0 else 0
            fours = batting_df[batting_df['runs_off_bat'] == 4].shape[0]
            sixes = batting_df[batting_df['runs_off_bat'] == 6].shape[0]
            batting_stats.update({
                'Total Runs': int(total_runs),
                'Balls Faced': int(balls_faced),
                'Strike Rate': round(strike_rate, 2),
                'Fours': fours,
                'Sixes': sixes,
                'Matches': batting_df['match_id'].nunique()
            })

    # Bowling
    if 'bowler' in ball_df.columns and 'player_dismissed' in ball_df.columns and 'total_runs' in ball_df.columns:
         bowling_df = ball_df[ball_df['bowler'] == player]
         if not bowling_df.empty:
             # Wickets: Count where player_dismissed is not null AND dismissal_kind is not run out/retired hurt etc.
             valid_dismissals = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'] 
             wickets = 0
             if 'dismissal_kind' in bowling_df.columns:
                  # Exclude run outs where the bowler wasn't the fielder involved
                  wickets = bowling_df[bowling_df['dismissal_kind'].isin(valid_dismissals)].shape[0]
             else: # Fallback if dismissal_kind is missing (less accurate)
                 wickets = bowling_df['player_dismissed'].notnull().sum() 

             # Runs conceded: Total runs excluding legbyes and byes
             runs_conceded = bowling_df[(bowling_df['legbye_runs'] == 0) & (bowling_df['bye_runs'] == 0)]['total_runs'].sum()

             # Calculate overs more accurately: exclude wides and no-balls from ball count
             balls_bowled = bowling_df[(bowling_df['wide_runs'] == 0) & (bowling_df['noball_runs'] == 0)].shape[0]
             overs = balls_bowled / 6
             economy_rate = (runs_conceded / overs) if overs > 0 else 0
             bowling_stats.update({
                 'Total Wickets': int(wickets),
                 'Runs Conceded': int(runs_conceded),
                 'Economy Rate': round(economy_rate, 2)
             })

    return {'Batting': batting_stats, 'Bowling': bowling_stats}

# --- Example usage comment (keep commented out in helper.py) ---
# if __name__ == '__main__':
#     # Example: Load ball_by_ball if needed for testing
#     try:
#         ball_by_ball_df = pd.read_csv("../csv/ball_by_ball.csv") # Adjust path if testing
#         if ball_by_ball_df is not None:
#             player_list = get_player_list(ball_by_ball_df)
#             print("Sample players:", player_list[:5])
#             if player_list:
#                  selected_player = player_list[0] # Example player
#                  stats = player_stats(ball_by_ball_df, selected_player)
#                  print(f"Stats for {selected_player}:", stats)
#     except FileNotFoundError:
#         print("ball_by_ball.csv not found in expected location for testing.")
#     except Exception as e:
#         print(f"Error during testing: {e}")
