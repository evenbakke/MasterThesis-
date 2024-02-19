

import requests
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
import json
import matplotlib

#Bidding zones NO1 Hentet fra NVE: https://temakart.nve.no/link/?link=vannkraft
shapefile_path = "C:\\Users\\mathi\\Downloads\\Export\\Polyline.shp"
gdf = gpd.read_file(shapefile_path)
# Convert the GeoDataFrame to GeoJSON
geojson = gdf.to_json()

print(geojson)

# Initialize transformer to convert from ETRS89 / UTM zone 33N (EPSG:25833) to WGS 84 (EPSG:4326)
transformer = Transformer.from_crs("epsg:25833", "epsg:4326", always_xy=True)

#UTM coordinates
utm_coordinates = [
    [352047.55168910336, 6962126.10481759],
    [345274.20480907627, 6643101.466768313],
    [308698.13165692997, 6530663.908559863],
    [251802.01786470236, 6534727.91668788],
    [241641.99754466172, 6626845.434256248],
    [198292.57751248832, 6595010.703920121],
    [167135.18186436367, 6673581.527728436],
    [219289.9528405723, 6708802.9315045765],
    [136655.12090424175, 6828013.836593053],
    [236223.32004064004, 6874749.93006524],
    [353402.2210651088, 6962803.439505592],
    [352724.8863771061, 6961448.770129587]
]

# Convert each coordinate to WGS 84 and format as POLYGON string
wkt_polygon = "POLYGON(("
for coord in utm_coordinates:
    lon, lat = transformer.transform(coord[0], coord[1])
    wkt_polygon += f"{lon} {lat}, "

# Remove the last comma and space, then close the parentheses
wkt_polygon = wkt_polygon.rstrip(", ") + "))"

print(wkt_polygon)
#we use the code above to take the area of each bidding zones from NVE, then we transform it into langitude and longitude to use on the online website of the Frost API.
# There we can insert the Polygon() command to extract all measuring systems within this geographical area. Below we will extract the IDs and Names of all the listed measuring points.
#and put them into the api to collect data.



# Path to the file
file_path = 'C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\MasterThesis-\\NO1 Måler Temperatur FrostAPI.txt'

# Load JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the 'data' part which contains sensor systems information
sensor_data = data['data']
# Create a list of dictionaries with 'id' and 'name' for each sensor system
sensors_list = [{'id': sensor['id'], 'name': sensor['name']} for sensor in sensor_data]
# Create a DataFrame
df_sensors = pd.DataFrame(sensors_list)
# Display the first few rows to ensure it's been created correctly
df_sensors.head()






file_path = 'C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\MasterThesis-\\NO1 Måler Temperatur FrostAPI.txt'

# Read the file
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize an empty list for storing IDs
ids = []

# Loop through each item in the data
for item in data['data']:
    # Extract the 'id' and add it to the list
    ids.append(item['id'])
    # Print the 'id' and 'name' for confirmation (optional)
    print(f"ID: {item['id']}, Name: {item['name']}")

# Print the list of IDs (optional)
print("List of IDs:", ids)


#Getting the Data
client_id = "aec37807-25c0-4318-b883-f18837c9b3bb"

# Define endpoint and parameters
endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources' :'SN23670, SN12590, SN26640, SN18269, SN18700, SN19660, SN18260',
    'elements': 'mean(air_temperature P1D)',
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
df.info()



#-------------------------------------

#FUNKER

# Load and parse the JSON data to get IDs
file_path = 'C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\MasterThesis-\\NO1 Måler Temperatur FrostAPI.txt'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract IDs
ids

# Function to split the sensor_ids list into chunks of a given size
def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Split the ids into chunks, 25 each time
id_chunks = list(chunk_list(ids, 25))

# Your Frost API credentials
client_id = "aec37807-25c0-4318-b883-f18837c9b3bb"
auth = (client_id, '') 

# Define the base endpoint
endpoint = 'https://frost.met.no/observations/v0.jsonld'

# Initialize an empty list to collect dataframes
rows = []

# Process each chunk of IDs
for chunk in id_chunks:
    parameters = {
        'sources': ','.join(chunk),
        'elements': 'mean(air_temperature P1D)',
        'referencetime': '2018-01-01/2023-12-31',
    }

    # Make the API request
    response = requests.get(endpoint, params=parameters, auth=auth)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()['data']
        print('Data retrieved from frost.met.no!')

        # Process each item in the response
        for item in data:
            row = pd.DataFrame(item['observations'])
            row['referenceTime'] = item['referenceTime']
            row['sourceId'] = item['sourceId']
            rows.append(row)  # Append the DataFrame to the list
    else:
        print(f"Error! Returned status code {response.status_code}")
        if 'error' in response.json():
            error_message = response.json()['error']
            print(f"Message: {error_message.get('message')}")
            print(f"Reason: {error_message.get('reason')}")

# Concatenate all DataFrames in the list into a single DataFrame
df_final = pd.concat(rows, ignore_index=True)

# Display the final DataFrame
print(df_final.head(25))
df_final.info()


df_final['referenceTime'] = pd.to_datetime(df_final['referenceTime'])

# Then, group by 'referenceTime' and calculate the mean temperature for each group
mean_temperature_over_time = df_final.groupby('referenceTime')['value'].mean()

# The result is a Series with the mean temperature for each time point
# To work with this as a DataFrame, you can reset the index
mean_temperature_df = mean_temperature_over_time.reset_index()

# Rename columns for clarity
mean_temperature_df.columns = ['Reference Time', 'Mean Temperature']

# Now, mean_temperature_df contains the average temperature for the entire area over time
#df_final.to_excel("NO1.xlsx")

