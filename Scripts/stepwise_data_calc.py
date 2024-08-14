

import os
import pandas as pd
import IPython

def import_kinematics(file):
    #imports the kinematics portion of the hdf
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return None
    key = 'df_kinematics'
    kinematics_df = pd.read_hdf(file, key)
    return kinematics_df

def add_position_stats(step_table):

    toe_tip_x_max = []
    toe_tip_x_min = []
    toe_tip_x_end = []
    toe_tip_x_excursion = []
    toe_tip_y_max = []
    iliac_crest_y_max = []
    iliac_crest_y_min = []
    iliac_crest_y_excursion = []

    for step_i, trial in step_table.iterrows():
        h5_path = trial['source-data-h5-path']
        h5_df = import_kinematics(h5_path)

        # Get step slice
        start = trial['swing-start-idx']
        stop = trial['stance-stop-idx']
        step_slice = h5_df[start:stop]

        # Calculate x toe statistics normalized to hip x
        slice_toe_x = step_slice['ToeTip_x'] - step_slice['Hip_x']
        toe_tip_x_max.append(slice_toe_x.max())
        toe_tip_x_min.append(slice_toe_x.min())
        toe_tip_x_end.append(slice_toe_x.iloc[-1])

        # Calculate y toe & crest statistics
        toe_tip_y_max.append(step_slice['ToeTip_y'].max())
        iliac_crest_y_max.append(step_slice['IliacCrest_y'].max())
        iliac_crest_y_min.append(step_slice['IliacCrest_y'].min())

    # Assign the calculated statistics back to the DataFrame
    step_table['ToeTip-x-max'] = toe_tip_x_max
    step_table['ToeTip-x-min'] = toe_tip_x_min
    step_table['ToeTip-x-end'] = toe_tip_x_end

    step_table['ToeTip-y-max'] = toe_tip_y_max
    step_table['IliacCrest-y-max'] = iliac_crest_y_max
    step_table['IliacCrest-y-max'] = iliac_crest_y_min


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


def calc_discrete_stats(step_table):
    step_table['ToeTip-x-excursion'] = step_table['ToeTip-x-max'] - step_table['ToeTip-x-min']
    step_table['IliacCrest-y-excursion'] = step_table['IliacCrest-y-max'] - step_table['IliacCrest-y-max']
    step_table['step-duration'] = step_table['stance-stop'] - step_table['swing-start']
    step_table['cycle-velocity'] = (step_table['ToeTip-x-end'] - step_table['ToeTip-x-max']) + step_table['belt-speed'] * step_table['swing-duration'] / step_table['step-duration']
    step_table['duty-factor'] = (step_table['stance-duration']) / (step_table['step-duration'])
    step_table['stride-length'] = (step_table['ToeTip-x-end'] - step_table['ToeTip-x-min']) + step_table['belt-speed'] * step_table['swing-duration']

    return step_table

def calc_joint_angle_stats(step_table, joint_angles):
    slicing_dict = {"step-idx": ['swing-start-idx', 'stance-stop-idx'],
                    "swing-idx": ['swing-start-idx', 'swing-stop-idx'],
                    "stance-idx": ['stance-start-idx', 'stance-stop-idx'],
                    #"step-toe-touch-idx": ['stance-start-idx', 'second-swing-stop-idx'],
                    #"e1",
                    #"e2",
                    #"e3",
                    #"e4"
                    }

    error_steps = []

    for step_i, trial in step_table.iterrows():
        h5_path = trial['source-data-h5-path']
        h5_df = import_kinematics(h5_path)
        for phase in slicing_dict:
            # Get step slice
            start = trial[slicing_dict[phase][0]]
            stop = trial[slicing_dict[phase][1]]
            step_slice = h5_df[start:stop]
            trial2 = trial.copy()

            for joint in joint_angles:
                try:
                    step_table.at[step_i, f'{phase}-{joint}-min'] = min(step_slice[joint])
                    step_table.at[step_i, f'{phase}-{joint}-max'] = max(step_slice[joint])
                    step_table[ f'{phase}-{joint}-excursion'] = step_table[f'{phase}-{joint}-max'] - step_table[f'{phase}-{joint}-min']
                except ValueError:
                    if step_i not in error_steps:
                        error_steps.append(step_i)

    if error_steps != []:
        print(error_steps)
        print("confirm phase files for these step indices")

    return step_table



def main():
    #this is for testing the functions
    step_table = pd.read_csv("Sample_data/step_table.csv")
    joint_angles = ["Hip_angle", "Knee_angle", "Ankle_angle", "MTP_angle"]
    step_table_updated = calc_joint_angle_stats(step_table, joint_angles)
    print(step_table_updated.columns)
    print(step_table_updated.iloc[:15, -5:])

if __name__ == "__main__":
    main()