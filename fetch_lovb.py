import requests
from bs4 import BeautifulSoup
from seleniumbase import Driver
import re
from datetime import datetime
import numpy as np
import pandas as pd

class LOVB:

    # Method to fetch and process teams
    def fetch_teams(self):
        """
        Fetches teams the LOVB site.

        Example
        -------
            >>> lovb = LOVB(api_url='https://provolleyball.com/api/rosters/')
            >>> teams = lovb.fetch_teams()
            >>> len(teams)
            6

        Returns
        -------
        **list[dict]**: A list of team entries.
        """

        # Target URL
        url = "https://www.lovb.com/"

        # Fetch the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all divs with the specific class
        divs = soup.find_all('div', attrs={'class': 'card relative w-full overflow-hidden'})

        # Loop through each div and extract the href or text inside the <a> tag
        teams = []
        for card in divs:
            a_tag = card.find('a')
            if a_tag:
                link = a_tag.get('href', 'No href found')  # Extract the link
                
                # Construct the team details
                team_name = " ".join(link.split('teams')[1].split('lovb')[1].split("-")[:-1]).title().strip()
                full_url = "https://www.lovb.com" + link
                team_id = link.split('/')[-1]  # Extract team_id from the URL
                
                # Append team info as a dictionary
                teams.append({
                    'name': team_name,
                    'url': full_url,
                    'team_id': team_id,
                    'schedule': full_url + "/schedule",
                    'roster': full_url + "/roster",
                })
            else:
                print("No <a> tag found in this card.")

        return teams

    # Method to fetch and process rosters
    def fetch_rosters(self):
        teams = self.fetch_teams()
        roster_urls = []
        for team in teams:
            roster_urls.append(team['roster'])

        driver = Driver(browser="chrome", headless=True)
        all_data = []
        unwanted_terms = ["Founding Athlete", "NEW", '-founding-athlete']

        for url in roster_urls:
            try:
                driver.get(url)  # Open the URL
                print(f"Fetching {url}")
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')

                # Find all the tables with class 'roster-table'
                tables = soup.find_all('table', class_='roster-table')

                if not tables:  # If no tables are found, skip this URL
                    print(f"Warning: No roster table found at {url}")
                    continue

                # Loop through each table
                for table in tables:
                    headers = [header.text.strip() for header in table.find_all('th')]

                    # Extract data from each row in the table
                    for row in table.find_all('tr')[1:]:  # Skip the header row
                        columns = row.find_all('td')

                        if columns:
                            row_data = {}
                            row_data['url'] = url  # Store URL for team name extraction later

                            # Extract and clean up the player's name and number from the first column
                            player_name_column = columns[0].get_text(strip=True)

                            # Use regex to separate the player number from the name
                            match = re.match(r"(\d+)([A-Za-z\s]+)", player_name_column)
                            if match:
                                player_number = match.group(1)  # The number (e.g., '1')
                                raw_player_name = match.group(2).strip()  # The name (e.g., 'Jordyn Poulter')
                                player_name = re.sub(r'(?<!^)([A-Z])', r' \1', raw_player_name)
                            else:
                                player_number = ''
                                player_name = player_name_column

                            for term in unwanted_terms:
                                player_name = player_name.replace(term, '').strip()
                                player_name = player_name.replace("  ", ' ').strip()

                            # Add the player number and name to the dictionary
                            row_data['Player Number'] = player_number
                            row_data['Name'] = player_name

                            # For each other column, map it to the corresponding header
                            for header, column in zip(headers[1:], columns[1:]):
                                column_text = column.get_text(strip=True)
                                row_data[header] = column_text

                            # Add the row's dictionary to all_data
                            all_data.append(row_data)

            except Exception as e:
                print(f"Error processing {url}: {e}")

        # Now process all the data after collecting it
        processed_data = []
        for item in all_data:
            # Determine team name from URL
            if 'atlanta' in item['url']:
                team_name = 'Atlanta'
            elif 'salt' in item['url']:
                team_name = 'Salt Lake'  
            elif 'austin' in item['url']:
                team_name = 'Austin'
            elif 'houston' in item['url']:
                team_name = 'Houston'
            elif 'madison' in item['url']:
                team_name = 'Madison'
            elif 'omaha' in item['url']:
                team_name = 'Omaha'
            else:
                team_name = None

            # Create links
            player_url = "https://www.lovb.com/teams/lovb-" + team_name.lower() + "-volleyball/athletes/" + item['Name'].replace(' ', '-').lower()
            
            # Create processed entry with all transformations
            processed_entry = {
                '#': item['Player Number'] if item['Player Number'] != '' else 'Staff',
                'Name': item['Name'],
                'Player URL': player_url,
                'team_name': team_name,
                'Team Name': team_name,  # Keep both for backward compatibility
                'division': 'Pro',
                'team_short': team_name,
                'conference_name': 'LOVB',
                'conference_short': 'LOVB',
            }
            
            # Handle position mapping
            position = item.get('Position', item.get('Title', ''))
            if position == 'Opposite Hitter':
                processed_entry['Position'] = 'OPP'
            elif position == 'Middle Blocker':
                processed_entry['Position'] = 'MB'
            elif position == 'Setter':
                processed_entry['Position'] = 'S'
            elif position == 'Outside Hitter':
                processed_entry['Position'] = 'OH'
            elif position == 'Libero':
                processed_entry['Position'] = 'L'
            else:
                processed_entry['Position'] = position
            
            # Rename columns
            if 'College / Home Club' in item:
                processed_entry['Hometown'] = item['College / Home Club']
            
            # Copy any other fields we want to keep
            for key, value in item.items():
                if key not in ['Title', 'Follow', 'url', 'Player Number', 'College / Home Club'] and key not in processed_entry:
                    processed_entry[key] = value
            
            processed_data.append(processed_entry)
        
        return processed_data

    # Method to fetch and process schedule
    def fetch_results(self):
        """Scrape volleyball matches using the week containers approach"""
        
        url="https://www.lovb.com/schedule"
        driver = Driver(browser="chrome", headless=True)
        driver.get(url)  # Open the URL
        print(f"Fetching {url}")
        
        # Wait for the page to load completely
        driver.sleep(2)  # Add a small delay to ensure content loads
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Find all week containers
        week_containers = soup.find_all('div', attrs={'class': 'mb-lg grid w-full gap-lg'})
        
        all_matches = []
        
        for week_idx, week in enumerate(week_containers):
            print(f"Processing week {week_idx+1}")
            
            # Find all matches within this week
            matches = week.find_all('div', attrs={'class': '[&>header]:first-of-type:rounded-t-md'})
            
            # If no matches found with that specific class, try another approach
            if not matches:
                matches = week.find_all('div', attrs={'class': lambda x: x and 'flex-1' in x and '[&>header]' in x})
            
            for match_idx, match in enumerate(matches):
                try:
                    print(f"  Processing match {match_idx+1}")
                    
                    # Get date for this match
                    date_div = match.find('div', attrs={'class': 'flex items-center gap-sm text-text-secondary'})
                    date = date_div.text.strip() if date_div else "Date not found"
                    
                    # Get match details link
                    match_details_link_elem = match.find('a', attrs={'class': 'link-hover flex items-center gap-sm text-xs'})
                    match_details_link = match_details_link_elem['href'] if match_details_link_elem and match_details_link_elem.has_attr('href') else ""
                    
                    # Find the section with teams and scores
                    section = match.find('section')
                    if not section:
                        print("  No section found, skipping match")
                        continue
                    
                    # Get teams
                    team_links = section.find_all('a', class_='group link-hover flex items-center gap-sm')
                    
                    teams = []
                    for team_link in team_links:
                        team_text_div = team_link.find('div', class_='text-pretty text-sm')
                        if team_text_div:
                            team_text = team_text_div.text.strip()
                            teams.append(team_text)
                    
                    if len(teams) < 2:
                        print("  Not enough teams found, skipping match")
                        continue
                    
                    team_1 = teams[0]
                    team_2 = teams[1]
                    print(f"  Teams: {team_1} vs {team_2}")
                    
                    # Get set scores
                    set_scores_divs = section.find_all('div', class_='flex items-center gap-sm')
                    
                    team_1_set_wins = "0"
                    team_2_set_wins = "0"
                    team_1_set_scores = []
                    team_2_set_scores = []
                    
                    score_divs_processed = 0
                    
                    for score_div in set_scores_divs:
                        # Check if this div contains score information
                        score_elements = score_div.find_all('div', class_=lambda x: x and 'size-4' in x)
                        if not score_elements:
                            continue
                        
                        # Get sets won
                        sets_won_div = score_div.find('div', class_='text-pretty text-sm')
                        sets_won = sets_won_div.text.strip() if sets_won_div else "0"
                        
                        # Get individual set scores
                        set_scores = [elem.text.strip() for elem in score_elements]
                        
                        if score_divs_processed == 0:  # First team
                            team_1_set_wins = sets_won
                            team_1_set_scores = set_scores
                            score_divs_processed += 1
                        elif score_divs_processed == 1:  # Second team
                            team_2_set_wins = sets_won
                            team_2_set_scores = set_scores
                            score_divs_processed += 1
                            break  # We have both teams' scores, no need to continue
                    
                    # Format the score string
                    score_parts = []
                    for j in range(min(len(team_1_set_scores), len(team_2_set_scores))):
                        score_parts.append(f"{team_1_set_scores[j]}-{team_2_set_scores[j]}")
                    
                    score_string = f"{team_1_set_wins}-{team_2_set_wins} [{', '.join(score_parts)}]"
                    
                    if match_details_link and "Salt Lake" in match_details_link:
                        match_details_link = match_details_link.replace('Salt Lake', 'Salt-Lake')

                    res = requests.get("https://lovb.com" + match_details_link if match_details_link else "")
                    soup = BeautifulSoup(res.content, 'html.parser')
                    team_stats = soup.find('iframe', attrs={'class': 'mt-2xl h-[23.3125rem] w-full sm:h-[24.3125rem] xl:h-[44.1875rem]'})['src'].split('?side')[0].replace('play-by-play', 'team-stats')
                    scoreboard = soup.find('iframe', attrs={'class': 'mt-2xl h-[23.3125rem] w-full sm:h-[24.3125rem] xl:h-[44.1875rem]'})['src'].split('?side')[0].replace('play-by-play', 'scoreboard')

                    # Create match object
                    match_data = {
                        "date": date,
                        "team_1": team_1,
                        "team_2": team_2,
                        "score": score_string,
                        'team_stats': team_stats,
                        'scoreboard': scoreboard,
                        "match_url": "https://lovb.com" + match_details_link if match_details_link else ""
                    }
                    
                    all_matches.append(match_data)
                    print(f"  Match added: {match_data['team_1']} vs {match_data['team_2']}, Score: {match_data['score']}")
                
                except Exception as e:
                    print(f"  Error processing match: {e}")
        
        driver.quit()
        return all_matches


lovb = LOVB()

print(lovb.fetch_schedule())