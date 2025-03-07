import requests
from urllib.parse import urlparse, parse_qs

class PVF:
    # Function to get team details in the specified format
    def get_team_details(self, team_id, game):
        return {
            "id": game.get(f"{team_id}_team", {}).get("id", ""),
            "name": game.get(f"{team_id}_team", {}).get("name", ""),
            "img": game.get(f"{team_id}_team_logo", {}).get("src", ""),
            "score": game.get(f"{team_id}_team", {}).get(f"{team_id}_team_score", ""),
            "color": game.get(f"{team_id}_team", {}).get("color", ""),
        }

    # Method to fetch and process teams
    def fetch_teams(self):
        """
        Fetches the roster of volleyball players for a given team from the PVF API.

        Arguments
        ---------
        roster_id : str
            The ID of the team's roster to be fetched. For example, use '40' to fetch players for a specific roster.

        Example
        -------
            >>> pvf = PVF(api_url='https://provolleyball.com/api/rosters/')
            >>> players = pvf.fetch_players(roster_id='40')
            >>> len(players)
            12

        Returns
        -------
        **list[dict]**: A list of player entries, each represented as a dictionary containing player details, 
            such as name, position, height, college, and team name.
        """

        # Fetch JSON data
        url = "https://provolleyball.com/api/teams?include&sort%5B0%5D=sort&sort%5B1%5D=name"
        response = requests.get(url)
        response.raise_for_status()
        teams_json = response.json().get('data', [])

        # Initialize the players list
        teams = []

        # Process each team entry
        for team in teams_json:
            # Extract player details
            team_id = team.get("id", "")
            name = team.get("name", '')
            img = team.get("featured_banner_image", {}).get("src", "")
            color = team.get("color", '')
            current_roster_id = team.get('current_roster_id', '')
            current_season_id = team.get("current_season_id", '')
            url = team.get("permalink", '')

            # Combine the details into the desired player entry structure
            team_entry = {
                'team_id': team_id,
                'name': name,
                # 'img': img,
                # 'color': color,
                'current_roster_id': current_roster_id,
                'current_season_id': current_season_id,
                'url': "https://provolleyball.com" + url
            }

            # Add the player entry to theteams list
            teams.append(team_entry)

        return teams

    # Method to fetch and process schedule
    def fetch_schedule(self, when='upcoming', season_id='3'):
        """
        Fetches the schedule of volleyball games for the given season from the PVF API.

        Arguments
        ---------
        season_id : str
            The ID of the season for which the schedule is to be fetched. 
            This parameter specifies which season's schedule to retrieve (e.g., '1' for a specific season).
        when : str
            Specifies the time period for the games to be fetched. 
            'past' for completed matches.
            'upcoming' for matches that are yet to happen.

        Example
        -------
            >>> pvf = PVF(when='past', season_id='1')
            >>> schedule = pvf.fetch_schedule()
            >>> len(schedule)
            20

        Returns
        -------
        **list[dict]**: A list of match entries, each represented as a dictionary containing match details, 
        such as team names, scores, and match times.
        """
        schedule_url = f'https://provolleyball.com/api/schedule-events/?filter%5Bevent_state%5D={when}&filter%5Bseason_id%5D={season_id}&sort%5B0%5D=start_datetime&include%5B0%5D=firstTeam&include%5B1%5D=secondTeam&include%5B2%5D=season&include%5B3%5D=links&include%5B4%5D=links.image&include%5B5%5D=firstTeamLogo&include%5B6%5D=secondTeamLogo&include%5B7%5D=presentedByLogo&per_page=200&page=1'
        title_corrections = {
            "Indy Ignite at Orlando Valkryies": "Indy Ignite at Orlando Valkyries"
        }
        # Fetch JSON data
        response = requests.get(schedule_url)
        response.raise_for_status()  # Raise error for HTTP issues
        games = response.json().get('data', [])

        # Initialize the schedule list
        schedule = []

        # Process each game in the response
        for game in games:
            # Extract the title
            title = game.get('title', "")

            # Correct the title if it matches a known typo
            if title in title_corrections:
                title = title_corrections[title]

            # Determine home and away teams
            if " at " in title:
                away_team, home_team = title.split(" at ")
            elif " vs " in title:
                home_team, away_team = title.split(" vs ")
            elif " vs. " in title:
                home_team, away_team = title.split(" vs. ")
            else:
                print(f"Skipping game with invalid title format: {title}")
                continue  # Skip this game if the title format is invalid

            # Strip and clean the team names
            home_team = home_team.strip()
            away_team = away_team.strip()

            # Fetch team names from API response
            first_team = game.get("first_team", {}).get("name", "")
            second_team = game.get("second_team", {}).get("name", "")

            # Initialize home and away team details
            if first_team == home_team:
                home_details = self.get_team_details("first", game)
                away_details = self.get_team_details("second", game)
            elif second_team == home_team:
                home_details = self.get_team_details("second", game)
                away_details = self.get_team_details("first", game)
            else:
                print(f"Skipping game due to team mismatch: {title}")
                continue  # Skip the game if team names do not match

            # Combine the details into the desired match entry structure
            match_entry = {
                "score": game.get('result_text', ''),
                "date": game.get('start_datetime'),
                "location": game.get('location', ""),
                "home_team_name": home_details["name"],
                "home_team_img": home_details["img"],
                "away_team_name": away_details["name"],
                "away_team_img": away_details["img"],
                "team_stats": "https://widgets.volleystation.com/team-stats/" + str(game.get('volley_station_match_id', "")),
                "scoreboard": "https://widgets.volleystation.com/scoreboard/" + str(game.get('volley_station_match_id', "")),
                "video": game.get('presented_by_url', '')
            }

            # Add the match entry to the schedule
            schedule.append(match_entry)
            
            
        return schedule

    # Method to fetch and process players
    def fetch_players(self):
        """
        Fetches the roster of volleyball players for all teams from the PVF API.

        Example
        -------
            >>> pvf = PVF(api_url='https://provolleyball.com/api/rosters/')
            >>> players = pvf.fetch_players()
            >>> len(players)
            120

        Returns
        -------
        **list[dict]**: A list of player entries, each represented as a dictionary containing player details, 
            such as name, position, height, college, and team name.
        """
        teams = self.fetch_teams()
        players = []

        for roster_ids in teams:
            roster_id = roster_ids['current_roster_id']
            try:
                url = f"https://provolleyball.com/api/rosters/{roster_id}/player-rosters?include%5B1%5D=headshotImage&include%5B2%5D=player.headshotImage&include%5B3%5D=positions&sort%5B0%5D=players.last_name"
                response = requests.get(url, params={"roster_id": roster_id})
                response.raise_for_status()
                rosters = response.json().get('data', [])

                for roster in rosters:
                    player_id = roster.get("player_id", "")
                    full_name = roster.get("player", {}).get("full_name", "")
                    college = roster.get("player", {}).get("college", "")
                    hometown = roster.get("player", {}).get("hometown", "")
                    height_feet = roster.get('player', {}).get('height_feet', '')
                    height_inches = roster.get('player', {}).get('height_inches', '')
                    height = f"{height_feet}'{height_inches}" if height_feet and height_inches else "Unknown"
                    jersey_number = roster.get("player", {}).get("jersey_number", "")
                    pro_experience = roster.get("player", {}).get("pro_experience", "")
                    player_positions = ", ".join(pos.get('name') for pos in roster.get("player_positions", []))
                    team = " ".join(word.title() for word in roster.get("permalink", "").split("/")[2].split('-'))
                    url = "https://provolleyball.com" + roster.get('player', {}).get('permalink', '')
                    

                    player_entry = {
                        "player_id": player_id,
                        "full_name": full_name,
                        "college": college,
                        "hometown": hometown,
                        "height": height,
                        "jersey_number": jersey_number,
                        "pro_experience": pro_experience,
                        "player_positions": player_positions,
                        "team": team,
                        "Player URL": url,
                        "conference_name": 'PVF',
                        "conference_short": 'PVF',
                        'division': 'Pro',
                    }

                    players.append(player_entry)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching players for roster_id {roster_id}: {e}")

        return players
    
    # Method to fetch team stats for the season
    def fetch_team_stats(self):
        """
        Fetches the team stats of the season. Currently no way to distinguish between seasons

        Example
        -------
            >>> pvf = PVF(api_url='https://provolleyball.com/api/rosters/')
            >>> players = pvf.fetch_players(roster_id='40')
            >>> len(players)
            12

        Returns
        -------
        **list[dict]**: A list of stats by team.

        """

        # Fetch JSON data
        url = "https://provolleyball.com/api/volley-station/team-stats"
        response = requests.get(url)
        response.raise_for_status()
        stats = response.json().get('data', [])
        
        return stats
        
    # Method to fetch team stats for the season
    def fetch_player_stats(self):
        """
        Fetches the player stats of the season. Currently no way to distinguish between seasons

        Example
        -------
            >>> pvf = PVF()
            >>> player_stats = pvf.fetch_player_stats()
            >>> len(player_stats)
            112

        Returns
        -------
        **list[dict]**: A list of stats by player.

        """

        # Fetch JSON data
        # Define the initial URL
        url = "https://provolleyball.com/api/volley-station/player-stats"
        response = requests.get(url)
        response.raise_for_status()

        # Get the links
        links = response.json().get('links', {})
        first = links['first']
        last = links['last']

        # Extract page numbers from the first and last URLs
        def get_page_number(url):
            query = urlparse(url).query
            params = parse_qs(query)
            return int(params.get('page', [1])[0])

        first_page = get_page_number(first)
        last_page = get_page_number(last)

        # Loop through all pages
        all_data = []
        for page in range(first_page, last_page + 1):
            paginated_url = f"https://provolleyball.com/api/volley-station/player-stats?page={page}"
            page_response = requests.get(paginated_url)
            page_response.raise_for_status()
            
            # Parse JSON response
            json_data = page_response.json()
            players = json_data.get('data', [])  # Adjust if your player stats are under a different key
            
            # Process each player's stats
            for player in players:
                player_dict = {
                    'assists': player.get('assists', ''),
                    'block_win': player.get('block_win', ''),
                    'break_point_attempts': player.get('break_point_attempts', ''),
                    'played_matches': player.get('played_matches', ''),
                    'played_sets': player.get('played_sets', ''),
                    'player_roster_id': player.get('player_roster_id', ''),
                    'points': player.get('points', ''),
                    'serve_win': player.get('serve_win', ''),
                    'side_out': player.get('side_out', ''),
                    'side_out_attempts': player.get('side_out_attempts', ''),
                    'spike_eff': player.get('spike_eff', ''),
                    'spike_ratio': player.get('spike_ratio', ''),
                    'spike_total': player.get('spike_total', ''),
                    'spike_win': player.get('spike_win', ''),
                    'successful_digs': player.get('successful_digs', ''),
                    'sum_points': player.get('sum_points', ''),
                    'won_matches': player.get('won_matches', ''),
                    'won_sets': player.get('won_sets', '')
                }
                # Append the player dict to the all_data list
                all_data.append(player_dict)
        
        return all_data

pvf = PVF()
print(pvf.fetch_schedule(when='past'))