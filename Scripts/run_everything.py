"""
runs scripts to generate:
- step_table.csv with stepwise stats
- animal_avg_&_stdv.csv with avgs and stdvs
- ANOVA_results.csv with group comparisons of the stats in animal_avg_&_stdv.csv
requires h5s with adjusted knee angles, recommend using batch_convert.py followed by locoproc
"""

import time
from step_table_initialize import main as step_table_initialize_main
from animal_avgs import main as animal_avgs_main
from group_comparison import main as group_comparison_main  
from stick_plots import main as stick_plots_main
from avg_group_compare_graphs import main as avg_group_compare_graphs_main

main_dir = 'Sample_data'

start_time = time.time()
step_table_initialize_main(main_dir)
    #prints h5 save directories, then saves step_table.csv to main_dir
animal_avgs_main(main_dir)
    #saves animal_avg_&_stdv.csv to main_dir
group_comparison_main(main_dir)
    #prints 'saved to: maindir\group_results' twice, saves ANOVA_results.csv, non_normal_stats.csv, normal_stats.csv & animal versions to group_results
stick_plots_main(main_dir)
    #saves stick_plots to main_dir/stick_diagrams; prints names of each trial
avg_group_compare_graphs_main(main_dir)
    #saves graphs to main_dir/group_results/avg_graphs
stop_time = time.time()

print(f"total time {main_dir}: {stop_time - start_time} seconds")
