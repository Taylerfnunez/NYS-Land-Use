import pandas as pd
import matplotlib.pyplot as plt

file_path =  '/Users/tedwhite15/Documents/Taylers_Files/Research/Projects/Land-use/AVLU_project/NYS-Land-Use/input/GenX_results/20250611_test/emissions.csv'
df = pd.read_csv(file_path)

# Remove the 'AnnualSum' row if present
df = df[df['Zone'] != 'AnnualSum']

# Set the time index
df = df.set_index('Zone')

# Convert all other columns to numeric
df = df.apply(pd.to_numeric)

# --- Plot 1: Power by zone over time ---
plt.figure(figsize=(12,6))
for col in df.columns[:-1]:  # skip 'Total' if present
   plt.plot(df.index, df[col], label=f'Zone {col}')
plt.xlabel("Time")
plt.ylabel("Emissions (MW)")
plt.xticks(df.index[::24])
plt.title("Emission by Zone Over Time")
plt.legend()
plt.show()

# --- Plot 2: Total power over time ---
# If your CSV already has a 'Total' column, you can use it. Otherwise sum across zones
df['Total_Power'] = df[df.columns[:-1]].sum(axis=1)  # sum over zones
plt.figure(figsize=(12,6))
plt.plot(df.index, df['Total_Power'], color='black')
plt.xlabel("Time")
plt.ylabel("Total Power (MW)")
plt.title("Total Power Over Time (All Zones)")
plt.show()