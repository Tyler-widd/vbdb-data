import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re

class NCAA:
    """
    A class to interact with NCAA statistics and data.
    """
    
    def __init__(self, gender):
        # Generic headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.gender = gender
        
        # Common conference abbreviation mappings
        self.conference_mapping = {
            "WAC": "Western Athletic Conference",
            "PWC": "Pacific West Conference",
            "RMAC": "Rocky Mountain Athletic Conference",
            "NE-10": "Northeast-10 Conference",
            "MIAA-MI": "Michigan Intercollegiate Athletic Association",
            "CCS": "Collegiate Conference of the South",
            "MAC": "Mid-American Conference",
            "SEC": "Southeastern Conference",
            "SWAC": "Southwestern Athletic Conf.",
            "GSC": "Gulf South Conference",
            "AAC": "American Athletic Conference",
            "GNWAC": "Great Northwest Athletic Conference",
            "AmerEast": "America East Conference",
            "SIAC": "Southern Intercol. Ath. Conf.",
            "GNEC": "Great Northeast Athletic Conference",
            "MAC-Mid": "Middle Atlantic Conference Commonwealth",
            "AMCC": "Allegheny Mountain Collegiate Conference",
            "E8": "Empire 8",
            "PAC": "Presidents' Athletic Conference",
            "NACC": "Northern Athletics Collegiate Conference",
            "PL": "Patriot League",
            "NESCAC": "New England Small College Athletic Conference",
            "HCAC": "Heartland Collegiate Athletic Conference",
            "SAC": "South Atlantic Conference",
            "LSC": "Lone Star Conference",
            "SBC": "Sun Belt Conference",
            "Big 12": "Big 12 Conference",
            "GAC": "Great American Conference",
            "MIAA-MA": "Mid-America Intercollegiate Athletics Association",
            "OVC": "Ohio Valley Conference",
            "IND": "Independent",
            "GMAC": "Great Midwest Athletic Conference",
            "MIAC": "Minnesota Intercollegiate Athletic Conference",
            "PBC": "Peach Belt Conference",
            "CCIW": "College Conference of Illinois & Wisconsin",
            "NSIC": "Northern Sun Intercollegiate Conference",
            "SCAC": "Southern Collegiate Athletic Conference",
            "ASUN": "Atlantic Sun Conference",
            "ODAC": "Old Dominion Athletic Conf.",
            "NEWMAC": "New England Women's and Men's Athletic Conference",
            "OAC": "Ohio Athletic Conference",
            "LL": "Liberty League",
            "SSC": "Sunshine State Conference",
            "Conf-CAR": "Conference Carolinas",
            "CUNYAC": "City University of New York Athletic Conference",
            "MVC": "Missouri Valley Conference",
            "MWC-MW": "Midwest Conference",
            "SAA": "Southern Athletic Association",
            "UMAC": "Upper Midwest Athletic Conference",
            "SLIAC": "St. Louis Intercollegiate Athletic Conference",
            "CACC": "Central Atlantic Collegiate Conference",
            "PSAC": "Pennsylvania State Athletic Conference",
            "CIAA": "Central Intercollegiate Athletic Association",
            "MWC-Mtn": "Mountain West Conference",
            "ACC": "Atlantic Coast Conference",
            "UAA": "University Athletic Association",
            "USA South": "USA South Athletic Conference",
            "MASCAC": "Massachusetts State Collegiate Athletic Conference",
            "Ivy": "The Ivy League",
            "UEC": "United East Conference",
            "Cent-Conf": "Centennial Conference",
            "ARC": "American Rivers Conference",
            "SUNYAC": "State University of New York Athletic Conference",
            "Big East": "Big East Conference",
            "CCAA": "California Collegiate Athletic Association",
            "SCIAC": "Southern California Intercollegiate Athletic Conf.",
            "Big West": "Big West Conference",
            "Big Sky": "Big Sky Conference",
            "Big Ten": "Big Ten Conference",
            "C2C": "Coast-To-Coast Athletic Conference",
            "CAA": "Coastal Athletic Association",
            "MAAC": "Metro Atlantic Athletic Conference",
            "LC": "Landmark Conference",
            "AtlEast": "Atlantic East Conference",
            "NEC": "Northeast Conference",
            "MEC": "Mountain East Conference",
            "Big South": "Big South Conference",
            "SoCon": "Southern Conference",
            "HL": "Horizon League",
            "NAC": "North Atlantic Conference",
            "MEAC": "Mid-Eastern Athletic Conf.",
            "CNE": "Conference of New England",
            "ECC": "East Coast Conference",
            "GLIAC": "Great Lakes Intercollegiate Athletic Conference",
            "A-10": "Atlantic 10 Conference",
            "NCAC": "North Coast Athletic Conference",
            "Summit": "The Summit League",
            "GLVC": "Great Lakes Valley Conference",
            "SLC": "Southland Conference",
            "ASC": "American Southwest Conference",
            "LEC": "Little East Conference",
            "Sky-Conf": "Skyline Conference",
            "C-USA": "Conference USA",
            "NWC": "Northwest Conference",
            "WCC": "West Coast Conference",
            "NJAC": "New Jersey Athletic Conference",
            "Pac-12": "Pac-12 Conference",
            "WIAC": "Wisconsin Intercollegiate Athletic Conference"
        }

        self.reverse_mapping = {v: k for k, v in self.conference_mapping.items()}
        
    def fetch_html_soup(self, url):
        """
        Normal process to produce soup from html

        Args:
            url (str): Url you'd like to get beautiful soup from
            
        Returns:
            BeautifulSoup: Parsed HTML content
        """
        request = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(request.content, 'html.parser')
        return soup
    
    def map_short_conf(self, df):
        """
        Maps full conference names to abbreviations
        
        Args:
            df (pandas.DataFrame): DataFrame containing conferenceName column
            
        Returns:
            pandas.DataFrame: DataFrame with added confAbbreviation column
        """
        # Use the reverse mapping to look up each conference name
        df['confAbbreviation'] = df['conferenceName'].map(self.reverse_mapping)
        return df
    
    def fetch_team_season(self, url, year):
        """
        Fetches the season URL for a specific team and year
        
        Args:
            url (str): Base URL for the team
            year (str): Season year format (e.g., '2024-25')
            
        Returns:
            str: URL path for the specified season
        """
        soup = self.fetch_html_soup(url)
        data = soup.find('a', string=year)
        return data['href']

    def fetch_ncaa_teams(self):
        """
        Return dataframe of NCAA teams and metadata
        
        Returns:
            pandas.DataFrame: NCAA teams with metadata
        """
        # Fetch simple team codes
        df = pd.read_html('https://stats.ncaa.org/game_upload/team_codes')[0]
        team_codes = df[(df[0] != 'ID') & (df[0] != 'NCAA Codes')].rename(columns={0: 'orgId', 1: 'team_short'})
        
        # Fetch the team metadata
        df_json = pd.read_json(f'https://web3.ncaa.org/directory/api/directory/memberList?type=12&sportCode={self.gender}VB')[['orgId', 'nameOfficial', 'divisionRoman', 'athleticWebUrl', 'conferenceName']]
        df_json['orgId'] = df_json['orgId'].astype(str)
        
        # Merge
        df = pd.merge(df_json, team_codes, how='left')
        
        return self.map_short_conf(df)

    def fetch_schedule_for_team(self, team_id, year):
        """
        Fetch schedule data for a specific team and year
        
        Args:
            team_id (str): Team identifier
            year (str): Season year format '2024-25'
            
        Returns:
            pandas.DataFrame: Schedule data for the team
        """
        # Fetch teams to join home team info
        teams = self.fetch_ncaa_teams()

        # Start process to get schedule
        url = "https://stats.ncaa.org" + self.fetch_team_season(url=f"https://stats.ncaa.org/teams/history/{self.gender}VB/{team_id}", year=year)
        print(url)
        soup = self.fetch_html_soup(url)

        # get game by game urls
        data = soup.find('a', string='Game By Game')
        if data is None:
            print(f"No 'Game By Game' link found for team {team_id} in season {year}")
            return pd.DataFrame()  # Return empty DataFrame
        gbg_url = "https://stats.ncaa.org" + data['href']
        
        # Use game by game url and get the soup from that url
        gbg_soup = self.fetch_html_soup(gbg_url)
        
        game_rows = gbg_soup.find_all('tr', id=re.compile(r'^contest_\d+'))
        data = []
        for row in game_rows:
            match_id = row['id'].replace('contest_', '')
            match_id = match_id.replace('_defense', '')

            date = row.find('td').text.strip()
            
            # Team info (assuming this is available in the soup)
            team_img = soup.find_all('img')[1]['src'] if len(soup.find_all('img')) > 1 else ""
            team_id = team_img.split('//')[-1].replace(".gif", '') if team_img else ""
            
            # Opponent cell processing
            opponent_cell = row.find_all('td')[1]
            opponent_text = opponent_cell.text.strip()
            
            # Determine location
            if '@' in opponent_text:
                location = 'away'
            elif '2024 NCAA' in opponent_text: 
                location = 'NCAA'
            else:
                location = 'home'
                    
            # Extract opponent info safely
            opponent_link = None  # Initialize before the loop
            for a_tag in opponent_cell.find_all('a'):
                # Only consider links with images that have height and width attributes
                # This will filter out the defensive stats image which doesn't have these attributes
                img_tag = a_tag.find('img')
                if img_tag and img_tag.has_attr('height') and img_tag.has_attr('width'):
                    opponent_link = a_tag
                    break
            
            opponent_name = "Unknown"
            opponent_img = ""
            opponent_id = ""
            opponent_season_id = ""
            
            if opponent_link:
                # Extract text after the image
                img_tag = opponent_link.find('img')
                if img_tag:
                    opponent_img = img_tag['src']
                    opponent_id = opponent_img.split('//')[-1].replace('.gif', '')
                    
                    # Get opponent name (text after the image)
                    opponent_name_parts = []
                    for content in opponent_link.contents:
                        if not isinstance(content, str) and content.name == 'img':
                            continue
                        opponent_name_parts.append(str(content).strip())
                    opponent_name = ' '.join(opponent_name_parts).strip()
                    
                    # If opponent name is empty, try using alt attribute
                    if not opponent_name and img_tag.get('alt'):
                        opponent_name = img_tag['alt']
                    
                    # Remove ranking prefix (like "#8")
                    opponent_name = re.sub(r'^#\d+\s+', '', opponent_name)
                
                opponent_season_id = opponent_link['href'].split('/')[-1]
            else:
                # Handle case where there's no link (like Paul Smiths)
                # Extract just the opponent name without location info
                opponent_name = opponent_text.split('\n')[0].strip()
                if '@' in opponent_name:
                    opponent_name = opponent_name.split('@')[1].strip()
                
                # Remove ranking prefix (like "#8")
                opponent_name = re.sub(r'^#\d+\s+', '', opponent_name)
            
            # Get result
            result_cell = row.find_all('td')[2]
            result = result_cell.text.strip() if result_cell else ""
            
            data.append({
                'match_id': match_id,
                'date': date,
                'team_id': team_id,
                'opponent_name': opponent_name,
                'opponent_id': opponent_id,
                'team_season_id': url.split('/')[-1],
                'team_img': team_img,
                'opponent_season_id': opponent_season_id,
                'opponent_img': opponent_img,
                'location': location,
                'result': result
            })
            
        df = pd.DataFrame(data)
            
        df = pd.merge(df, teams, left_on='team_id', right_on='orgId', how='left')
        df = pd.merge(df, teams[['orgId', 'nameOfficial', 'divisionRoman', 'conferenceName']].rename(columns={'orgId': 'opponent_id', 'nameOfficial': 'oppNameOfficial', 'divisionRoman': "oppDivision", 'conferenceName': 'oppConference'}), how='left')
        df = df[df['opponent_name'] != 'Defensive Totals']
        df = df[df['date'] != '']
        return df

    def fetch_schedule(self, divisions=None):
        """
        Fetch schedule data for specified NCAA divisions
        
        Args:
            divisions (list or str, optional): List of divisions ('I', 'II', 'III') or a single division.
                                            If None, fetches all divisions.
        
        Returns:
            pandas.DataFrame: Combined schedule data for all requested divisions
        """
        # Handle input flexibility
        if divisions is None:
            divisions = ['I', 'II', 'III']
        elif isinstance(divisions, str):
            divisions = [divisions]
            
        # Fetch teams
        teams = self.fetch_ncaa_teams()
        
        # Initialize list to store schedules
        all_schedules = []
        
        # Process each division
        for division in divisions:
            print(f"Fetching Division {division} schedules...")
            
            # Fetch teams for the specified division
            teams_df = teams[teams['divisionRoman'] == division]
            
            # Loop through all unique orgIds for this division
            for team_id in teams_df['orgId'].unique():
                try:
                    team_schedule = self.fetch_schedule_for_team(team_id=team_id, year='2024-25')
                    team_schedule['division'] = division
                    all_schedules.append(team_schedule)
                except Exception as e:
                    print(f"Error fetching schedule for team ID {team_id}: {e}")
                    continue
        
        # Concatenate all team schedules into one DataFrame
        if all_schedules:
            return pd.concat(all_schedules, ignore_index=True)
        else:
            return pd.DataFrame()  # Return empty DataFrame if no schedules were fetched

    def fetch_teams_history(self, team_id):
        """
        Fetch a team's history.

        Parameters:
            gender (str): 'M' | 'W'
            team_id (str): The ID of the team.

        Returns:
            list: A list of dictionaries containing team history
        """
        url = f"https://stats.ncaa.org/teams/history/{self.gender}VB/{team_id}"
        response = requests.get(url, headers=self.headers)

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

    def fetch_players(self):
        """
        Function to gather D1-D3 NCAA rosters.

        Parameters:
            gender (str): 'M' | 'W'

        Returns:
            list: A list of dictionaries containing player information
        """
        # Get all team codes and clean a bit of data
        df = pd.read_html("https://stats.ncaa.org/game_upload/team_codes")[0]
        df = df[(df[0] != "NCAA Codes") & (df[0] != "ID")]
        df.rename(columns={0: "team_id", 1: "team_name"}, inplace=True)

        json_data = requests.get(
            f"https://web3.ncaa.org/directory/api/directory/memberList?type=12&sportCode={self.gender}VB&"
        ).json()
        
        teams_dict = []
        for json in json_data:
            teams_dict.append(
                {
                    "team_id": json["orgId"],
                    "team_name": json["nameOfficial"],
                    "conference_id": json["conferenceId"],
                    "conference_name": json["conferenceName"],
                    "school_url": json["webSiteUrl"],
                    "division": json["divisionRoman"],
                    "school_athletic_url": json["athleticWebUrl"],
                    "sportRegion": json["sportRegion"],
                    "state": json["memberOrgAddress"]["state"],
                }
            )
        teams_df = pd.json_normalize(teams_dict)
        teams_df["team_id"] = teams_df["team_id"].astype(str)
        
        # List to store team data
        team_data = []

        # Loop through each team_id
        for team_id in teams_df["team_id"].unique():
            url = f"https://web3.ncaa.org/directory/orgDetail?id={team_id}"
            response = requests.get(url, headers=self.headers)

            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the specific table
            table = soup.find(
                "table", attrs={"class": "table table-responsive table-condensed table-striped"}
            )
            if not table:
                continue

            rows = table.find_all("tr")
            for row in rows[1:]:  # Skip header row
                columns = row.find_all("td")
                if self.gender == "W":
                    gender_text = "Women's"
                else:
                    gender_text = "Men's"
                if columns and columns[0].text.strip() == f"{gender_text} Volleyball":
                    team_data.append(
                        {
                            "team_id": team_id,
                            "head_coach": columns[1].text.strip(),
                            "division_hist_url": columns[2].text.strip(),
                            "conference": columns[3].text.strip(),
                        }
                    )

        df = pd.json_normalize(team_data)
        df["head_coach"] = df["head_coach"].apply(
            lambda x: " ".join(x.split()) if isinstance(x, str) else x
        )

        teams = pd.read_html("https://stats.ncaa.org/game_upload/team_codes")[0]
        teams = teams[(teams[0] != "NCAA Codes") & (teams[0] != "ID")]
        teams.rename(columns={0: "team_id", 1: "team_short"}, inplace=True)
        teams["team_id"] = teams["team_id"].astype(str)
        df["team_id"] = df["team_id"].astype(str)
        df = pd.merge(df, teams, on="team_id")

        team_ids = list(df["team_id"].dropna().unique())
        roster_list = []

        for team_id in team_ids:
            url = f"https://stats.ncaa.org/teams/history/{self.gender}VB/{team_id}"
            response = requests.get(url, headers=self.headers)

            soup = BeautifulSoup(response.content, "html.parser")
            roster_link = soup.find('td').find('a')['href']
            conference_short = soup.find_all('tr')[1].find_all('td')[3].text
            response = requests.get(
                "https://stats.ncaa.org" + roster_link + "/roster",
                headers=self.headers
            )

            soup = BeautifulSoup(response.content, "html.parser")
            
            table = soup.find('table', {'id': lambda x: x and x.startswith('rosters_form_players')})
            if not table:
                continue

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

        # Concatenate all roster DataFrames
        if roster_list:
            roster_list_df = pd.concat(roster_list).reset_index(drop=True)
            final_df = pd.merge(roster_list_df, df, on='team_id')
            final_final_df = pd.merge(final_df, teams_df, on='team_id')
            final_data = final_final_df[['#', 'Name', 'Class', 'Position', 'Height', 'Hometown', 
                                 'High School', 'Player URL', 'team_id', 'head_coach', 
                                 'division_hist_url', 'division', 'team_name', 'team_short', 
                                 'conference_name', 'conference_short', 'state', 'sportRegion', 
                                 'school_url', 'school_athletic_url']].to_dict(orient='records')
            return final_data
        else:
            return []

    def fetch_match_details(self, season_id, summary=False, box_score=False, pbp=False):
        """
        Fetch detailed match information for a given season ID
        
        Parameters:
            season_id (str): Season ID to fetch match details for
            summary (bool): Whether to fetch match summary
            box_score (bool): Whether to fetch box score data
            pbp (bool): Whether to fetch play-by-play data
            
        Returns:
            dict or DataFrame: Match details as requested
        """
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

        def analyze_volleyball_match(html, match_id):
            plays = parse_volleyball_pbp(html, match_id)
            return plays

        # Main function logic
        try:
            # Using fetch_schedule might not work directly with season_id
            # You may need to adjust how you get the match IDs
            sch_df = pd.DataFrame(self.fetch_schedule())
            match_id_list = list(sch_df["match_id"].unique())
        except:
            # Fallback to directly using the season_id
            print(f"Using season ID directly: {season_id}")
            match_id_list = [season_id]
        
        results = {}
        
        if summary:
            match_data = []
            for match_id in match_id_list:
                url = f"https://stats.ncaa.org/contests/{match_id}/box_score"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, "html.parser")
                game_data = soup.find('table', attrs={'style': 'border-collapse: collapse'})
                
                if not game_data:
                    continue
                
                data = {
                    "match_id": match_id,
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

        if box_score:
            box_score_data = []
            for match_id in match_id_list:
                try:
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
                except Exception as e:
                    print(f"Error fetching box score for match {match_id}: {e}")
                    continue
                    
            if box_score_data:
                results['box_score'] = pd.concat(box_score_data).reset_index(drop=True)
            else:
                results['box_score'] = pd.DataFrame()

        if pbp:
            pbp_data = []
            for match_id in match_id_list:
                try:
                    url = f"https://stats.ncaa.org/contests/{match_id}/play_by_play"
                    response = requests.get(url, headers=self.headers)
                    
                    match_stats = analyze_volleyball_match(response.content, match_id)
                    pbp_data.append(match_stats)
                except Exception as e:
                    print(f"Error fetching play by play for match {match_id}: {e}")
                    continue
                    
            if pbp_data:
                results['pbp'] = pd.concat(pbp_data).reset_index(drop=True)
            else:
                results['pbp'] = pd.DataFrame()

        return results

# # Example usage
# if __name__ == "__main__":
#     ncaa = NCAA(gender='W')
    
#     # Example 1: Fetch NCAA teams
#     teams = ncaa.fetch_ncaa_teams()
#     print(f"Retrieved {len(teams)} teams")
    
#     # Example 2: Fetch schedule for a specific division
#     #div_schedules = ncaa.fetch_schedule('I')  # Division I only
#     #print(f"Retrieved {len(div_schedules)} Division I schedule entries")
    
#     # Example 3: Fetch a specific team's schedule
#     if len(teams) > 0:
#         team_ids = teams['orgId'].iloc[0:2]
#         df_list = []
#         for team_id in team_ids:
#             team_schedule = ncaa.fetch_schedule_for_team(team_id, '2024-25')
#             df_list.append(team_schedule)
        
#         df = pd.concat(df_list)
#         print(df)
#         print(f"Retrieved {len(df)} games for team {team_ids}")

