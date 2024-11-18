"""
runs scripts to generate:
- step_table.csv with stepwise stats
- animal_avg_&_stdv.csv with avgs and stdvs
- ANOVA_results.csv with group comparisons of the stats in animal_avg_&_stdv.csv
requires h5s with adjusted knee angles, recommend using batch_convert.py followed by locoproc
"""
print('importing...')

import time
start_time = time.time()

from step_table_initialize import main as step_table_initialize_main
from animal_avgs import main as animal_avgs_main
from group_comparison import main as group_comparison_main  
from stick_plots import main as stick_plots_main
from avg_group_compare_graphs import main as avg_group_compare_graphs_main
from all_joint_angle_toe_touch import main as all_joint_angle_toe_touch

main_dir = 'Full_data'

print()
step_table_initialize_main(main_dir)
    #prints h5 save directories, then saves step_table.csv to main_dir
    #also runs segmental_calc which adds segmental stats to the h5 files directly
print()

animal_avgs_main(main_dir)
    #saves animal_avg_&_stdv.csv to main_dir
print()

group_comparison_main(main_dir)
    #prints 'saved to: maindir\group_results' twice, saves ANOVA_results.csv, non_normal_stats.csv, normal_stats.csv & animal versions to group_results
print()

stick_plots_main(main_dir)
    #saves stick_plots to main_dir/stick_diagrams; prints names of each trial
print()

avg_group_compare_graphs_main(main_dir)
    #saves graphs to main_dir/group_results/avg_graphs
print()

all_joint_angle_toe_touch(main_dir)
    #saves graphs to main_dir/angle_graphs/toe_touch_aligned
print()

stop_time = time.time()

print(f"total time {main_dir}: {stop_time - start_time} seconds")
