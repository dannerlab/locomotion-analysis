"""
re-runs all scripts to generate:
- step_table.csv with stepwise stats
- animal_avg_&_stdv.csv with avgs and stdvs
- ANOVA_results.csv with group comparisons of the stats in animal_avg_&_stdv.csv
"""

import os

os.system('python Scripts/step_table_initialize.py')

os.system('python Scripts/animal_avgs.py')

os.system('python Scripts/group_comparison.py')