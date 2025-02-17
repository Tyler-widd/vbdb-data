import base64
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fetch_lovb import LOVB
import pandas as pd
from seleniumbase import Driver
from datetime import datetime, timedelta, date
import re
import numpy as np
from bs4 import BeautifulSoup

# Push to github
def push_to_github(commit_message, csv_filename, path):
    """
    Pushes a file to GitHub repository using GitHub API.
    
    Parameters:
    csv_filename (str): File to be pushed.
    commit_message (str): Commit message for the update.
    """
    repo_owner = 'widbuntu'
    repo_name = 'vbdb-info'
    path = path  # Path in the repository where you want to store the file
    token = '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'  # Your GitHub Personal Access Token

    with open(csv_filename, 'rb') as f:
        content = f.read()
        
     # Encode content in Base64
    encoded_content = base64.b64encode(content).decode('utf-8')
    
    # Use GitHub API to upload the file
    api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}'
    
    # Get the SHA of the file if it already exists
    response = requests.get(api_url)
    sha = response.json().get('sha', None)

    # Prepare the request data
    data = {
        'message': commit_message,
        'content': encoded_content,
    }
    
    if sha:
        data['sha'] = sha  # Add the SHA to update the existing file

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    # Make the request to the GitHub API
    response = requests.put(api_url, json=data, headers=headers)

    if response.status_code in [201, 200]:
        print("File successfully pushed to GitHub.")
    else:
        print(f"Failed to push file: {response.json()}")



def process_results(df):
    players = pd.read_csv('https://raw.githubusercontent.com/widbuntu/vbdb-info/refs/heads/main/data/mNcaaPlayers24.csv')
    teams = players[['team_name', 'team_id', 'conference_name', 'division', 'team_short', 'conference_short']].drop_duplicates()
    teams['team_id'] = teams['team_id'].astype(str)
    df = pd.merge(df, teams, on='team_id', how='left')
    
    # Convert set columns to numeric, replacing any non-numeric values with 0
    for i in range(1, 6):
        df[f'set_{i}'] = pd.to_numeric(df[f'set_{i}'], errors='coerce').fillna(0).astype(int)

    # Group the DataFrame by date and box_score_url
    grouped = df.groupby(['date', 'box_score_url'])

    # Create a new list to store the transformed data
    transformed_data = []

    for (date, url), group in grouped:  # noqa: F402
        if len(group) != 2:
            continue  # Skip if we don't have exactly two teams
        
        # Determine home and away teams (assuming the first team listed is the home team)
        home_team = group.iloc[0]
        away_team = group.iloc[1]
        
        # Create the match string
        match = f"{home_team['team']} ({home_team['conference_short']}) vs {away_team['team']} ({away_team['conference_short']})"
        
        # Calculate the score and create set scores list
        home_score = 0
        away_score = 0
        set_scores = []
        
        for i in range(1, 6):
            home_set = int(home_team[f'set_{i}'])
            away_set = int(away_team[f'set_{i}'])
            
            if home_set == 0 and away_set == 0:
                break  # Match ended before this set
            
            set_scores.append(f"{home_set}-{away_set}")
            
            if home_set > away_set:
                home_score += 1
            else:
                away_score += 1
        
        # Create the results string
        results = f"[{home_score}-{away_score}] ({', '.join(set_scores)})"
        
        transformed_data.append({
            'date': date,
            'match': match,
            'results': results,
            'box_score_url': url
        })

    # Create a new DataFrame from the transformed data
    new_df = pd.DataFrame(transformed_data)
    new_df['match'] = new_df['match'].str.replace('(nan)', '(na)')

    # Display the result
    return new_df

