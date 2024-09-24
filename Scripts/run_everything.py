"""
runs scripts to generate:
- step_table.csv with stepwise stats
- animal_avg_&_stdv.csv with avgs and stdvs
- ANOVA_results.csv with group comparisons of the stats in animal_avg_&_stdv.csv
requires h5s with adjusted knee angles, recommend using batch_convert.py followed by locoproc 
"""

import os

#make it work on Windows & Linux
scripts_dir = os.path.join('Scripts')
batch_convert = os.path.join(scripts_dir, 'batch_convert.py')
step_table_initialize = os.path.join(scripts_dir, 'step_table_initialize.py')
animal_avgs = os.path.join(scripts_dir, 'animal_avgs.py')
group_comparison = os.path.join(scripts_dir, 'group_comparison.py')
stick_plots = os.path.join(scripts_dir, 'stick_plots.py')


os.system(f'python {step_table_initialize}')

os.system(f'python {animal_avgs}')

os.system(f'python {group_comparison}')

os.system(f'python {stick_plots}')
