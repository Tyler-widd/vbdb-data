from fetch_lovb import LOVB
from fetch_pvf import PVF
import pandas as pd

# PVF
pvf = PVF()
df = pd.DataFrame(pvf.fetch_schedule())
df['date'] = df['date'].str.split('T').str[0]
df = df[['date', 'location', 'home_team_id', 'away_team_id', 'home_team_name', 'away_team_name']]
df['league'] = 'pvf'
df.to_csv('24PvfSch.csv', index=False)

# LOVB
lovb = LOVB()
df = pd.DataFrame(lovb.fetch_schedule())
df = df[['date', 'location', 'home_team_id', 'away_team_id', 'home_team_name', 'away_team_name']]
df['league'] = 'lovb'
df.to_csv('24LovbSch.csv', index=False)