def fetch_results(url):
    """
    fetch_daily_results()
    -----------------------
        Fetch NCAA Womens D1 volleyball scores by a url. box_score_url might be utlized as a match_id

    Parameters
    ----------
        URL: 
            https://stats.ncaa.org/contests/livestream_scoreboards?utf8=&season_division_id=18323&game_date=09/20/2024&conference_id=0&ia=web
    
    Returns
    -------
        A pandas dataframe. 
    
    Example Data
    ------------
                +-----+---------+------------+----------------+-------+-------+-------+-------+-------+---------------------------------------------------+
                |     | team_id | date       | team           | set_1 | set_2 | set_3 | set_4 | set_5 | box_score_url                                     |
                +-----+---------+------------+----------------+-------+-------+-------+-------+-------+---------------------------------------------------+
                | 320 | 551     | 09/20/2024 | Portland       | 24    | 25    | 25    | 22    | 11    | https://stats.ncaa.org/contests/5672004/box_score |
                | 321 | 101     | 09/20/2024 | CSUN           | 26    | 23    | 17    | 25    | 15    | https://stats.ncaa.org/contests/5672004/box_score |
                | 322 | 754     | 09/20/2024 | Washington St. | 20    | 14    | 11    |       |       | https://stats.ncaa.org/contests/5671977/box_score |
                | 323 | 99      | 09/20/2024 | Long Beach St. | 25    | 25    | 25    |       |       | https://stats.ncaa.org/contests/5671977/box_score |
                | 324 | 550     | 09/20/2024 | Portland St.   | 20    | 15    | 17    |       |       | https://stats.ncaa.org/contests/5671971/box_score |

    """

    try:
        df_date_fetch = url.split('game_date=')[1].split('&')[0]
        df_date = df_date_fetch.split('/')[1] + "/" + df_date_fetch.split('/')[2] + "/" + df_date_fetch.split('/')[0] 
        df_date = df_date_fetch
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        if not soup.find_all('div', attrs={'class': 'card m-2'}):
            columns = ['team_id', 'date', 'team', 'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'box_score_url']
            df = pd.DataFrame(columns=columns)
            return df
        else:
            columns = ['team_id', 'date', 'team', 'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'box_score_url']
            df = pd.DataFrame(columns=columns)
            df_list = []
            for soup_data in soup.find_all('div', attrs={'class': 'card m-2'}):
                tt = soup_data.find('div', attrs={'class': 'table-responsive'})
                teams = tt.find('td', class_='opponents_min_width')
                top_team = re.sub(r"\s*\(\d{1,2}-\d{1,2}\)", "", teams.text.strip())
                bot_team = re.sub(r"\s*\(\d{1,2}-\d{1,2}\)", "", teams.find_next('td', class_='opponents_min_width').text.strip())
                # Initialize lists to hold scores for all matches
                team_id_list = []
                for match in tt.find_all('tr', attrs={'id': re.compile('contest')}):
                    img_tag = match.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        team_id = img_tag['src'].split('//')[2].split('.gif')[0]
                    else:
                        team_id = None 
                    team_id_list.append(team_id)
                    match_id = match['id']
                    box_score_url = f"https://stats.ncaa.org/contests/{match_id.split('_')[1]}/box_score"
                    
                    table = match.find('table', attrs={'id': re.compile('linescore')})
                    
                    if table:
                        rows = table.find_all('tr')
                        
                        top_team_scores = []
                        bot_team_scores = []
                        
                        for idx, tr in enumerate(rows):
                            scores = [td.text.strip() for td in tr.find_all('td')]
                            if idx % 2 == 0:
                                # Even index: top team scores
                                top_team_scores = scores
                            else:
                                # Odd index: bottom team scores
                                bot_team_scores = scores
                # Create a pandas DataFrame
                data = {
                    f'{top_team}': top_team_scores,
                    f'{bot_team}': bot_team_scores,
                }
                df = pd.DataFrame(data)
                df = pd.DataFrame(data).transpose()
                df.columns = [f'set {i+1}' for i in range(len(df.columns))]
                df['date'] = df_date
                df['team_id'] = team_id_list
                df['box_score_url'] = box_score_url
                df_list.append(df)
            df = pd.concat(df_list).reset_index(drop=False)
            column_rename = {
                'index': 'team',
                'team_id': 'team_id',
                'set 1': 'set_1',
                'set 2': 'set_2',
                'set 3': 'set_3',
                'set 4': 'set_4',
                'set 5': 'set_5',
                }
            df.rename(columns=column_rename, inplace=True)
            df = df.reindex(columns=['team', 'set_1', 'set_2', 'set_3', 'set_4', 'set_5', 'date', 'team_id', 'box_score_url'], fill_value=None)
            df['team_id'] = np.where(df['team_id'] == '', None, df['team_id'])
            df = df.fillna(0)
            dfs = process_results(df)

            return dfs
    except:
        pass

def format_vs_match_result(raw_text):
    lines = raw_text.split("\n")
    team1 = lines[0]
    team2 = lines[len(lines) // 2]
    team1_scores = list(map(int, lines[1:len(lines) // 2 - 1]))
    team1_sets_won = int(lines[len(lines) // 2 - 1])
    team2_scores = list(map(int, lines[len(lines) // 2 + 1:-1]))
    team2_sets_won = int(lines[-1])

    # Create the formatted score sequence
    scores = ", ".join(f"{t1}-{t2}" for t1, t2 in zip(team1_scores, team2_scores))
    match_result = f"{team1} vs {team2} [{team1_sets_won}-{team2_sets_won}] ({scores})"
    
    return match_result

def fetch_pvf_results():
    # PVF Volleystation Match ids
    schedule_url = f'https://provolleyball.com/api/schedule-events/?filter%5Bevent_state%5D=past&filter%5Bseason_id%5D=3&sort%5B0%5D=start_datetime&include%5B0%5D=firstTeam&include%5B1%5D=secondTeam&include%5B2%5D=season&include%5B3%5D=links&include%5B4%5D=links.image&include%5B5%5D=firstTeamLogo&include%5B6%5D=secondTeamLogo&include%5B7%5D=presentedByLogo&per_page=200&page=1'
    # Fetch JSON data

    res_list = []
    json_data = requests.get(schedule_url).json()
    for json in json_data['data']:
        id = json['volley_station_match_id']
        driver = Driver(browser="chrome", headless=False)
        driver.get(f'https://widgets.volleystation.com/match-result/{id}')
        data = format_vs_match_result(driver.get_text('div'))
        start_datetime = json['start_datetime'].split('T')[0]
        date_object = datetime.strptime(start_datetime, '%Y-%m-%d')
        new_date = (date_object - timedelta(days=1)).date()
        formatted_date = new_date.strftime('%m/%d/%Y')
        res_list.append({'date': formatted_date, 'match': data, 'box_score_url': f'https://widgets.volleystation.com/team-stats/{id}', 'div': 'Pro Women'})
        driver.quit()
    return res_list

def fetch_lovb_results():
    lovb = LOVB()
    match_ids = list(pd.json_normalize(lovb.fetch_schedule())['match_id'].unique())
    all_data = []  # List to collect all match results
    
    for match_id in match_ids:
        # Skip TBA matches
        if 'tba-tba' in match_id.lower():
            print(f"Skipping TBA match: {match_id}")
            continue
            
        driver = Driver(browser="chrome", headless=False)
        try:
            driver.get(match_id)
            
            try:
                driver.click("/html/body/main/div[2]/div/div[1]/div[1]/div/div/button[2]")
            except Exception as click_error:
                error_message = str(click_error)
                if "not present after 7 seconds" in error_message:
                    print(f"Click failed for match {match_id}: {error_message}")
                    driver.quit()
                    return all_data  # Stop entire function when we hit timeout error
                raise  # Re-raise any other click errors
            
            # Get Date
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            date_str = soup.find('h1').text
            cleaned_date_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)
            date_obj = datetime.strptime(cleaned_date_str, "%A, %B %d")
            date_obj = date_obj.replace(year=2025)
            formatted_date = date_obj.strftime("%m/%d/%Y")
            
            url_vs_list = []
            iframe_src = soup.find('iframe')['src']
            updated_url = iframe_src.split('?')[0].replace("play-by-play", "match-result")
            url_vs_list.append(updated_url)
            driver.quit()
            
            for url in url_vs_list:
                driver = Driver(browser="chrome", headless=False)
                driver.get(url)
                data = format_vs_match_result(driver.get_text('div'))
                print(data)
                all_data.append({'date': formatted_date, 'match': data, 'box_score_url': url.replace('match-result', 'team-stats'), 'div': 'Pro Women'})
                driver.quit()
                
        except Exception as e:
            print(f"Error processing match {match_id}: {e}")
            if driver:
                driver.quit()
            return all_data  # Return collected data on any error
    
    return all_data # Return all collected data after processing all matches

def fetch_ncaa_results(division):
    
    start_date = date(2024, 12, 15)
    end_date = date(2025, 1, 13)

    # List to hold individual dataframes for each date
    results_list = []

    # Loop through each date in the range
    current_date = start_date
    while current_date <= end_date:
        # Format the date to MM/DD/YYYY
        use_date = current_date.strftime('%m/%d/%Y')

        # Fetch the results for the current date
        if division == 'D-I':
            div_id = '18463'
        else:
            div_id = '18464'
        url = f"https://stats.ncaa.org/contests/livestream_scoreboards?utf8=&season_division_id={div_id}&game_date={use_date}"
        df = fetch_results(url)  # Fetch results for the current date

        if df is not None:
            results_list.append(df)  # Append the result to the list

        # Increment the current date by one day
        current_date += timedelta(days=1)

    # Concatenate all results into a single DataFrame
    final_results_df = pd.concat(results_list, ignore_index=True)[['date', 'match', 'results', 'box_score_url']]
    final_results_df = final_results_df[final_results_df['results'] != '[0-0] ()']
    final_results_df['div'] = division
    final_results_df['match_2'] = final_results_df['match'] + " " + final_results_df['results']
    final_results_df = final_results_df.drop(columns=['match', 'results'])
    final_results_df = final_results_df.rename(columns={'match_2': 'match'})
    final_results_df = final_results_df[['date', 'match', 'box_score_url', 'div']]
    return final_results_df

def process_and_upload():
    pvf = pd.json_normalize(fetch_pvf_results())
    lovb = pd.json_normalize(fetch_lovb_results())
    d_one = fetch_ncaa_results('D-I')
    d_three = fetch_ncaa_results('D-III')


    df = pd.concat([pvf, lovb, d_one, d_three]).reset_index(drop=True).sort_values('date')
    df = df[(df['date'] != '01/01/2025') & (df['match'] != 'Wabash (MCVL) vs Ball St. (MIVA)')]
    df = df[(df['date'] != '01/01/2025') & (df['match'] != 'Wabash (MCVL) vs Ball St. (MIVA)')]
    df = df[(df['date'] != '01/01/2025') & (df['match'] != 'Wabash (MCVL) vs Ball St. (MIVA)')]
    df = df[(df['date'] != '12/15/2024')]
    df = df[(df['date'] != '12/16/2024')]
    df = df[(df['date'] != '12/17/2024')]
    df = df[(df['date'] != '12/18/2024')]
    df = df[(df['date'] != '12/19/2024')]
    df = df[(df['date'] != '12/20/2024')]
    df = df[(df['date'] != '12/21/2024')]
    df = df[(df['date'] != '12/22/2024')]
    df = df[(df['date'] != '12/23/2024')]
    df = df[(df['date'] != '12/24/2024')]
    df = df[(df['date'] != '12/25/2024')]
    df = df[(df['date'] != '12/26/2024')]
    df = df[(df['date'] != '12/27/2024')]
    df = df[(df['date'] != '12/28/2024')]
    df = df[(df['date'] != '12/29/2024')]
    df = df[(df['date'] != '12/30/2024')]
    df = df[(df['date'] != '12/31/2024')]
    df = df.drop_duplicates()
    df.to_csv('2025.csv', index=False)
    push_to_github(f"Updated 2025 scores on {str(date.today())}", '2025.csv', 'data/2025.csv')

push_to_github(f"Updated 2025 scores on {str(date.today())}", '2025.csv', 'data/2025.csv')