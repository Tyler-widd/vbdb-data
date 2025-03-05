import pandas as pd

def fetch_and_combine_results():
    # Initialize fetchers
    from fetch_ncaa import NCAA
    df_list = []
    # Fetch data from different sources
    ncaa_w = NCAA(gender='W')
    
    teams = ncaa_w.fetch_ncaa_teams()
    if len(teams) > 0:
        team_ids = teams['orgId'].iloc
        for team_id in team_ids:
            team_schedule = ncaa_w.fetch_schedule_for_team(team_id, '2024-25')
            team_schedule['gender'] = 'W'
            df_list.append(team_schedule)
            
    # Fetch data from different sources
    ncaa_m = NCAA(gender='M')
    
    teams_m = ncaa_m.fetch_ncaa_teams()
    
    if len(teams) > 0:
        team_idsM = teams_m['orgId'].iloc
        for team_id in team_idsM:
            team_schedule = ncaa_m.fetch_schedule_for_team(team_id, '2024-25')
            team_schedule['gender'] = 'M'
            df_list.append(team_schedule)

        
    df = pd.concat(df_list)
    df.to_csv("data/cbvb_ncaa_results.csv", index=False)
    return df

if __name__ == "__main__":
    print(fetch_and_combine_results())