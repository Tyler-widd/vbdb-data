import json
import os
from fetch_lovb import LOVB
from fetch_ncaa import NCAA
from fetch_pvf import PVF

def fetch_all_teams():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Initialize fetchers
    lovb = LOVB()
    ncaa_w = NCAA('W')
    ncaa_m = NCAA('M')
    pvf = PVF()

    # Fetch data
    ncaa_m_teams = ncaa_m.fetch_ncaa_teams()
    ncaa_w_teams = ncaa_w.fetch_ncaa_teams()
    lovb_teams = lovb.fetch_teams()
    pvf_teams = pvf.fetch_teams()

    # Standardized list for all teams
    all_teams = []

    # Process LOVB teams
    for team in lovb_teams:
        all_teams.append({
            "name": team["name"],
            "url": team["url"],
            "conference": "LOVB",
            "level": "Pro Women",
            'img': team['img'],
            "division": None
        })

    # Process PVF teams
    for team in pvf_teams:
        all_teams.append({
            "name": team["name"],
            "url": team["url"],
            "conference": "PVF",
            'img': team['img'],
            "level": "Pro Women",
            "division": None
        })

    # Process NCAA Men's teams
    for team in ncaa_m_teams.to_dict(orient='records'):
        all_teams.append({
            "name": team["nameOfficial"],
            "url": team["athleticWebUrl"],
            "conference": team["confAbbreviation"],
            'img': team['img'],
            "level": "NCAA Men",
            "division": team["divisionRoman"]
        })

    # Process NCAA Women's teams
    for team in ncaa_w_teams.to_dict(orient='records'):
        all_teams.append({
            "name": team["nameOfficial"],
            "url": team["athleticWebUrl"],
            "conference": team["confAbbreviation"],
            'img': team['img'],
            "level": "NCAA Women",
            "division": team["divisionRoman"]
        })

    # Output JSON
    json_filename = "data/vbdb_teams.json"
    with open(json_filename, "w") as json_file:
        json.dump(all_teams, json_file, indent=4)

    print(f"JSON data successfully saved to {json_filename}")

if __name__ == "__main__":
    fetch_all_teams()
