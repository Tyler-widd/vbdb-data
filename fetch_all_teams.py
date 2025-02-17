import json
import os
import subprocess
from fetch_lovb import LOVB
from fetch_ncaa import NCAA
from fetch_pvf import PVF

def fetch_all_teams():
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Initialize fetchers
    lovb = LOVB()
    ncaa = NCAA()
    pvf = PVF()

    # Fetch data
    ncaa_m_teams = ncaa.fetch_teams('M')
    ncaa_w_teams = ncaa.fetch_teams('W')
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
            "division": None
        })

    # Process PVF teams
    for team in pvf_teams:
        all_teams.append({
            "name": team["name"],
            "url": team["url"],
            "conference": "PVF",
            "level": "Pro Women",
            "division": None
        })

    # Process NCAA Men's teams
    for team in ncaa_m_teams:
        all_teams.append({
            "name": team["full_name"],
            "url": team["school_athletic_url"],
            "conference": team["conference_name"],
            "level": "NCAA Men",
            "division": team["division"]
        })

    # Process NCAA Women's teams
    for team in ncaa_w_teams:
        all_teams.append({
            "name": team["full_name"],
            "url": team["school_athletic_url"],
            "conference": team["conference_name"],
            "level": "NCAA Women",
            "division": team["division"]
        })

    # Output JSON
    json_filename = "data/vbdb_teams.json"
    with open(json_filename, "w") as json_file:
        json.dump(all_teams, json_file, indent=4)

    print(f"JSON data successfully saved to {json_filename}")

    # Push JSON to GitHub
    try:
        repo_path = os.path.abspath(".")  # Path to the Git repository
        subprocess.run(["git", "-C", repo_path, "add", json_filename], check=True)
        subprocess.run(["git", "-C", repo_path, "commit", "-m", "Update vbdb_teams.json"], check=True)
        subprocess.run(["git", "-C", repo_path, "push", "origin", "master"], check=True) 
        print("Successfully pushed changes to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")

if __name__ == "__main__":
    fetch_all_teams()

