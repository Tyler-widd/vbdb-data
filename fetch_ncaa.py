import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

# Suppress the specific BeautifulSoup warning

class NCAA:
    ""

    def fetch_teams(self, gender, sport="VB"):
        """
        Function to gather D1-D3 NCAA women's volleyball teams.

        Parameters:
            gender (str): The wanted gender. W, M
            sport (str): Change sport if desired. Use 'SV' for beach volleyball.


        Returns:
            list: A list of dictionaries, each containing:
                - team_id
                - division
                - conference_id
                - conference_name
                - school_url
                - school_athletic_url
                - sport_region
                - full_name
        """
        url = f"https://web3.ncaa.org/directory/api/directory/memberList?type=12&sportCode={gender}{sport}"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code != 200:
            print("Failed to retrieve data")
            return None

        json_data = response.json()

        team_data = []
        for team in json_data:
            team_info = {
                "team_id": team.get("orgId", None),
                "division": team.get("division", None),
                "conference_id": team.get("conferenceId", None),
                "conference_name": team.get("conferenceName", None),
                "school_url": team.get("webSiteUrl", None),
                "school_athletic_url": team.get("athleticWebUrl", None),
                "sport_region": team.get("sportRegion", None),
                "full_name": team.get("nameOfficial", None)
            }
            team_data.append(team_info)

        return team_data

    def fetch_players(self, gender):
        """
        Function to gather D1-D3 NCAA rosters.

        Returns:
            list: A list of dictionaries, each containing:
                - team_id
                - full_name
                - head_coach
                - division
                - conference
                - url
        """
        # Get all team codes and clean a bit of data
        df = pd.read_html('https://stats.ncaa.org/game_upload/team_codes')[0]
        df = df[(df[0] != 'NCAA Codes') & (df[0] != 'ID')]
        df.rename(columns={0: 'team_id', 1: 'team_name'}, inplace=True)


        json_data = requests.get(f"https://web3.ncaa.org/directory/api/directory/memberList?type=12&sportCode={gender}VB&").json()
        teams_dict = []
        for json in json_data:
            teams_dict.append({
                'team_id': json['orgId'],
                'team_name': json['nameOfficial'],
                'conference_id': json['conferenceId'],
                'conference_name': json['conferenceName'],
                'school_url': json['webSiteUrl'],
                'division': json['divisionRoman'],
                'school_athletic_url': json['athleticWebUrl'],
                'sportRegion': json['sportRegion'],
                'state': json['memberOrgAddress']['state']
                })
        teams_df = pd.json_normalize(teams_dict)
        teams_df['team_id'] = teams_df['team_id'].astype(str)

        # List to store team data
        team_data = []

        # Loop through each team_id
        for team_id in teams_df['team_id'].unique():
            url = f'https://web3.ncaa.org/directory/orgDetail?id={team_id}'
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            })

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the specific table
            table = soup.find('table', attrs={'class': 'table table-responsive table-condensed table-striped'})
            if not table:
                continue

            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header row
                columns = row.find_all('td')
                if gender == 'W':
                    gender_text = "Women's"
                else:
                    gender_text = "Men's"
                if columns and columns[0].text.strip() == f"{gender_text} Volleyball":
                    team_data.append({
                        'team_id': team_id,
                        'head_coach': columns[1].text.strip(),
                        'division_hist_url': columns[2].text.strip(),
                        'conference': columns[3].text.strip()
                    })

        df = pd.json_normalize(team_data)
        df['head_coach'] = df['head_coach'].apply(lambda x: " ".join(x.split()) if isinstance(x, str) else x)
        
        teams = pd.read_html('https://stats.ncaa.org/game_upload/team_codes')[0]
        teams = teams[(teams[0] != 'NCAA Codes') & (teams[0] != 'ID')]
        teams.rename(columns={0: 'team_id', 1: 'team_short'}, inplace=True)
        teams['team_id'] = teams['team_id'].astype(str)
        df['team_id'] = df['team_id'].astype(str)
        df = pd.merge(df, teams, on = 'team_id')
        
        team_ids = list(df['team_id'].dropna().unique())
        
        roster_list = []

        for team_id in team_ids:
            url = f'https://stats.ncaa.org/teams/history/{gender}VB/{team_id}'
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                },
            )

            soup = BeautifulSoup(response.content, "html.parser")
            try:
                if soup.find('td') and soup.find('td').text == '2025-26':
                    roster_link = soup.find('td').find('a')['href']
                    conference_short = soup.find_all('tr')[1].find_all('td')[3].text
                    response = requests.get(
                        "https://stats.ncaa.org" + roster_link + "/roster",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                        },
                    )

                    soup = BeautifulSoup(response.content, "html.parser")
                    
                    table = soup.find('table', {'id': lambda x: x and x.startswith('rosters_form_players')})

                    # Extract headers
                    headers = [th.text.strip() for th in table.find('thead').find_all('th')]

                    # Add a header for the player URL
                    headers.append('Player URL')

                    # Extract rows
                    rows = []
                    for tr in table.find('tbody').find_all('tr'):
                        cells = tr.find_all('td')
                        row = []
                        player_url = None  # Placeholder for the player URL
                        
                        for cell in cells:
                            # Check if the cell contains a link
                            link = cell.find('a')
                            if link:
                                row.append(link.text.strip())  # Append the name
                                player_url = link['href']    # Save the href for later
                            else:
                                row.append(cell.text.strip())  # Append regular cell text
                        
                        # Append the player URL as a separate field
                        row.append(player_url)
                        rows.append(row)

                    # Create DataFrame for the current team
                    roster_df = pd.DataFrame(rows, columns=headers)
                    roster_df['team_id'] = team_id
                    roster_df['conference_short'] = conference_short
                    roster_df['team_id'] = roster_df['team_id'].astype(str)
                    roster_list.append(roster_df)

                    # Append to the roster_list (this was previously inside the loop where it was resetting)
                    if roster_list:
                        roster_list_df = pd.concat(roster_list).reset_index(drop=True)
                        # Continue with the rest of your code
                    else:
                        print("No roster data found. Check the team IDs or the website structure.")
                        return [] 

            except Exception as e:
                print(f"Error processing team_id {team_id}: {e}")

        # Concatenate all the roster data into a single DataFrame
        roster_list_df = pd.concat(roster_list).reset_index(drop=True)

        # Merge the roster information with the other team data
        final_df = pd.merge(roster_list_df, df, on='team_id')
        final_final_df = pd.merge(final_df, teams_df, on='team_id')
        final_data = final_final_df[['#', 'Name', 'Class', 'Position', 'Height', 'Hometown', 
                               'High School', 'Player URL', 'team_id', 'head_coach', 
                               'division_hist_url', 'division', 'team_name', 'team_short', 
                               'conference_name', 'conference_short', 'state', 'sportRegion', 
                               'school_url', 'school_athletic_url']].to_dict(orient='records')

        # Return the final DataFrame with the desired columns
        return final_data

    def fetch_teams_history(self, gender, team_id):
        """
        Fetch a team's history.

        Parameters:
            gender (str): 'M' | 'W'
            team_id (str): The ID of the team.

        Returns:
            list: A list of dictionaries, each containing:
                - team_id
                - year
                - season_id
                - head_coach
                - division
                - conference
                - wins
                - losses
                - ties
                - wl
                - notes
        """
        url = f"https://stats.ncaa.org/teams/history/{gender}VB/{team_id}"
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            },
        )

        soup = BeautifulSoup(response.content, "html.parser")

        tbody = soup.find("tbody")
        rows = tbody.find_all("tr")

        # Initialize a list to hold the data dictionaries
        data_list = []

        for row in rows:
            # Extract each cell (td) in the row
            cells = row.find_all("td")

            # Create a dictionary for the row data
            row_data = {
                "team_id": team_id,
                "year": cells[0].text.strip(),  # Year (text)
                "season_id": cells[0].find("a")["href"].split("/")[-1],
                "head_coach": cells[1].text.strip(),  # Head Coach
                "division": cells[2].text.strip(),  # Division
                "conference": cells[3].text.strip(),  # Conference
                "wins": cells[4].text.strip(),  # Wins
                "losses": cells[5].text.strip(),  # Losses
                "ties": cells[6].text.strip(),  # Ties
                "wl": cells[7].text.strip(),  # Wins-Losses percentage
                "notes": cells[8].text.strip(),  # Notes
            }

            # Append the dictionary to the list
            data_list.append(row_data)

        return data_list

    def fetch_schedule(self, season_id, gbg=False):
        """
        Fetch a team's season.

        Parameters:
            season_id (str): The ID of the season.

        Returns:
            list: A list of dictionaries containing schedule data.
        """
        url = f"https://stats.ncaa.org/teams/{season_id}"
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
            },
        )
        soup = BeautifulSoup(response.content, "html.parser")
        
        if not gbg:
            try:
                team_id = (
                    soup.find("div", {"class": "card-header"})
                    .find("img")["src"]
                    .split("//")[-1]
                    .split(".gif")[0]
                )
            except (AttributeError, KeyError, IndexError):
                team_id = None

            table = soup.find("div", attrs={"style": "min-width: 400px;"})
            game_data = []

            if not table:
                return game_data  # Return empty list if the table is not found

            for row in table.find_all("tr", class_="underline_rows"):
                cells = row.find_all("td")

                if len(cells) >= 4:
                    try:
                        date = cells[0].text.strip()
                        try:
                            opponent_raw = cells[1].text.strip()  # Get the raw text
                            if "@" in opponent_raw:
                                if opponent_raw.startswith("@"):
                                    opponent = opponent_raw.split("@")[1].strip()
                                else:
                                    opponent = opponent_raw.split("@")[0].strip()
                            else:
                                opponent = opponent_raw
                        except (AttributeError, IndexError):
                            opponent = None
                        opponent_tag = cells[1].find("a")
                        opponent_season_id = opponent_tag["href"].split("/")[-1] if opponent_tag else None
                        opponent_team_id = (
                            opponent_tag.find("img")["src"].split("//")[-1].split(".gif")[0] if opponent_tag else None
                        )
                        result = cells[2].text.strip()
                        attendance = cells[3].text.strip()
                        box_score_link_tag = cells[2].find("a")
                        box_score_link = box_score_link_tag["href"] if box_score_link_tag else None

                        row_data = {
                            "team_id": team_id,
                            "season_id": season_id,
                            "date": date,
                            "opponent": opponent,
                            "opponent_season_id": opponent_season_id,
                            "opponent_team_id": opponent_team_id,
                            "result": result,
                            "attendance": attendance,
                            "box_score": box_score_link,
                        }
                        game_data.append(row_data)
                    except (AttributeError, KeyError, IndexError):
                        continue

            return game_data

        else:
            team_id = (
                soup.find("div", {"class": "card-header"})
                .find("img")["src"]
                .split("//")[-1]
                .split(".gif")[0]
            )
            data = []
            try:
                gbg_url = soup.find('a', string="Game By Game")['href']
                url = "https://stats.ncaa.org" + gbg_url
                response = requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                })
                soup = BeautifulSoup(response.content, "html.parser")
                rows = soup.find_all('tr', id=lambda x: x and 'contest' in x)

                for row in rows:
                    try:
                        cells = row.find_all('td')
                        match_id = row.get('id')
                        date = cells[0].text.strip()
                        opponent_cell = cells[1]
                        opponent_raw = opponent_cell.text.strip()
                        opponent = opponent_raw.split('\n')[0].strip()
                        opponent_link = opponent_cell.find('a')
                        opponent_season_id = opponent_link['href'].split('/')[-1] if opponent_link else None
                        opponent_img = opponent_cell.find('img')
                        opponent_team_id = opponent_img['src'].split('/')[-1].split('.')[0] if opponent_img else None

                        row_data = {
                            'team_id': team_id,
                            "match_id": match_id,
                            "date": date,
                            "opponent": opponent,
                            "opponent_season_id": opponent_season_id,
                            "opponent_team_id": opponent_team_id,
                            "season_id": season_id,
                        }
                        data.append(row_data)
                    except (AttributeError, KeyError, IndexError):
                        continue

            except (AttributeError, KeyError, IndexError):
                pass

            return data

    def fetch_match_details(self, season_id, summary=False, box_score=False, pbp=False):

        def parse_play(play_text, school, score, match_id, set_number):
            play_text = ' '.join(play_text.split())
            
            serve_match = re.search(r'([\w\s]+)\s+serves', play_text)
            if serve_match:
                player = serve_match.group(1).strip()
                return {
                    'match_id': match_id,
                    'set_number': set_number,
                    'skill': 'serves',
                    'player': player,
                    'play': play_text,
                    'school': school,
                    'score': score
                }
            
            skill_match = re.search(r'([\w]+)\s+by\s+([\w\s]+)', play_text)
            if skill_match:
                skill, player = skill_match.groups()
                return {
                    'match_id': match_id,
                    'set_number': set_number,
                    'skill': skill.lower().strip(),
                    'player': player.strip(),
                    'play': play_text,
                    'school': school,
                    'score': score
                }
            return None

        def parse_volleyball_pbp(html, match_id):
            soup = BeautifulSoup(html, 'html.parser')
            
            short_play_text = []
            short_plays = soup.find_all('span', attrs={'class': 'short_play_text'})
            for short_play in short_plays:
                short_play_text.append(short_play.text.strip().replace('\x01 ', '').strip())

            # Find all set containers
            set_containers = soup.find_all('div', {'class': 'col', 'style': 'max-width: 800px;'})
            teams = {}
            headers = soup.find_all('th')
            for header in headers:
                team_div = header.find('span', class_='d-none')
                if team_div and '40%' in header.get('width', ''):
                    if 'text-align: left' in str(header) or not teams:
                        teams['left'] = team_div.text.strip()
                    else:
                        teams['right'] = team_div.text.strip()
            
            all_plays = []
            current_score = '0-0'
            current_sequence_id = None
            current_sequence = []
            
            for container in set_containers:
                # Get set number from header
                header = container.find('div', class_='card-header')
                if not header:
                    continue
                    
                set_text = header.text.strip()
                current_set = int(set_text[0]) if set_text[0].isdigit() else 1
                
                rows = container.find_all('tr')
                for row in rows:
                    score_cell = row.find('td', string=re.compile(r'\d+-\d+'))
                    if score_cell:
                        current_score = score_cell.text.strip()
                        if current_sequence:
                            all_plays.extend(current_sequence)
                            current_sequence = []
                        continue
                    
                    if 'scoring_plays' in row.get('class', []):
                        play_cell = row.find('td', class_='smtext')
                        if not play_cell:
                            continue
                            
                        play_text = play_cell.text.strip()
                        if not play_text:
                            continue
                        
                        school = None
                        if play_cell.parent.find_all('td')[0].text.strip():
                            school = teams['left']
                        else:
                            school = teams['right']

                        play_info = parse_play(play_text, school, current_score, match_id, current_set)
                        if play_info:
                            sequence_id = row.get('class')[1]
                            if sequence_id != current_sequence_id:
                                if current_sequence:
                                    all_plays.extend(current_sequence)
                                current_sequence = []
                                current_sequence_id = sequence_id
                            current_sequence.append(play_info)
            
            if current_sequence:
                all_plays.extend(current_sequence)

            short_play_index = 0
            previous_score = None
            for play in all_plays:
                current_score = play["score"]
                
                # If the score changes, move to the next short_play_text
                if current_score != previous_score:
                    if short_play_index < len(short_play_text):
                        play["short_play_text"] = short_play_text[short_play_index]
                        short_play_index += 1
                    else:
                        play["short_play_text"] = ""

                previous_score = current_score

            df = pd.DataFrame(all_plays)
            df['short_play_text'] = df['short_play_text'].ffill()

            df['grade'] = np.where((df['score'] != df['score'].shift(-1)) & df['short_play_text'].str.contains('kill', na=False), '#', 
                          np.where((df['score'] != df['score'].shift(-1)) & df['short_play_text'].str.contains('error', na=False), '=', 
                          np.where((df['skill'] == 'attack') & (df['skill'].shift(-1) == 'block') & (df['skill'].shift(-2) == 'block') & (df['play'].shift(-2).str.contains('Block by', na=False)), '/', 
                          np.where((df['score'] != df['score'].shift(-1)) & df['play'].str.contains('Block error', na=False), '=', 
                          np.where((df['score'] != df['score'].shift(-1)) & df['short_play_text'].str.contains('Kill', na=False), '#', 
                          np.where((df['score'] != df['score'].shift(-1)) & df['short_play_text'].str.contains('ace', na=False), '#', 
                          np.where((df['score'] != df['score'].shift(-1)) & (df['short_play_text'].str.contains('Reception by', na=False)) & (df['play'].str.contains('Reception error', na=False)), '=', 
                          np.where((df['score'] != df['score'].shift(-1)) & (df['skill'] == 'block') & df['short_play_text'].str.contains('Block by', na=False), '#', 
                          None))))))))

            df['skill'] = np.where((df['skill'] == 'error') & (df['short_play_text'].str.contains('Set')), 'set', 
                                    np.where((df['skill'] == 'error') & (df['short_play_text'].str.contains('Block')), 'block', 
                                             np.where((df['skill'] == 'error') & (df['short_play_text'].str.contains('Reception')), 'reception', 
                                                      np.where((df['skill'] == 'error') & (df['play'].str.contains('Ball handling')), 'freeball', 
                                                               np.where((df['skill'] == 'error') & (df['play'].str.contains('Block')), 'block', 
                                                                        np.where((df['skill'] == 'error') & (df['short_play_text'] == '') & (df['play'].str.contains('Ball handling')), 'freeball',
                                                               df['skill']))))))
            
            df = df[df['skill'] != 'substitution']
            df = df[df['skill'] != 'challengeoutcome']

            return df

        def analyze_volleyball_match(html):
            plays = parse_volleyball_pbp(html, match_id)
            return plays

        # Main function logic
        sched = self.fetch_schedule(season_id)
        sch_df = pd.DataFrame(sched)
        match_id_list = list(sch_df["match_id"].unique())
        
        results = {}
        
        if summary:
            match_data = []
            for match_id in match_id_list:
                url = f"https://stats.ncaa.org/contests/{match_id}/box_score"
                response = requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                })
                soup = BeautifulSoup(response.content, "html.parser")
                game_data = soup.find('table', attrs={'style': 'border-collapse: collapse'})
                
                data = {
                    "teams": [],
                    "summary": {}
                }
                
                header_row = game_data.find("tr")
                sets = [cell.text.strip() for cell in header_row.find_all("td")[1:]]
                
                rows = game_data.find_all("tr")[1:3]
                for row in rows:
                    cells = row.find_all("td")
                    team_name = cells[0].text.strip()
                    scores = [int(cell.text.strip()) for cell in cells[1:-1]]
                    set_wins = int(cells[-1].text.strip())
                    data["teams"].append({
                        "name": team_name,
                        "set_scores": dict(zip(sets, scores)),
                        "sets_won": set_wins,
                    })
                
                summary_rows = game_data.find_all("tr")[3:]
                data["summary"] = {
                    "date": summary_rows[0].text.strip(),
                    "location": summary_rows[1].text.strip(),
                    "attendance": summary_rows[2].text.strip().replace("Attendance: ", "")
                }
                match_data.append(data)
            results['summary'] = match_data
            return results

        if box_score:
            box_score_data = []
            for match_id in match_id_list:
                df_one = pd.read_html(f'https://stats.ncaa.org/contests/{match_id}/individual_stats')[3]
                df_one['team'] = np.where(df_one['Name'] == 'TEAM', df_one['Name'].shift(-1), None)[-2]
                df_one['match_id'] = match_id
                df_one = df_one[~df_one['P'].isna()]
                
                df_two = pd.read_html(f'https://stats.ncaa.org/contests/{match_id}/individual_stats')[4]
                df_two['team'] = np.where(df_two['Name'] == 'TEAM', df_two['Name'].shift(-1), None)[-2]
                df_two['match_id'] = match_id
                df_two = df_two[~df_two['P'].isna()]
                
                df = pd.concat([df_one, df_two])
                df['#'] = df['#'].astype(int)
                box_score_data.append(df)
            results['box_score'] = pd.concat(box_score_data).reset_index(drop=True)
            return results

        if pbp:
            pbp_data = []
            for match_id in match_id_list:
                url = f"https://stats.ncaa.org/contests/{match_id}/play_by_play"
                response = requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                })
                
                match_stats = analyze_volleyball_match(response.content)
                pbp_data.append(match_stats)
            df = pd.concat(pbp_data)
            return pbp_data
