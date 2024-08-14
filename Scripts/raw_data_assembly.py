
"""
This file creates the step_table.csv file that contains links to source data phase & h5 files
This enables easy access to all trials within an experimental group
Saves files in directory 2 above the h5 file of the first h5 directory provided
Should run after batch_convert & phase_step_select have been run and then columns in generated phase files have been edited for true/false includes

h5 files should be named: mouse-type_exp-type/mouse-id_side_trial-number where side is left or right, and may be excluded

current run time is around 40 seconds on my laptop

"""

import glob, os
import pandas as pd
import numpy as np
import IPython, time

def import_kinematics(file):
    #imports the kinematics portion of the hdf
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return None
    key = 'df_kinematics'
    kinematics_df = pd.read_hdf(file, key)
    return kinematics_df


def closest(list, num):
    list = np.asarray(list)
    idx = (np.abs(list - num)).argmin()
    return list[idx]


def get_swing_stance(stepcycle_df, h5_df):
    steps = []
    for idx in range(len(stepcycle_df)):
        step = h5_df.loc[stepcycle_df.loc[idx, 'swing-start-idx'] : stepcycle_df.loc[idx, 'stance-stop-idx']].copy()
        step['abs_toe_touch_idx'] = stepcycle_df.loc[idx, 'stance-start-idx'] #abs_toe_touch_idx is the index where toe touch occurs
        step['abs_toe_touch_time'] = stepcycle_df.loc[idx, 'stance-start'] #abs_toe_touch_time is the time where toe touch occurs
        steps.append(step)
    return steps


def get_stance_swing(stepcycle_df, h5_df):
    steps = []
    for idx in range(len(stepcycle_df)):
        step = h5_df.loc[stepcycle_df.loc[idx, 'stance-start-idx'] : stepcycle_df.loc[idx, 'second-swing-stop-idx']].copy()
        step['abs_toe_off_idx'] = stepcycle_df.loc[idx, 'stance-stop-idx'] #abs_toe_touch_idx is the index where toe off occurs
        step['abs_toe_off_time'] = stepcycle_df.loc[idx, 'stance-stop'] #abs_toe_touch_time is the time where toe off occurs
        steps.append(step)
    return steps


def get_trial_data(path):
    id_trial = os.path.splitext(os.path.basename(path).split('/')[-1])[0]
    mouse_id = id_trial.split("_")[0]
    if (len(id_trial.split("_")) == 3):
        trial_number = id_trial.split("_")[2]
        side = id_trial.split("_")[1]
    elif (len(id_trial.split("_"))==2):
        side = 'NA'
        trial_number = id_trial.split("_")[1]
    else:
        side = 'NA'
        trial_number = ''
        print(id_trial)


    trial_dir = os.path.split(os.path.split(path)[0])[0]
    mouse_exp = os.path.basename(trial_dir).split("_")
    mouse_type = mouse_exp[0]
    exp_type = mouse_exp[1]
    working_dir = os.getcwd()
    source_data_h5_path = os.path.join(working_dir, path)
    source_data_h5_path = source_data_h5_path.replace('\\', '/')
    source_data_phase_path = os.path.join(working_dir, trial_dir, 'phase', f'{id_trial}.phase')

    phase_df = pd.read_csv(source_data_phase_path)

    trial_data = {
                'mouse-id': mouse_id,
                'mouse-type': mouse_type,
                'exp-type': exp_type,
                'trial-number': trial_number,
                'side': side,
                'source-data-h5-path': source_data_h5_path,
                'source-data-phase-path': source_data_phase_path,
                #'h5-df': h5_df,
                #'phase-df': phase_df
    }
    return(trial_data)


def get_trial_table(h5_dirs):
    all_h5_paths = []
    for dir in h5_dirs:
        h5_paths = glob.glob(os.path.join(dir, '*'))
        all_h5_paths += h5_paths

    #columns = ['mouse-id', 'mouse-type', 'exp-type', 'trial-number', 'side', 'source-data-h5-path', 'source-data-phase-path']
    #directory_df = pd.DataFrame(columns=columns)

    for path in all_h5_paths:
        trial_data = get_trial_data(path)
        directory_df = directory_df._append(trial_data, ignore_index = True)

    return directory_df


