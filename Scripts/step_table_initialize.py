"""
Take existing data files (csv/phase, h5) and make one large table
with trialwise & step data
also add discrete stats for x and y positions
"""
import os, glob
import pandas as pd
import numpy as np
import IPython
from stepwise_data_calc import add_discrete_stats

#Helper functions

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


def get_paths(h5_dirs):
    phase_dirs = []
    for dir in h5_dirs:
        base_dir = os.path.split(dir)[0]
        phase_dir = os.path.join(base_dir, 'phase')
        phase_dirs.append(phase_dir)
    for dir in phase_dirs:
        if not os.path.exists(dir):
            print(f'directory does not exist: {dir}')

    all_phase_paths = []
    for dir in phase_dirs:
        phase_paths = glob.glob(os.path.join(dir, '*'))
        all_phase_paths += phase_paths

    all_h5_paths = []
    for dir in h5_dirs:
        h5_paths = glob.glob(os.path.join(dir, '*'))
        all_h5_paths += h5_paths

    all_h5_paths.sort()
    all_phase_paths.sort()

    return all_phase_paths, all_h5_paths

def get_trial_data(h5_path):
    id_trial = os.path.splitext(os.path.basename(h5_path).split('/')[-1])[0]
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


    trial_dir = os.path.split(os.path.split(h5_path)[0])[0]
    mouse_exp = os.path.basename(trial_dir).split("_")
    mouse_type = mouse_exp[0]
    exp_type = mouse_exp[1]
    working_dir = os.getcwd()
    source_data_h5_path = os.path.join(working_dir, h5_path)
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

def get_step_data(h5_path, phase_path, trial_data):
    #this processes one trial
    #get timing and corresponding indices per phase
    phase_df = pd.read_csv(phase_path)
    step_indices = []
    swing_starts = []
    swing_stops = []
    stance_starts = []
    stance_stops = []


    for step_i in range(len(phase_df.iloc[:-1])):
        swing_starts.append(phase_df['swing'][step_i])
        swing_stops.append(phase_df['stance'][step_i])
        stance_starts.append(phase_df['stance'][step_i])
        stance_stops.append(phase_df['swing'][step_i + 1])
        step_indices.append(step_i)

    #create dataframe
    cycle_df = pd.DataFrame({'step-number': step_indices,
                'swing-start': swing_starts,
                'swing-stop': swing_stops,
                'stance-start': stance_starts,
                'stance-stop': stance_stops,})

    cycle_df['stance-duration'] = cycle_df['stance-stop'] - cycle_df['stance-start']
    cycle_df['swing-duration'] = cycle_df['swing-stop'] - cycle_df['swing-start']

    #append trial data to cycle_df
    for key in trial_data.keys():
        cycle_df[key] = trial_data[key]


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

    return stepwise_table


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

def step_table_initialize(h5_dirs):

    phase_paths, h5_paths = get_paths(h5_dirs)

    step_dfs_by_trial = []
    for h5_path, phase_path in zip(h5_paths, phase_paths):
        trialname_h5 = os.path.splitext(os.path.split(h5_path)[1])[0]
        trailname_phase = os.path.splitext(os.path.split(phase_path)[1])[0]
        if trialname_h5 == trailname_phase:
            trial_data = get_trial_data(h5_path)
            step_table_no_second_swing = get_step_data(h5_path, phase_path, trial_data)
            step_table = add_second_swing(step_table_no_second_swing)
            step_table = add_discrete_stats(step_table)
            step_dfs_by_trial.append(step_table)
        else:
            print(f'file mismatch: \nh5: {trialname_h5}, phase: {trailname_phase}')
    step_table = pd.concat((step_dfs_by_trial), ignore_index = True)

    return step_table

def main():
    #input
    h5_dirs = ['Sample_data/V3Off_Levelwalk/h5',
               'Sample_data/WT_Levelwalk/h5',]
    #run code
    step_table = step_table_initialize(h5_dirs)

    #save
    save_dir = os.path.split(os.path.split(h5_dirs[0])[0])[0]
    step_table.to_csv(os.path.join(save_dir, 'step_table.csv'))


if __name__ == "__main__":
    main()