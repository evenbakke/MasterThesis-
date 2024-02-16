

import requests
import pandas as pd

client_id = "aec37807-25c0-4318-b883-f18837c9b3bb"

# Define endpoint and parameters
endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources': 'SN18700,SN90450',
    'elements': 'mean(air_temperature P1D),sum(precipitation_amount P1D),mean(wind_speed P1D)',
    'referencetime': '2018-01-01/2023-12-31',
}
# Issue an HTTP GET request
r = requests.get(endpoint, parameters, auth=(client_id,''))
# Extract JSON data
json = r.json()

# Check if the request worked, print out any errors
if r.status_code == 200:
    data = json['data']
    print('Data retrieved from frost.met.no!')
else:
    print('Error! Returned status code %s' % r.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])

# Assuming 'data' is your list of dictionaries from the JSON response
rows = []  # Initialize an empty list to collect dataframes
for item in data:
    row = pd.DataFrame(item['observations'])
    row['referenceTime'] = item['referenceTime']
    row['sourceId'] = item['sourceId']
    rows.append(row)  # Append the dataframe to the list

# Concatenate all dataframes in the list into a single dataframe
df = pd.concat(rows, ignore_index=True)
