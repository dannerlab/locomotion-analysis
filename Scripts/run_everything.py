"""
runs scripts to generate:
- step_table.csv with stepwise stats
- animal_avg_&_stdv.csv with avgs and stdvs
- ANOVA_results.csv with group comparisons of the stats in animal_avg_&_stdv.csv
requires h5s with adjusted knee angles, recommend using batch_convert.py followed by locoproc, see also instructions on Data Prep in the wiki
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
from useful_imports import exclude_trials, get_prelim_exclude_trials
from all_joint_angle_toe_off import main as all_joint_angle_toe_off
from mouse_joint_angles_toe_touch import main as mouse_joint_angles_toe_touch
from mouse_joint_angles_toe_off import main as mouse_joint_angles_toe_off
import pandas as pd

###########################################################################
#fill out these variables here
main_dir = 'Full_data'
groups = ['WT_Levelwalk', 'V3Off_Levelwalk', 'WT_Incline', 'V3Off_Incline']
###########################################################################

prelim_excluded = get_prelim_exclude_trials() #####this does not exclude them, just shows which are being excluded by default
if prelim_excluded != []:
    print(f'excluding trials: {prelim_excluded}')

print()
step_table_initialize_main(main_dir, groups)
    #prints h5 save directories, then saves step_table.csv to main_dir
    #also runs segmental_calc which adds segmental stats to the h5 files directly
print()

step_table_df = pd.read_csv(f"{main_dir}/step_table.csv")
step_table_df, excluded_trials = exclude_trials(step_table_df)
print(f'excluded trials: {excluded_trials}')

#basic viewing of data
stick_plots_main(main_dir)
    #saves stick_plots to main_dir/stick_diagrams; prints names of each trial
print()

#calculate averages and stdvs for specified stats
animal_avgs_main(main_dir)
    #saves animal_avg_&_stdv.csv to main_dir
print()


paired_groups = [
                 [('WT', 'Levelwalk'), ('V3Off', 'Levelwalk')],
                 [('WT', 'Incline'), ('V3Off', 'Incline')]
                 ]
for pair in paired_groups:
    print(f'processing: {pair}')

    #calculate & graph boxplots for comparison between groups in the pair
    # group_comparison_main(main_dir, pair)
    #     #prints 'saved to: maindir\group_results' twice, saves ANOVA_results.csv, non_normal_stats.csv, normal_stats.csv & animal versions to group_results
    # print()

    # avg_group_compare_graphs_main(main_dir, pair)
    #     #saves graphs to main_dir/group_results/avg_graphs
    # print()

    #graph each group and a summary comparison
    all_joint_angle_toe_touch(main_dir, pair)
        #saves graphs to main_dir/angle_graphs/toe_touch_aligned
    print()

    all_joint_angle_toe_off(main_dir, pair)
        #saves graphs to main_dir/angle_graphs/toe_off_aligned
    print()


mouse_joint_angles_toe_touch(main_dir)
    #saves graphs to main_dir/angle_graphs/toe_touch_aligned/group_dir
print()

mouse_joint_angles_toe_off(main_dir)
    #saves graphs to main_dir/angle_graphs/toe_off_aligned/group_dir
print()

stop_time = time.time()

print(f"total time {main_dir}: {stop_time - start_time} seconds")
