import requests
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
}

url = 'https://www.advancedeventsystems.com/api/landing/events'
res = requests.get(url).json()
df = pd.json_normalize(res['value'])
# event_data = []
# for event in res['value']:
#     event_data.append({
#         'startDate': event.get('startDate', ''),
#         'endDate': event.get('endDate', ''),
#         'eventId': event.get('eventSchedulerKey', ''),
#         'state': event.get('state', {}).get('name', ''),
#         'region': event.get('region', ''),
#         'name': event.get('name', ''),
#         'locationName': event.get('locationName', ''),
#         "eventMetaType": event.get('eventMetaType', {}).get('description'),
#         'juniors': event.get('eventMetaType', {}).get('isJunior', ''),
#         'usav': event.get('isUSAV', '')
#     })

# df = pd.DataFrame(event_data)
df = df[['eventSchedulerKey', 'eventId', 'name', 'locationName', 'region.name', 'region.code', 'startDate', 'endDate', 'eventType.eventTypeId', 'eventType.eventMetaType.isJunior', 'eventType.eventMetaType.description', 'affiliation.isUSAV', 'address.state.name', 'age.minAge', 'age.maxAge', 'genderClassTypes']]
df.to_clipboard()
print(df)

df = df[['name', 'eventId', 'startDate', 'eventSchedulerKey', 'eventType.eventMetaType.description', 'age.minAge', 'age.maxAge', 'genderClassTypes']]
df[(df['eventType.eventMetaType.description'] == 'Junior Volleyball') & (df['genderClassTypes'].astype(str).str.contains('Female')) & (df['age.minAge'] > 16)]

"""
- https://www.advancedeventsystems.com/api/landing/events
    * Events gives eventTypeId, use this id here:
- https://results.advancedeventsystems.com/event/{eventTypeId}
    * Use this endpoint to get the clubs and divisions. divisionId is needed to match fetching
- https://results.advancedeventsystems.com/api/event/{eventTypeId}/division/{divisionId}/playdays
    * Use this endpoint to get the play days by division. Play day is needed for the match fetching
- https://results.advancedeventsystems.com/api/event/{eventTypeId}/courts/{playDayId}/420
    * Use this endpoint to get the MatchId and other relevent match metadata info
- https://results.advancedeventsystems.com/api/event/{eventTypeId}/courts/match/{matchId}
    * Use this to get the scores for the match and other relevent match metadata info
    
"""