"""
computes animal level averages & stdv
"""

import pandas as pd
import IPython
import numpy as np
import os
from useful_imports import get_numeric_col_names, exclude_trials

def calc_avg(step_table):
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id'])

    trial_ID_cols = ['mouse-id',
                     'mouse-type',
                     'exp-type',
                    ]
    selected_col_names = get_numeric_col_names()

    ID_df = step_table[trial_ID_cols].drop_duplicates()
    ID_df = ID_df.reset_index(drop=True) #so that when it is concatenated with avg & stdv dfs there are not issues

    avg_arr = np.full((len(step_table_grouped), len(selected_col_names)), np.NaN) #array with length = n mice and width = n stats
    stdv_arr = np.full((len(step_table_grouped), len(selected_col_names)), np.NaN) #same array but will be filled with stdv
    median_arr = np.full((len(step_table_grouped), len(selected_col_names)), np.NaN) #same array but will be filled with median

    for mouse_i, (name, mouse) in enumerate(step_table_grouped):
        for col_i, col in enumerate(selected_col_names):
            avg = np.average(mouse[col])
            stdv = np.std(mouse[col])
            median = np.median(mouse[col])
            avg_arr[mouse_i, col_i] = avg
            stdv_arr[mouse_i, col_i] = stdv
            median_arr[mouse_i, col_i] = median

    avg_selected_col_names = (f'avg-{col_name}' for col_name in selected_col_names)
    stdv_selected_col_names = (f'stdv-{col_name}' for col_name in selected_col_names)
    median_selected_col_names = (f'median-{col_name}' for col_name in selected_col_names)

    avg_df = pd.DataFrame(avg_arr, columns=avg_selected_col_names)
    stdv_df = pd.DataFrame(stdv_arr, columns=stdv_selected_col_names)
    median_df = pd.DataFrame(median_arr, columns=median_selected_col_names)
    results_df = pd.concat([ID_df, avg_df, stdv_df], axis = 1, ignore_index=False)
    return results_df

def save_results(results_df, step_table_path):
    save_dir = os.path.split(step_table_path)[0]
    save_name = os.path.join(save_dir, "animal_avg_stdv_&_median.csv")
    results_df.to_csv(save_name)
    print('saved to:', save_name)

def main(main_dir):
    print('running animal_avgs.py')
    step_table_path = f"{main_dir}/step_table.csv"
    step_table_unfiltered = pd.read_csv(step_table_path)
    step_table, excluded_trials = exclude_trials(step_table_unfiltered)
    
    results_df = calc_avg(step_table)
    save_results(results_df, step_table_path)


if __name__ == "__main__":
    main("Full_data")
