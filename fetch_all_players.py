import json
import os

def fetch_and_combine_players():
    # Initialize fetchers
    from fetch_lovb import LOVB
    from fetch_pvf import PVF
    from fetch_ncaa import NCAA

    # Fetch data from different sources
    lovb = LOVB()
    lovb_roster = lovb.fetch_rosters()
    pvf = PVF()
    pvf_roster = pvf.fetch_players()
    ncaa = NCAA()
    ncaa_men = ncaa.fetch_players(gender='M')
    ncaa_women = ncaa.fetch_players(gender='W')
    
    # Create a unified structure for all players
    all_players = []
     
    # # Process LOVB players
    for player in lovb_roster:
        all_players.append({
            "name": player.get('Name', ''),
            "jersey": player.get('#', ''),
            "position": player.get('Position', ''),
            "height": player.get('Height', ''),
            "hometown": player.get('Hometown', ''),
            "team": player.get('team_name', ''),
            "conference": player.get('conference_name', 'LOVB'),
            "level": "Pro Women",
            "division": player.get('division', 'Pro'),
            "profile_url": player.get('Player URL', ''),
            "college": None,
            "high_school": None,
            "class_year": None,
            "state": None,
            "head_coach": None,
            "data_source": "LOVB"
        })
    print(lovb_roster)
    
    # # Process PVF players
    for player in pvf_roster:
        all_players.append({
            "name": player.get('full_name', ''),
            "jersey": str(player.get('jersey_number', '')),
            "position": player.get('player_positions', ''),
            "height": player.get('height', ''),
            "hometown": player.get('hometown', ''),
            "team": player.get('team', ''),
            "conference": player.get('conference_name', 'PVF'),
            "level": "Pro Women",
            "division": player.get('division', 'Pro'),
            "profile_url": player.get('Player URL', ''),
            "college": player.get('college', ''),
            "high_school": None,
            "class_year": None,
            "state": None,
            "head_coach": None,
            "data_source": "PVF"
        })
    print(pvf_roster)
    
    # # Process NCAA Men players
    for player in ncaa_men:
        all_players.append({
            "name": player.get('Name', ''),
            "jersey": player.get('#', ''),
            "position": player.get('Position', ''),
            "height": player.get('Height', ''),
            "hometown": player.get('Hometown', ''),
            "team": player.get('team_name', ''),
            "conference": player.get('conference_name', ''),
            "level": "NCAA Men",
            "division": player.get('division', ''),
            "profile_url": f"https://stats.ncaa.org{player.get('Player URL', '')}" if player.get('Player URL') else '',
            "college": player.get('team_name', ''),
            "high_school": player.get('High School', ''),
            "class_year": player.get('Class', ''),
            "state": player.get('state', ''),
            "head_coach": player.get('head_coach', ''),
            "data_source": "NCAA"
        })
    print(ncaa_men)
    
    # Process NCAA Women players
    for player in ncaa_women:
        all_players.append({
            "name": player.get('Name', ''),
            "jersey": player.get('#', ''),
            "position": player.get('Position', ''),
            "height": player.get('Height', ''),
            "hometown": player.get('Hometown', ''),
            "team": player.get('team_name', ''),
            "conference": player.get('conference_name', ''),
            "level": "NCAA Women",
            "division": player.get('division', ''),
            "profile_url": f"https://stats.ncaa.org{player.get('Player URL', '')}" if player.get('Player URL') else '',
            "college": player.get('team_name', ''),
            "high_school": player.get('High School', ''),
            "class_year": player.get('Class', ''),
            "state": player.get('state', ''),
            "head_coach": player.get('head_coach', ''),
            "data_source": "NCAA"
        })
    print(ncaa_women)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    print(all_players)
    
    # Save combined data to JSON file
    json_filename = "data/vbdb_players.json"
    with open(json_filename, "w", encoding='utf-8') as json_file:
        json.dump(all_players, json_file, indent=4, ensure_ascii=False)
    
    print(f"Combined player data successfully saved to {json_filename}")
    print(f"Total players: {len(all_players)}")
    
    return all_players

if __name__ == "__main__":
    print(fetch_and_combine_players())