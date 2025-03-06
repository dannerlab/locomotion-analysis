"""
graphs each mouse all steps within window -.15s to .25s aligned at toe touch
"""

#graphs joint angles for window around toe touch: -0.15, + 0.25 seconds
#based on graphs from Han Zhang 2020 thesis work Figure 3.2c

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, IPython
from useful_imports import get_joints_and_segments, get_rc_params, exclude_trials, import_kinematics, get_sampling_freq, get_color

def get_mouse_window_array(mouse_data, joint_or_seg):
    """
    for each mouse, create an array of windows around toe touch
    0.15 seconds before toe off, 0.25 seconds after toe off
    returns array of windows (includes all trials of that mouse)
    """
    #mouse_data is step_table portion corresponding to one mouse, may contain multiple trials
    mouse_data_trial_grouped = mouse_data.groupby('trial-number')
    windows_arrays_dict = {} #key: trial_id, value: array of windows for that trial
    n_trials = len(mouse_data_trial_grouped)
    #sanity check
    h5_fps = mouse_data['source-data-h5-path'].unique()
    if n_trials != len(h5_fps):
        IPython.embed()
        fklsjd
    # actual stuff
    for trial_id, trial_data in mouse_data_trial_grouped: #trial numbers may not start from 0
        h5_fp = trial_data['source-data-h5-path'].iloc[0]
        h5_df = import_kinematics(h5_fp)
        toe_touch_idx = trial_data['swing-stop-idx'][:-1] #exclude last step because no toe off 
        if joint_or_seg not in h5_df.columns: #some trials are missing joint values, this replaces those with a Nan array
            windows_array = np.full((len(toe_touch_idx), int(0.4 * get_sampling_freq())), np.nan)
        else:
            windows_array = np.ones((len(toe_touch_idx), int(0.4 * get_sampling_freq()))) #0.4 seconds total window length
            h5_segment = h5_df[joint_or_seg]
            for toe_touch_i, toe_touch in enumerate(toe_touch_idx):
                window_start_idx = int(toe_touch - 0.15 * get_sampling_freq()) #0.15 seconds before toe off; could throw error if sampling frequency not /100
                window_stop_idx = int(toe_touch + 0.25 * get_sampling_freq()) #0.25 seconds after toe off
                if window_start_idx < 0: #if window goes before start of recording
                    nan_pad = np.full(window_start_idx * -1, np.nan)
                    window_vals = h5_segment[:window_stop_idx]
                    window = np.concatenate((nan_pad, window_vals))
                elif window_stop_idx > len(h5_segment): #if window goes past end of recording
                    nan_pad = np.full(window_stop_idx - len(h5_segment), np.nan)
                    window_vals = h5_segment[window_start_idx:]
                    window = np.concatenate((window_vals, nan_pad))
                else:
                    window = h5_segment[window_start_idx:window_stop_idx]
                try:
                    windows_array[toe_touch_i] = window ######################issues with shape
                except ValueError:
                    print(toe_touch_i)
                    IPython.embed()
                    gfkdsl
        windows_arrays_dict[trial_id] = windows_array
    windows_array_all_trials = np.concatenate(list(windows_arrays_dict.values()), axis=0)
    avg_window = np.nanmean(windows_array_all_trials, axis=0)
    stdv_window = np.nanstd(windows_array_all_trials, axis=0)

    return windows_array_all_trials, avg_window, stdv_window

def graph_mouse(group_name, mouse_id, joint_or_seg, windows_array_all_trials, avg_window, stdv_window, super_save_directory):
    """
    graphs each mouse all steps within window -.15s to .25s aligned at toe touch, saves
    """
    fig, ax = plt.subplots()
    xaxistime = np.linspace(-0.15, 0.25, int(0.4 * get_sampling_freq()))
    color = get_color(group_name)

    #plot
    for step in windows_array_all_trials:
        ax.plot(xaxistime, step, color = 'black', alpha = 0.25)
    ax.plot(xaxistime, avg_window, color = color, linewidth = 2)
    plt.fill_between(xaxistime, avg_window - stdv_window, avg_window + stdv_window, color = color, alpha = 0.2)
    ax.axvline(0, color = 'black', linestyle = '--')

    #labels, format
    ax.set_title(f'{joint_or_seg} for {group_name}_{mouse_id}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(f'{joint_or_seg} (degrees)')
    ax.set_xlim(-0.15, 0.25)

    #save
    save_path = f'{super_save_directory}/{mouse_id}_{joint_or_seg}.png'
    if not os.path.exists(f'{super_save_directory}'):
        os.makedirs(f'{super_save_directory}', exist_ok = True)
    plt.savefig(save_path)
    plt.close

    return

def main(main_dir, selected_groups):
    #set up statistics names & rc params
    joints_and_segments = get_joints_and_segments()
    joint_seg_names = [None] * len(joints_and_segments)
    for idx, joint_or_seg in enumerate(joints_and_segments):
        joint_seg_names[idx] = f'{joint_or_seg}_angle'
    rc_params = get_rc_params()
    plt.rcParams.update(rc_params)

    ##directories
    step_table_unfiltered_extraidx = pd.read_csv(f'{main_dir}/step_table.csv')
    step_table_unfiltered = step_table_unfiltered_extraidx.drop(columns='Unnamed: 0') #remove extra index column
    step_table, excluded_trials = exclude_trials(step_table_unfiltered) #excluded_trials can be printed to see which are being excluded
    step_table_grouped_all_groups = step_table.groupby(['mouse-type', 'exp-type'])
    
    if selected_groups != step_table_grouped_all_groups.groups.keys():
        step_table_selected = [step_table_grouped_all_groups.get_group(group) for group in selected_groups]
    step_table_grouped = pd.concat(step_table_selected).groupby(['mouse-type', 'exp-type'])
    save_directory = f'{main_dir}/angle_graphs/toe_off_aligned'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory, exist_ok = True)

    #actually make the graphs
    for joint_or_seg in joint_seg_names:
        for group, group_data in step_table_grouped: #should run twice, each group on own axes
            group_name = '_'.join(group) #should be something like WT_Levelwalk
            super_save_directory = f'{main_dir}/angle_graphs/toe_touch_aligned_window/{group_name}'
            step_table_by_mouse = group_data.groupby('mouse-id') #get mouse-wise data
            for mouse_id, mouse_data in step_table_by_mouse:
                windows_array_all_trials, avg_window, stdv_window = get_mouse_window_array(mouse_data, joint_or_seg)
                #plot
                graph_mouse(group_name, mouse_id, joint_or_seg, windows_array_all_trials, avg_window, stdv_window, super_save_directory)
            print(f'saved to: {super_save_directory}')

if __name__ == "__main__":
    selected_groups = [('WT', 'Incline'), ('V3Off', 'Incline')]############edit to change groups, can only be 2
    main('Full_data', selected_groups)