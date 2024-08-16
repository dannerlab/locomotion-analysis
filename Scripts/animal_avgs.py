"""
computes animal level averages & stdv
"""

import pandas as pd
import IPython
import numpy as np
import os

def calc_avg(step_table):
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id'])
    selected_col_names = ['stance-duration',
                 'swing-duration',
                 "second-swing-duration",
                 "step-ToeTip_x-min",
                 "step-ToeTip_x-max",
                 "step-ToeTip_x-end",
                 "step-ToeTip_x-excursion",
                 "step-ToeTip_y-min",
                 "step-ToeTip_y-max",
                 "step-ToeTip_y-end",
                 "step-ToeTip_y-excursion",
                 "step-IliacCrest_y-min",
                 "step-IliacCrest_y-max",
                 "step-IliacCrest_y-end",
                 "step-IliacCrest_y-excursion",
                 "swing-ToeTip_x-min",
                 "swing-ToeTip_x-max",
                 "swing-ToeTip_x-end",
                 "swing-ToeTip_x-excursion",
                 "swing-ToeTip_y-min",
                 "swing-ToeTip_y-max",
                 "swing-ToeTip_y-end",
                 "swing-ToeTip_y-excursion",
                 "swing-IliacCrest_y-min",
                 "swing-IliacCrest_y-max",
                 "swing-IliacCrest_y-end",
                 "swing-IliacCrest_y-excursion",
                 "stance-ToeTip_x-min",
                 "stance-ToeTip_x-max",
                 "stance-ToeTip_x-end",
                 "stance-ToeTip_x-excursion",
                 "stance-ToeTip_y-min",
                 "stance-ToeTip_y-max",
                 "stance-ToeTip_y-end",
                 "stance-ToeTip_y-excursion",
                 "stance-IliacCrest_y-min",
                 "stance-IliacCrest_y-max",
                 "stance-IliacCrest_y-end",
                 "stance-IliacCrest_y-excursion",
                 "step-duration",
                 "cycle-velocity",
                 "duty-factor",
                 "stride-length",
                 "step-Hip_angle-min",
                 "step-Hip_angle-max",
                 "step-Hip_angle-excursion",
                 "step-Knee_angle-min",
                 "step-Knee_angle-max",
                 "step-Knee_angle-excursion",
                 "step-Ankle_angle-min",
                 "step-Ankle_angle-max",
                 "step-Ankle_angle-excursion",
                 "step-MTP_angle-min",
                 "step-MTP_angle-max",
                 "step-MTP_angle-excursion",
                 "swing-Hip_angle-min",
                 "swing-Hip_angle-max",
                 "swing-Hip_angle-excursion",
                 "swing-Knee_angle-min",
                 "swing-Knee_angle-max",
                 "swing-Knee_angle-excursion",
                 "swing-Ankle_angle-min",
                 "swing-Ankle_angle-max",
                 "swing-Ankle_angle-excursion",
                 "swing-MTP_angle-min",
                 "swing-MTP_angle-max",
                 "swing-MTP_angle-excursion",
                 "stance-Hip_angle-min",
                 "stance-Hip_angle-max",
                 "stance-Hip_angle-excursion",
                 "stance-Knee_angle-min",
                 "stance-Knee_angle-max",
                 "stance-Knee_angle-excursion",
                 "stance-Ankle_angle-min",
                 "stance-Ankle_angle-max",
                 "stance-Ankle_angle-excursion",
                 "stance-MTP_angle-min",
                 "stance-MTP_angle-max",
                 "stance-MTP_angle-excursion",
                 "step-Crest-min",
                 "step-Crest-max",
                 "step-Crest-excursion",
                 "step-Thigh-min",
                 "step-Thigh-max",
                 "step-Thigh-excursion",
                 "step-Shank-min",
                 "step-Shank-max",
                 "step-Shank-excursion",
                 "swing-Crest-min",
                 "swing-Crest-max",
                 "swing-Crest-excursion",
                 "swing-Thigh-min",
                 "swing-Thigh-max",
                 "swing-Thigh-excursion",
                 "swing-Shank-min",
                 "swing-Shank-max",
                 "swing-Shank-excursion",
                 "stance-Crest-min",
                 "stance-Crest-max",
                 "stance-Crest-excursion",
                 "stance-Thigh-min",
                 "stance-Thigh-max",
                 "stance-Thigh-excursion",
                 "stance-Shank-min",
                 "stance-Shank-max",
                 "stance-Shank-excursion"]
    trial_ID_cols = ['mouse-id',
                              'mouse-type',
                              'exp-type',
                              ]

    ID_df = step_table[trial_ID_cols].drop_duplicates()
    ID_df = ID_df.reset_index(drop=True) #so that when it is concatenated with avg & stdv dfs there are not issues

    avg_arr = np.full((len(step_table_grouped), len(selected_col_names)), np.NaN) #array with length = n mice and width = n stats
    stdv_arr = avg_arr #same array but will be filled with stdv

    for mouse_i, (name, mouse) in enumerate(step_table_grouped):
        for col_i, col in enumerate(selected_col_names):
            avg = np.average(mouse[col])
            stdv = np.std(mouse[col])
            avg_arr[mouse_i, col_i] = avg
            stdv_arr[mouse_i, col_i] = stdv

    avg_selected_col_names = (f'avg-{col_name}' for col_name in selected_col_names)
    stdv_selected_col_names = (f'stdv-{col_name}' for col_name in selected_col_names)

    avg_df = pd.DataFrame(avg_arr, columns=avg_selected_col_names)
    stdv_df = pd.DataFrame(avg_arr, columns=stdv_selected_col_names)
    results_df = pd.concat([ID_df, avg_df, stdv_df], axis = 1, ignore_index=False)
    return results_df

def save_results(results_df, step_table_path):
    save_dir = os.path.split(step_table_path)[0]
    save_name = os.path.join(save_dir, "animal_avg_&_stdv.csv")
    results_df.to_csv(save_name)
    print(f"saved to: {save_name}")



def main():
    step_table_path = "Sample_data/step_table.csv"
    step_table = pd.read_csv(step_table_path)

    results_df = calc_avg(step_table)
    save_results(results_df, step_table_path)


if __name__ == "__main__":
    main()
