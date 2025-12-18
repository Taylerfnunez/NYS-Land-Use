# Economics

import pandas as pd
import matplotlib.pyplot as plt

s1_path_2030 = 'NYS-Land-Use/output/202512092100-PG-2030-B/s1/results/costs.csv'
s2_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s2/results/costs.csv'
s3_path = 'NYS-Land-Use/output/202512092100-PG-2030-B/s3/results/costs.csv'
s1_path_2040 = 'NYS-Land-Use/output/202512092232-PG-2040-B/s1/results/costs.csv'
s4_path = 'NYS-Land-Use/output/202512092232-PG-2040-B/s4/results/costs.csv'
s5_path = 'NYS-Land-Use/output/202512092232-PG-2040-B/s5/results/costs.csv'
s6_path = 'NYS-Land-Use/output/202512092232-PG-2040-B/s6/results/costs.csv'
s7_path = 'NYS-Land-Use/output/202512092232-PG-2040-B/s7/results/costs.csv'

pathnames = [s1_path_2030, s2_path, s3_path, s1_path_2040, s4_path, s5_path, s6_path, s7_path]
scenario_names = ['s1 2030', 's2', 's3', 's1 2040', 's4', 's5', 's6', 's7']

def load_data(pathname):
    df = pd.read_csv(pathname)

def economic_comparison(data):
    total_cost = data.loc[1, "Total"]
    return total_cost

for i in range(len(pathnames)):
    df = pd.read_csv(pathnames[i])
    cost = economic_comparison(df)
    print (cost)

plt.figure(figsize=(10,6))
plt.bar(scenario_names, [economic_comparison(pd.read_csv(p)) for p in pathnames], color='green')
plt.ylabel("Total System Cost ($)")
plt.xlabel("Scenario")
plt.title("Total System Cost by Scenario")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
save_path = "NYS-Land-Use/Land Analysis/Economics Figures/Total_cost_by_scenario.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()