def get_indices(h5_df, cycle_df, cycle_key):
    num_steps = len(cycle_df)
    times = []
    indices = []
    for step_i in range(num_steps):
        time = closest(h5_df['time'], cycle_df[cycle_key][step_i])
        times.append(time)
        for segment in range(len(h5_df)):
            if times[step_i] == h5_df["time"][segment]:
                indices.append(segment)
                break #stop after first match
    return indices

def add_discrete_stats(step_table, key):

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
        h5_df = pd.read_hdf(h5_path, key)

        # Get step slice
        start = trial['swing-start-idx']
        stop = trial['stance-stop-idx']
        step_slice = h5_df[start:stop]

        # Calculate x toe statistics normalized to hip x
        slice_toe_x = step_slice['ToeTip_x'] - step_slice['Hip_x']
        toe_tip_x_max.append(slice_toe_x.max())
        toe_tip_x_min.append(slice_toe_x.min())
        toe_tip_x_end.append(slice_toe_x.iloc[-1])
        toe_tip_x_excursion.append(slice_toe_x.max() - slice_toe_x.min())

        # Calculate y toe & crest statistics
        toe_tip_y_max.append(step_slice['ToeTip_y'].max())
        iliac_crest_y_max.append(step_slice['IliacCrest_y'].max())
        iliac_crest_y_min.append(step_slice['IliacCrest_y'].min())
        iliac_crest_y_excursion.append(step_slice['IliacCrest_y'].max() - step_slice['IliacCrest_y'].min())

    # Assign the calculated statistics back to the DataFrame
    step_table['ToeTip_x_max'] = toe_tip_x_max
    step_table['ToeTip_x_min'] = toe_tip_x_min
    step_table['ToeTip_x_end'] = toe_tip_x_end
    step_table['ToeTip_x_excursion'] = toe_tip_x_excursion
    step_table['ToeTip_y_max'] = toe_tip_y_max
    step_table['IliacCrest_y_max'] = iliac_crest_y_max
    step_table['IliacCrest_y_min'] = iliac_crest_y_min
    step_table['IliacCrest_y_excursion'] = iliac_crest_y_excursion

    return step_table

def get_step_data(h5_path, phase_path):
    #gets stepcyclewise data for each trial
    trial_data = pd.DataFrame(get_trial_data(h5_path), index = [0]) # retrieves trial data: mouse-id, mouse-type, exp-type, trial-number, side, source-data-h5-path, source-data-phase-path

    #retrieve data that comes from phase file
    phase_df = pd.read_csv(phase_path)

    step_indices = []
    swing_starts = []
    swing_stops = []
    stance_starts = []
    stance_stops = []
    incl_swing = []
    incl_stance = []

    for step_i in range(len(phase_df.iloc[:-1])):
        swing_starts.append(phase_df['swing'][step_i])
        swing_stops.append(phase_df['stance'][step_i])
        stance_starts.append(phase_df['stance'][step_i])
        stance_stops.append(phase_df['swing'][step_i + 1])
        incl_swing.append(phase_df['include-swing'][step_i])
        incl_stance.append(phase_df['include-stance'][step_i])
        step_indices.append(step_i)

    cycle_df = pd.DataFrame({'step-number': step_indices,
                'swing-start': swing_starts,
                'swing-stop': swing_stops,
                'stance-start': stance_starts,
                'stance-stop': stance_stops,
                'include-swing': incl_swing,
                'include-stance': incl_stance})
    cycle_df['stance-duration'] = cycle_df['stance-stop'] - cycle_df['stance-start']
    cycle_df['swing-duration'] = cycle_df['swing-stop'] - cycle_df['swing-start']

    #append trial data to cycle_df
    for key in trial_data.keys():
        cycle_df[key] = trial_data[key][0]


    #retrieve indices from h5
    h5_df = import_kinematics(h5_path)

    swing_start_indices = get_indices(h5_df, cycle_df, 'swing-start')
    swing_stop_indices = get_indices(h5_df, cycle_df, 'swing-stop')
    stance_start_indices = get_indices(h5_df, cycle_df, 'stance-start')
    stance_stop_indices = get_indices(h5_df, cycle_df, 'stance-stop')

    indices = pd.DataFrame({'swing-start-idx': swing_start_indices,
               'swing-stop-idx': swing_stop_indices,
               'stance-start-idx': stance_start_indices,
               'stance-stop-idx': stance_stop_indices
    })

    #combine step data from phase with indices corresponding to h5
    stepwise_table = pd.concat((cycle_df, indices), axis = 1)

    #add columns for second swing to allow slicing for stance then swing steps (toe off alignment)
    step_table = add_second_swing(stepwise_table)

    #add x and y stats
    key = 'df_kinematics'
    step_table = add_discrete_stats(step_table, key)

    return step_table


