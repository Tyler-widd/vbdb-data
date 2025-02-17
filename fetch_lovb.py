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
        unwanted_terms = ["Founding Athlete", "NEW"]

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

                all_rows = []

                # Loop through each table
                for table in tables:
                    headers = [header.text.strip() for header in table.find_all('th')]

                    rows = []

                    # Extract data from each row in the table
                    for row in table.find_all('tr')[1:]:  # Skip the header row
                        columns = row.find_all('td')

                        if columns:
                            row_data = {}

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
                            row_data['url'] = url

                            # For each other column, map it to the corresponding header
                            for header, column in zip(headers[1:], columns[1:]):
                                column_text = column.get_text(strip=True)
                                row_data[header] = column_text

                            # Add the row's dictionary to the rows list
                            rows.append(row_data)

                    # Append the rows of this table to the all_rows list
                    all_rows.extend(rows)

                # Append the all rows of this URL to all_data
                all_data.extend(all_rows)

            except Exception as e:
                print(f"Error processing {url}: {e}")

        # Close the driver after scraping is complete
        driver.quit()

        df = pd.DataFrame(all_data)
        df['Position'] = np.where(df['Position'].isna(), df['Title'], df['Position'])
        df['Player Number'] = df['Player Number']
        df['Player Number'] = np.where(df['Player Number'] == '', 'Staff', df['Player Number'])
        df['Team Name'] = np.where(df['url'].str.contains('atlanta'), 'Atlanta',
                                   np.where(df['url'].str.contains('salt'), 'Salt Lake',
                                            np.where(df['url'].str.contains('austin'), 'Austin',
                                                     np.where(df['url'].str.contains('houston'), 'Houston',
                                                              np.where(df['url'].str.contains('madison'), 'Madison',
                                                                       np.where(df['url'].str.contains('omaha'), 'Omaha', None))))))
        df.drop(columns=['Title', 'Follow', 'url'], inplace=True)

        return df

    # Method to fetch and process schedule
    def fetch_schedule(self):
        """
        Fetches teams the LOVB site.

        Example
        -------
            >>> lovb = LOVB()
            >>> teams = lovb.fetch_schedule()
            >>> len(teams)
            42

        Returns
        -------
        **list[dict]**: A list of schedule entries.
        """

        # Get teams first to use to get other stuff
        # Fetch teams and create a DataFrame
        teams = self.fetch_teams()
        df_teams = pd.DataFrame(teams)

        # Target URL
        url = "https://www.lovb.com/schedule"

        # Fetch the page
        response = requests.get(url)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all divs with the specific class
        days = soup.find_all('div', attrs={"day-schedule"})

        schedule = []

        for i, day in enumerate(days):
            try:
                # Match ID
                match_div = day.find('div', attrs={'xl:ml-auto'})
                match_id = (
                    "https://www.lovb.com" + match_div.find('a')['href']
                    if match_div and match_div.find('a') else None
                )
                if match_id:
                    match_id = match_id.replace("Salt Lake", "Salt-Lake")

                # Input date
                date_element = day.find('p', attrs={'class': 'hidden lg:block'})
                input_date = date_element.text if date_element else None
                cleaned_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', input_date) if input_date else None
                cleaned_date_with_year = f"{cleaned_date}, 2025" if cleaned_date else None

                # Parse date
                if cleaned_date_with_year:
                    try:
                        if "•" in cleaned_date:
                            match = re.search(r'(\w+, \w+ \d+).*?(\d{4})', cleaned_date_with_year)
                            new_date = f"{match.group(1)}, {match.group(2)}"
                            parsed_date = datetime.strptime(new_date, "%A, %B %d, %Y")
                        else:
                            parsed_date = datetime.strptime(cleaned_date_with_year, "%A, %B %d, %Y")
                        date = parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        date = None
                else:
                    date = None

                # Location
                location_element = day.find('p', attrs={'class': 'flex items-center text-card-headline-s'})
                location = location_element.text.strip() if location_element else None

                # Teams
                teams = day.find_all('div', attrs={'class': 'text-pretty'})
                if len(teams) >= 2:
                    home_team_name = teams[2].text.strip()
                    away_team_name = teams[0].text.strip()
                    home_team_id = (
                        df_teams.loc[df_teams['name'] == home_team_name, 'team_id'].values[0]
                        if not df_teams.loc[df_teams['name'] == home_team_name].empty else None
                    )
                    away_team_id = (
                        df_teams.loc[df_teams['name'] == away_team_name, 'team_id'].values[0]
                        if not df_teams.loc[df_teams['name'] == away_team_name].empty else None
                    )
                else:
                    home_team_name = away_team_name = None
                    home_team_id = away_team_id = None

                # Venue
                venue_element = day.find('a', attrs={'class': 'text-card-headline-s link-hover link'})
                venue = venue_element.text.strip() if venue_element else None

                # Other fields (set to None by default)
                title = None
                status = None
                volley_station_match_id = None
                home_team_img = None
                home_team_score = None
                home_team_color = None
                away_team_img = None
                away_team_score = None
                away_team_color = None

                # Add match entry to schedule
                match_entry = {
                    "match_id": match_id,
                    "title": title,
                    "date": date,
                    "location": location,
                    "status": status,
                    "volley_station_match_id": volley_station_match_id,
                    "home_team_id": home_team_id,
                    "home_team_name": home_team_name,
                    "home_team_img": home_team_img,
                    "home_team_score": home_team_score,
                    "home_team_color": home_team_color,
                    "away_team_id": away_team_id,
                    "away_team_name": away_team_name,
                    "away_team_img": away_team_img,
                    "away_team_score": away_team_score,
                    "away_team_color": away_team_color,
                    "venue": venue
                }

                schedule.append(match_entry)
            except Exception as e:
                print(f"Error processing day {i + 1}: {e}")
                continue
        return schedule
