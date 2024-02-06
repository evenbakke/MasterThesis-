#System load (production and demand)

import pandas as pd
import matplotlib.pyplot as plt

#Data Taken from: https://www.statnett.no/for-aktorer-i-kraftbransjen/tall-og-data-fra-kraftsystemet/#produksjon-og-forbruk
load_2018 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2018.xls')
load_2019 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2019.xls')
load_2020 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2020.xls')
load_2021 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2021.xls')
load_2022 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2022.xls')
load_2023 = pd.read_excel('/Users/mathiassperre/Desktop/System Load (production Demand)/ProductionConsumption-2023.xls')

# Concatenate the dataframes
combined_load = pd.concat([load_2018, load_2019, load_2020, load_2021, load_2022, load_2023])
#removing Timezone +01
combined_load['Time(Local)'] = pd.to_datetime(combined_load['Time(Local)'], format='%d.%m.%Y %H:%M:%S %z')

# Now remove the timezone information correctly
combined_load['Time(Local)'] = combined_load['Time(Local)'].apply(lambda x: x.replace(tzinfo=None))
combined_load.to_excel("load_combined.xlsx")


# Plotting "Production" and "Consumption" over time
plt.figure(figsize=(15, 7))  # Set the figure size for better readability
plt.plot(combined_load['Time(Local)'], combined_load['Production'], label='Production', color='blue')
plt.plot(combined_load['Time(Local)'], combined_load['Consumption'], label='Consumption', color='red')
plt.title('Production and Consumption over Time')
plt.xlabel('Time')
plt.ylabel('MW')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()  # Adjust the layout to make room for the rotated date labels
plt.show()



