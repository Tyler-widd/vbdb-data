import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_lovb import LOVB
#from fetch_ncaa import NCAA
import numpy as np

## NCAA
#ncaa = NCAA()
#men = ncaa.fetch_players(gender = 'M')
#women = ncaa.fetch_players(gender = 'W')
#men.to_csv('men_roster.csv', index=False)
#men['Player URL'] = "https://stats.ncaa.org" + men['Player URL']
#women.to_csv('women_roster.csv', index=False)
#women['Player URL'] = "https://stats.ncaa.org" + women['Player URL']

# PVF
# pvf = PVF()
# teams = pvf.fetch_teams()
# roster_ids = []
# for team in teams:
#     roster_ids.append(team['current_roster_id'])
# rosters = []
# for roster_id in  [40, 46, 45, 77, 44, 5, 42, 41]:
#     df = pd.DataFrame(pvf.fetch_players(roster_id))
#     df['jersey_number'] = df['jersey_number'].astype(str)
#     df['jersey_number'] = df['jersey_number'].str.split('.').str[0]
#     rosters.append(df)
# pvf = pd.concat(rosters).reset_index(drop=True)

# team_mapping = {
#     'Atlanta Vibe': 'https://provolleyball.com/teams/atlanta-vibe/roster/2025-roster/players/',
#     'Columbus Fury': 'https://provolleyball.com/teams/columbus-fury/roster/2025-columbus-roster/players/',
#     'Grand Rapids Rise': 'https://provolleyball.com/teams/grand-rapids-rise/roster/2025-grand-rapids-roster/players/',
#     'Indy Ignite': 'https://provolleyball.com/teams/indy-ignite/roster/2025-indy-roster/players/',
#     'Omaha Supernovas': 'https://provolleyball.com/teams/omaha-supernovas/roster/2025-omaha-roster/players/',
#     'Orlando Valkyries': 'https://provolleyball.com/teams/orlando-valkyries/roster/2025-orlando-roster/players/',
#     'San Diego Mojo': 'https://provolleyball.com/teams/san-diego-mojo/roster/2025-san-diego-roster/players/',
#     'Vegas Thrill': 'https://provolleyball.com/teams/vegas-thrill/roster/2025-vegas-roster/players/'
#     }

# pvf['player_url'] = np.where(
#     pvf['team'].isin(team_mapping.keys()),  # Check if the team is in team_mapping
#     pvf['team'].map(team_mapping) + 
#     pvf['full_name'].str.lower().str.replace(' ', '-'),  # Append slugified player name
#     None  # Set to None if team is not in the mapping
# )

# pvf.rename(columns={'jersey_number': '#',
#                     'full_name': 'Name',
#                     'player_positions': 'Position',
#                     'height': 'Height',
#                     'hometown': 'Hometown',
#                     'college': 'High School',
#                     'player_url': 'Player URL',
#                     'team': 'team_name'}, inplace=True)
# pvf = pvf[['#', 'Name', 'Position', 'Height', 'Hometown', 'High School', 'Player URL', 'team_name']]
# pvf['team_id'] = None
# pvf['head_coach'] = None
# pvf['Class'] = None
# pvf['division_hist_url'] = None
# pvf['division'] = None
# pvf['team_short'] = None
# pvf['conference_short'] = 'PVF'
# pvf['conference_name'] = 'PVF'
# pvf['state'] = None
# pvf['sportRegion'] = None
# pvf['school_url'] = None
# pvf['High School']
# pvf['school_athletic_url'] = None
# pvf['Height'] = pvf['Height'].str.replace("'", "-")

# pvf['Position'] = np.where(pvf['Position'] == 'Opposite Hitter', 'OPP', 
#                            np.where(pvf['Position'] == 'Middle Blocker', 'MB', 
#                                     np.where(pvf['Position'] == 'Setter', 'S', 
#                                              np.where(pvf['Position'] == 'Outside Hitter', 'OH', 
#                                                       np.where(pvf['Position'] == 'Libero', 'L', 
#                                                                np.where(pvf['Position'] == 'Outside Hitter, Opposite Hitter', 'OH', 
#                                                                         np.where(pvf['Position'] == 'Libero, Setter', 'L', pvf['Position'])))))))

# pvf.to_csv('24PvfRosters.csv', index=False)

# # LOVB
lovb = LOVB()
df = lovb.fetch_rosters()
df['links'] = "https://www.lovb.com/teams/lovb-" + df['Team Name'].str.lower() + "-volleyball/athletes/" + df['Name'].str.replace(' ', '-').str.lower()
df[df['Player Number'] != 'Staff']
df.to_csv('lovb_test.csv', index=False)

df = df.rename(columns={
    'Player Number': '#',
    'College / Home Club': 'Hometown',
    'Team Name': 'team_name',
    'links': 'Player URL'
})

df['Class'] = None
df['High School'] = None
df['team_id'] = None
df['head_coach'] = None
df['division_hist_url'] = None
df['division'] = 'Pro'
df['team_short'] = df['team_name']
df['conference_name'] = 'LOVB'
df['conference_short'] = 'LOVB'
df['state'] = None
df['sportRegion'] = None
df['school_url'] = None
df['school_athletic_url'] = None

df['Position'] = np.where(df['Position'] == 'Opposite Hitter', 'OPP', 
                           np.where(df['Position'] == 'Middle Blocker', 'MB', 
                                    np.where(df['Position'] == 'Setter', 'S', 
                                             np.where(df['Position'] == 'Outside Hitter', 'OH', 
                                                      np.where(df['Position'] == 'Libero', 'L', df['Position'])))))

df.to_csv('24LovbRosters.csv', index=False)