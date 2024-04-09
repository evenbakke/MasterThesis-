

import requests
import pandas as pd
import geopandas as gpd
from pyproj import Transformer
import json
import matplotlib.pyplot as plt

#Bidding zones NO1 Hentet fra NVE: https://temakart.nve.no/link/?link=vannkraft
shapefile_path = "C:\\Users\\mathi\\Downloads\\NO4\\Polyline.shp"
gdf = gpd.read_file(shapefile_path)
# Convert the GeoDataFrame to GeoJSON
geojson = gdf.to_json()

print(geojson)

# Initialize transformer to convert from ETRS89 / UTM zone 33N (EPSG:25833) to WGS 84 (EPSG:4326)
transformer = Transformer.from_crs("epsg:25833", "epsg:4326", always_xy=True)


# NO AREA UTM coordinates
utm_coordinates = [[299892.78071289486, 7265572.045042808], [410975.66954533925, 7583919.348404082], [760480.3685547373, 7896847.974261333], [967744.7830835665, 7964581.443061604], [1127595.7694522059, 7888719.958005301], [1054443.6231479133, 7722095.624756634], [988064.8237236477, 7826405.1667090515], [902720.6530353063, 7640815.462196309], [750997.6829226994, 7697711.575988537], [595210.7046820762, 7550052.614003946], [513930.54212175106, 7348206.876979139], [447551.74269748555, 7101657.0505461525], [302602.1194649057, 7265572.045042808]
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

#The code belows takes in the result from their website from POLYGON, and loads it in as json. From here, ID and Name is extracted. The ids are then split into chunks of
# lists with 25 values, to then be parsed one at a time to METs API. We then transform datacolumn into datetime and sorts the df before saving it to a csv

# Path to the file
file_path = "C:\\Users\\mathi\\OneDrive\\Dokumenter\\Skole\Master Thesis\\FROST MET API\\NO5 Måler TemperaturFrostAPI.txt"

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
df_sensors.info()


#Extracting IDs
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

#-------------------------------------
#GETTING DATA

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

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
print(df_final.tail(25))
df_final.info()


df_final['referenceTime'] = pd.to_datetime(df_final['referenceTime'])
df_final_sorted = df_final.sort_values(by="referenceTime")
df_final_sorted.to_csv("NO5Temp.csv")
df_final.tail(25)


#plotting and computing mean values for every Bidding Zone.

no1 = pd.read_csv('C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\\MasterThesis-\\FROST MET API\\NO1Temp.csv')
no2 = pd.read_csv('C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\\MasterThesis-\\FROST MET API\\NO2Temp.csv')
no3 = pd.read_csv('C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\\MasterThesis-\\FROST MET API\\NO3Temp.csv')
no4 = pd.read_csv('C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\\MasterThesis-\\FROST MET API\\NO4Temp.csv')
no5 = pd.read_csv('C:\\Users\\mathi\\OneDrive\\Dokumenter\\GitHub\\MasterThesis-\\FROST MET API\\NO5Temp.csv')

no1["sourceId"].nunique() #200 unique stations
no2["sourceId"].nunique() #200 Unique stations
no3["sourceId"].nunique() #194 Unique stations
no4["sourceId"].nunique() #207 unique stations
no5["sourceId"].nunique() #107 unique stations



dfs = [no1,no2,no3,no4,no5]
for df in dfs:
    df['referenceTime'] = pd.to_datetime(df['referenceTime'])
    df.sort_values(by='referenceTime')

#this needs to be manually changed from no1 to no5
no5['referenceTime'] = pd.to_datetime(no5['referenceTime'])

# Group by the date part of 'referenceTime' and calculate the mean of 'value'
no5_daily_mean = no5.groupby(no5['referenceTime'].dt.date)['value'].mean().reset_index()

# Convert 'referenceTime' back to datetime format if necessary
no5_daily_mean['referenceTime'] = pd.to_datetime(no5_daily_mean['referenceTime'])


dfs = [no1_daily_mean, no2_daily_mean, no3_daily_mean, no4_daily_mean,no5_daily_mean]
fig, axs = plt.subplots(5, 1, figsize=(10, 12))  # 5 rows, 1 column

# Titles for each subplot (optional)
titles = ['NO1', 'NO2', 'NO3', 'NO4', 'NO5'  ]

for ax, df, title in zip(axs, dfs, titles):
    ax.plot(df['referenceTime'], df['value'], marker='', linestyle='solid')
    ax.set_title(title)
    ax.set_xlabel('Year')
    ax.set_ylabel('Temperature Degc')
    ax.grid(True)
    ax.tick_params(axis='x', labelrotation=45)

plt.tight_layout()  # Adjust layout to make room for labels
plt.show()