def analysis_table(h5_dirs):

    #get the phase directories
    phase_dirs = []
    for dir in h5_dirs:
        base_dir = os.path.split(dir)[0]
        phase_dir = os.path.join(base_dir, 'phase')
        phase_dirs.append(phase_dir)
    for dir in phase_dirs:
        if not os.path.exists(dir):
            print(f'directory does not exist: {dir}')

    all_h5_paths = []
    for dir in h5_dirs:
        h5_paths = glob.glob(os.path.join(dir, '*'))
        all_h5_paths += h5_paths

    all_phase_paths = []
    for dir in phase_dirs:
        phase_paths = glob.glob(os.path.join(dir, '*'))
        all_phase_paths += phase_paths


    #specify the columns that should be in the dataframe. Each row is one stepcycle.
    columns = ['mouse-id', #from trial
            'mouse-type',
            'exp-type',
            'trial-number',
            'side',
            'source-data-h5-path',
            'source-data-phase-path',
            'step-number', #from phase
            'swing-start',
            'swing-stop',
            'stance-start',
            'stance-stop',
            'stance-duration',
            'swing-duration',
            'include-stance', #user-defined, from phase
            'include-swing',
            'swing-start-idx', #from h5 matching
            'swing-stop-idx',
            'stance-start-idx',
            'stance-stop-idx']

    columns_df = pd.DataFrame(columns = columns)

    all_h5_paths.sort()
    all_phase_paths.sort()
    list_of_step_dfs = [columns_df]

    for h5_path, phase_path in zip(all_h5_paths, all_phase_paths):
        trialname_h5 = os.path.splitext(os.path.split(h5_path)[1])[0]
        trailname_phase = os.path.splitext(os.path.split(phase_path)[1])[0]
        if trialname_h5 == trailname_phase:
            stepwise_table = get_step_data(h5_path, phase_path)
            list_of_step_dfs.append(stepwise_table)
        else:
            print(f'file mismatch: \nh5: {trialname_h5}, phase: {trailname_phase}')

    step_cycle_df = pd.concat((list_of_step_dfs), ignore_index = True)

    return step_cycle_df


def add_second_swing(step_table):
    #adds columns to facilitate easy selection of steps that consist of a stance phase followed by a swing phase
    #recommend using this rather than indexing through each time because it handles mouse & trial separation

    swing_cols = ['swing-start', 'swing-stop', 'swing-duration', 'include-swing', 'swing-start-idx', 'swing-stop-idx']

    second_step_table = pd.DataFrame()
    for mouse_id in step_table['mouse-id'].unique():
        for trial in step_table['trial-number'].unique():
            mouse_id_trial_df = step_table[(step_table['mouse-id'] == mouse_id) & (step_table['trial-number'] == trial)] #selects all steps from one trial
            mouse_id_trial_df_second = mouse_id_trial_df.copy()
            for col in swing_cols:
                mouse_id_trial_df_second[f'second-{col}'] = mouse_id_trial_df[col].shift(-1) #.shift(-1) shifts the column values up by one and fills with NaN
            second_step_table = pd.concat([second_step_table, mouse_id_trial_df_second], ignore_index=True)
    return second_step_table


def main():
    start_time = time.time()
    #which groups to analyze
    h5_dirs = ['Sample_data/V3Off_Levelwalk/h5',
               'Sample_data/WT_Levelwalk/h5',]

    save_dir = os.path.split(os.path.split(h5_dirs[0])[0])[0]

    step_table = analysis_table(h5_dirs)
    step_table.to_csv(os.path.join(save_dir, 'step_table.csv'))

    end_time = time.time()
    print(f'RUN TIME : {end_time-start_time}')


if __name__ == '__main__':
    main()
