import pandas as pd

from fetch_ncaa import NCAA


def fetch_and_combine_results():
    """Fetch and combine NCAA volleyball schedules for both men's and women's teams."""
    # Initialize empty list to store individual team schedules
    df_list = []
    
    # Process women's teams
    print("Fetching women's teams data...")
    ncaa_w = NCAA(gender='W')
    teams_w = ncaa_w.fetch_ncaa_teams()
    
    if not teams_w.empty:
        total_w = len(teams_w)
        print(f"Found {total_w} women's teams. Starting to fetch schedules...")
        
        for i, team_id in enumerate(teams_w['orgId'][0:4]):
            try:
                print(f"Fetching women's schedule {i+1}/{total_w} for team ID: {team_id}")
                team_schedule = ncaa_w.fetch_schedule_for_team(team_id, '2024-25')
                
                if not team_schedule.empty:
                    team_schedule['gender'] = 'W'
                    df_list.append(team_schedule)
                    print(f"Successfully fetched schedule with {len(team_schedule)} games")
                else:
                    print(f"No schedule data found for women's team ID: {team_id}")
            except Exception as e:
                print(f"Error fetching women's team {team_id}: {str(e)}")
    
    # Process men's teams
    print("\nFetching men's teams data...")
    ncaa_m = NCAA(gender='M')
    teams_m = ncaa_m.fetch_ncaa_teams()
    
    if not teams_m.empty:
        total_m = len(teams_m)
        print(f"Found {total_m} men's teams. Starting to fetch schedules...")
        
        for i, team_id in enumerate(teams_m['orgId'][0:4]):
            try:
                print(f"Fetching men's schedule {i+1}/{total_m} for team ID: {team_id}")
                team_schedule = ncaa_m.fetch_schedule_for_team(team_id, '2024-25')
                
                if not team_schedule.empty:
                    team_schedule['gender'] = 'M'
                    df_list.append(team_schedule)
                    print(f"Successfully fetched schedule with {len(team_schedule)} games")
                else:
                    print(f"No schedule data found for men's team ID: {team_id}")
            except Exception as e:
                print(f"Error fetching men's team {team_id}: {str(e)}")
    
    # Combine all schedules
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        print(f"\nCombined data: {len(df)} total games across {len(df_list)} teams")
        df.to_csv("data/cbvb_ncaa_results.csv", index=False)
        return df
    else:
        print("No schedule data was successfully retrieved")
        return pd.DataFrame()

if __name__ == "__main__":
    result = fetch_and_combine_results()
    # Uncomment to save to CSV
    print(result)
