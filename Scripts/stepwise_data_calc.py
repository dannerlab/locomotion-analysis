
"""
has functions for adding data to step table, called by step_table_initialize
"""
import os
import pandas as pd
import IPython
import sys
from useful_imports import get_position_stats

def import_kinematics(file):
    #imports the kinematics portion of the hdf
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return None
    key = 'df_kinematics'
    kinematics_df = pd.read_hdf(file, key)
    return kinematics_df

def add_position_stats(step_table, slicing_dict):

    stats = get_position_stats()

    for step_i, step in step_table.iterrows():
        h5_path = step['source-data-h5-path']
        h5_df = import_kinematics(h5_path)

        for phase in slicing_dict:
            # Get step slice
            start = step[slicing_dict[phase][0]]
            stop = step[slicing_dict[phase][1]]
            step_slice = h5_df[start:stop]

            for stat in stats:
                try:
                    #add the columns
                    additional_cols = [f'{phase}-{stat}-min', f'{phase}-{stat}-max', f'{phase}-{stat}-end', f'{phase}-{stat}-excursion']
                    for col in additional_cols:
                        if col not in step_table.columns:
                            step_table[col] = None

                    step_table.at[step_i, f'{phase}-{stat}-min'] = min(step_slice[stat])
                    step_table.at[step_i, f'{phase}-{stat}-max'] = max(step_slice[stat])
                    step_table.at[step_i, f'{phase}-{stat}-end'] = step_slice[stat].tolist()[-1]
                    step_table[f'{phase}-{stat}-excursion'] = step_table[f'{phase}-{stat}-max'] - step_table[f'{phase}-{stat}-min']
                except ValueError:
                    print(ValueError)
                    print(f'h5 path: {h5_path}')
                    print('confirm phase files for this step index, make sure swing time is prior to stance time')
                    print('terminating from stepwise_data_calc.py')
                    exit()



    return step_table


def add_second_swing(step_table):
    #adds columns to facilitate easy selection of steps that consist of a stance phase followed by a swing phase
    #recommend using this rather than indexing through each time because it handles mouse & trial separation

    swing_cols = ['swing-start', 'swing-stop', 'swing-duration', 'swing-start-idx', 'swing-stop-idx']

    second_step_table = pd.DataFrame()
    for mouse_id in step_table['mouse-id'].unique():
        for trial in step_table['trial-number'].unique():
            mouse_id_trial_df = step_table[(step_table['mouse-id'] == mouse_id) & (step_table['trial-number'] == trial)] #selects all steps from one trial
            mouse_id_trial_df_second = mouse_id_trial_df.copy()
            for col in swing_cols:
                mouse_id_trial_df_second[f'second-{col}'] = mouse_id_trial_df[col].shift(-1) #.shift(-1) shifts the column values up by one and fills with NaN
            second_step_table = pd.concat([second_step_table, mouse_id_trial_df_second], ignore_index=True)
    return second_step_table


def calc_discrete_stats(step_table, slicing_dict):
    step_table = add_position_stats(step_table, slicing_dict)

    step_table['step-duration'] = step_table['stance-stop'] - step_table['swing-start']

    phase0 = list(slicing_dict.keys())[0]
    step_table['cycle-velocity'] = (step_table[f'{phase0}-ToeTip_x-end'] - step_table[f'{phase0}-ToeTip_x-max']) + step_table['belt-speed'] * step_table['swing-duration'] / step_table['step-duration'] #this is probably wrong
    step_table['duty-factor'] = (step_table['stance-duration']) / (step_table['step-duration'])
    step_table['stride-length'] = (step_table[f'{phase0}-ToeTip_x-end'] - step_table[f'{phase0}-ToeTip_x-min']) + step_table['belt-speed'] * step_table['swing-duration'] #probably also off

    return step_table

def calc_joint_angle_stats(step_table, joint_angles, slicing_dict):

    error_steps = []
    printed_h5_path = None
    for step_i, step in step_table.iterrows():
        h5_path = step['source-data-h5-path']
        h5_df = import_kinematics(h5_path)
        for phase in slicing_dict:
            # Get step slice
            start = step[slicing_dict[phase][0]]
            stop = step[slicing_dict[phase][1]]
            step_slice = h5_df[start:stop]
            
            for joint in joint_angles:
                try:
                    step_table.at[step_i, f'{phase}-{joint}-min'] = min(step_slice[joint])
                    step_table.at[step_i, f'{phase}-{joint}-max'] = max(step_slice[joint])
                    step_table[ f'{phase}-{joint}-excursion'] = step_table[f'{phase}-{joint}-max'] - step_table[f'{phase}-{joint}-min']
                except ValueError:
                    if step_i not in error_steps:
                        error_steps.append(step_i)
                    print(f'ValueError: {h5_path} {phase} {joint} start:{start} stop:{stop}')
                except KeyError:
                    if h5_path != printed_h5_path:
                        printed_h5_path = h5_path
                        print(f'KeyError: {joint} not found in {h5_path}, from stepwise_data_calc.py')

    if error_steps != []:
        print(error_steps)
        print("confirm phase files for these step indices")

    return step_table

def calc_segmental_stats(step_table, segment_dict, slicing_dict):
    #calculate_segmental_angles from segmental_calc must have been run on all h5s or this will not work
    for step_i, step in step_table.iterrows():
        h5_path = step['source-data-h5-path']
        h5_df = import_kinematics(h5_path)
        for phase in slicing_dict:
            # Get step slice
            start = step[slicing_dict[phase][0]]
            stop = step[slicing_dict[phase][1]]
            step_slice = h5_df[start:stop]

            for segment in segment_dict:
                step_table.at[step_i, f'{phase}-{segment}-min'] = min(step_slice[f'{segment}_angle'])
                step_table.at[step_i, f'{phase}-{segment}-max'] = max(step_slice[f'{segment}_angle'])
                step_table[ f'{phase}-{segment}-excursion'] = step_table[f'{phase}-{segment}-max'] - step_table[f'{phase}-{segment}-min']

    return step_table


def main():
    #this is for testing the functions, should be called by step_table_initialize
    #does not save anything, so test away!
    step_table = pd.read_csv("Full_data/step_table.csv")
    joint_angles = ["Hip_angle", "Knee_angle", "Ankle_angle", "MTP_angle"]
    segment_dict = {"Crest": ["IliacCrest", "Hip"],
                    "Thigh": ["Hip", "Knee"],
                    "Shank": ["Knee", "Ankle"]}
    slicing_dict = {"step": ['swing-start-idx', 'stance-stop-idx'],
                    "swing": ['swing-start-idx', 'swing-stop-idx'],
                    "stance": ['stance-start-idx', 'stance-stop-idx'],
                    #"step-toe-off-idx": ['stance-start-idx', 'second-swing-stop-idx'],
                    #"e1",
                    #"e2",
                    #"e3",
                    #"e4",
                    #hip_flexion: ['hip-flex-start-idx', 'hip-flex-stop-idx'],
                    #hip_extension: ['hip-ext-start-idx', 'hip-ext-stop-idx'],
                    }
    step_table_updated = add_position_stats(step_table, slicing_dict)
    # step_table_updated = calc_segmental_stats(step_table, segment_dict, slicing_dict)
    print(step_table_updated.columns)
    print(step_table_updated.iloc[:15, -5:])
    print(step_table_updated.shape)

if __name__ == "__main__":
    main()