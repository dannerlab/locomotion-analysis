"""
Take existing data files (csv/phase, h5) and make one large table
with trialwise & step data
also add discrete stats for x and y positions
"""
import os, warnings
import glob
import pandas as pd
import numpy as np
from stepwise_data_calc import calc_discrete_stats, add_second_swing, calc_joint_angle_stats, calc_segmental_stats
from segmental_calc import calculate_segmental_angles
from useful_imports import import_kinematics, get_prelim_exclude_trials
from calculate_hip_to_toe import calculate_hip_to_toe_x
import IPython

#suppress PerformanceWarning so it stops warning about fragmented DataFrame
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)
#Helper functions

def closest(lst, num):
    lst = np.asarray(lst)
    idx = (np.abs(lst - num)).argmin()
    return lst[idx]

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

    all_phase_paths_unfiltered = []
    for dir in phase_dirs:
        phase_paths = glob.glob(os.path.join(dir, '*'))
        all_phase_paths_unfiltered += phase_paths

    all_h5_paths_unfiltered = []
    for dir in h5_dirs:
        h5_paths = glob.glob(os.path.join(dir, '*'))
        all_h5_paths_unfiltered += h5_paths

    all_h5_paths_unfiltered.sort()
    all_phase_paths_unfiltered.sort()

    excluded_h5_paths = get_prelim_exclude_trials()
    excluded_phase_paths = [h5_path.replace('.h5', '.phase').replace('h5_knee_fixed', 'phase') for h5_path in excluded_h5_paths]
    all_h5_paths = [path for path in all_h5_paths_unfiltered if path not in excluded_h5_paths]
    all_phase_paths = [path for path in all_phase_paths_unfiltered if path not in excluded_phase_paths]

    return all_phase_paths, all_h5_paths

def get_trial_data(h5_path, belt_speed):
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
                'belt-speed' : belt_speed
    }
    return(trial_data)

def get_step_data(h5_path, phase_path, trial_data):
    '''get timing and corresponding indices per phase'''
    #this processes one trial
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
    #specify the columns that should be in the dataframe so they show up in a meaningful order. Each row is one stepcycle.
    empty_list = [None] * len(step_indices)
    cycle_df = pd.DataFrame({'mouse-id': empty_list, #from trial
            'mouse-type': empty_list,
            'exp-type': empty_list,
            'trial-number': empty_list,
            'side': empty_list,
            'source-data-h5-path': empty_list,
            'source-data-phase-path': empty_list,
            'step-number': step_indices, #from phase
            'swing-start': swing_starts,
            'swing-stop': swing_stops,
            'stance-start': stance_starts,
            'stance-stop': stance_stops,
            'stance-duration': empty_list,
            'swing-duration': empty_list,
            #'include-stance': empty_list, #user-defined, from phase
            #'include-swing': empty_list,
            'swing-start-idx': empty_list, #from h5 matching
            'swing-stop-idx': empty_list,
            'stance-start-idx': empty_list,
            'stance-stop-idx': empty_list,})


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

    cycle_df['swing-start-idx'] = swing_start_indices
    cycle_df['swing-stop-idx'] = swing_stop_indices
    cycle_df['stance-start-idx'] = stance_start_indices
    cycle_df['stance-stop-idx'] = stance_stop_indices


    return cycle_df


def step_table_initialize(h5_dirs):

    phase_paths, h5_paths = get_paths(h5_dirs)

    belt_speed = 15 #cm/s
    joint_angles = ["Hip_angle", "Knee_angle", "Ankle_angle", "MTP_angle"]
    segment_dict = {"Crest": ["IliacCrest", "Hip"],
                    "Thigh": ["Hip", "Knee"],
                    "Shank": ["Knee", "Ankle"]}
    slicing_dict = {"step": ['swing-start-idx', 'stance-stop-idx'], #step will be default as long as it is in position 0
                    "swing": ['swing-start-idx', 'swing-stop-idx'],
                    "stance": ['stance-start-idx', 'stance-stop-idx'],
                    #"step-toe-touch-idx": ['stance-start-idx', 'second-swing-stop-idx'],
                    #"f": ['swing-start-idx', 'peak-swing-idx'],
                    #"e1": ['peak-swing-idx', 'stance-start-idx'],
                    #"e2": ['stance-start-idx', 'trough-stance-idx'],
                    #"e3": ['trough-stance-idx', 'stance-stop-idx'],
                    }


    step_dfs_by_trial = []
    trial_table = pd.DataFrame()
    
    for h5_path, phase_path in zip(h5_paths, phase_paths): # for each trial
        trialname_h5 = os.path.splitext(os.path.split(h5_path)[1])[0]
        trailname_phase = os.path.splitext(os.path.split(phase_path)[1])[0]
        if trialname_h5 == trailname_phase:
            #basic set-up
            h5_with_stats_path = calculate_segmental_angles(h5_path, segment_dict)
            calculate_hip_to_toe_x(h5_with_stats_path)
            trial_data = get_trial_data(h5_with_stats_path, belt_speed)
            trial_table = get_step_data(h5_with_stats_path, phase_path, trial_data) #will require update once we add ankle phases
            trial_table = add_second_swing(trial_table)

            #additional calculations
            trial_table = calc_discrete_stats(trial_table, slicing_dict)
            trial_table = calc_joint_angle_stats(trial_table, joint_angles, slicing_dict)
            trial_table = calc_segmental_stats(trial_table, segment_dict, slicing_dict)
            step_dfs_by_trial.append(trial_table)

        else:
            print(f'file mismatch: \nh5: {trialname_h5}, phase: {trailname_phase}')
            print('skipping')
    
    step_table = pd.concat((step_dfs_by_trial), ignore_index = True)

    return step_table

def main(main_dir, groups):
    print('running step_table_initialize.py')
    #input

    h5_dirs = [os.path.join(main_dir, group, 'h5_knee_fixed') for group in groups]
    
    #run code
    step_table = step_table_initialize(h5_dirs)

    #save
    save_dir = os.path.split(os.path.split(h5_dirs[0])[0])[0]
    save_name = os.path.join(save_dir, 'step_table.csv')
    step_table.to_csv(save_name)
    print(f"saved to: {save_name}")


if __name__ == "__main__":
    groups = ['WT_Levelwalk', 'V3Off_Levelwalk', 'WT_Incline', 'V3Off_Incline']
    main("Full_data", groups)