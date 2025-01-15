"""
plots continuous stats: joint angle, segment angle
aligned at toe off
per mouse (each line is a step, each trial gets a color if you want, and avg line is avg of all steps)
"""

import os
from useful_imports import *
import pandas as pd
import matplotlib.pyplot as plt
import IPython
import numpy as np
from all_joint_angle_toe_off import get_steps, get_stances, get_swings

rc_params = get_rc_params()
plt.rcParams.update(rc_params)

def get_max_lengths(trial_grouped):
    all_stances_len = []
    all_swings_len = []
    max_stances = []
    max_swings = []
    for trial_id, trial_data in trial_grouped:
        h5_df = import_kinematics(trial_data['source-data-h5-path'].iloc[0])
        stances = get_stances(trial_data, h5_df)
        all_stances_len.append([len(stance) for stance in stances])
        swings = get_swings(trial_data, h5_df)
        all_swings_len.append([len(swing) for swing in swings])
        max_stance = max(len(stance) for stance in stances)
        max_stances.append(max_stance)
        max_swing = max(len(swing) for swing in swings)
        max_swings.append(max_swing)
    max_stance_len = max(max_stances)
    max_swing_len = max(max_swings)

    return max_stance_len, max_swing_len, all_stances_len, all_swings_len

def get_max_toe_off(trial_grouped):
    toe_lifts = [] #filled with toe off idx for each step in each trial
    for trial_id, trial in trial_grouped:
        h5_df = import_kinematics(trial['source-data-h5-path'].iloc[0])
        h5_df['abs-idx'] = range(len(h5_df))
        steps = get_steps(trial, h5_df)
        for step in steps:
            abs_toe_off = step['abs-toe-off-idx'].iloc[0]
            rel_toe_off = abs_toe_off - step['abs-idx'].iloc[0]
            toe_lifts.append(rel_toe_off)
    max_toe_off = max(toe_lifts)
    return max_toe_off
        

def get_stepwise_stats(mouse_id, mouse_data, stat):
    """calculates the average line for a group of trials"""
 
    trial_grouped = mouse_data.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])
    max_stance_len, max_swing_len, stance_lens, swing_lens = get_max_lengths(trial_grouped)
    max_step_combined_len = max_stance_len + max_swing_len - 1 #subtract 1 because toe off is included in swing
    max_toe_off = get_max_toe_off(trial_grouped) #max toe off across all trials
    
    ntrials = len(trial_grouped)
    steps_arr = np.nan*np.ones((len(mouse_data) - 1*ntrials, max_step_combined_len))
    abs_step_i = 0
    for trial_i, (trial_id, trial_data) in enumerate(trial_grouped):
        h5_df = import_kinematics(trial_data['source-data-h5-path'].iloc[0])
        #print(trial_data['source-data-h5-path'].iloc[0])
        #print(h5_df.shape)
        h5_df['abs-idx'] = range(len(h5_df))
        steps_list = get_steps(trial_data, h5_df) #simply called steps in other scripts, here called steps_list to differentiate from steps_arr

        for step_i, step in enumerate(steps_list):
            #print(f'step_i: {step_i}, trial_i: {trial_i}, abs_step_i: {abs_step_i}')
            step['toe-off-adjusted-idx'] = step['abs-idx'] - step['abs-toe-off-idx']

            stance_pad = np.nan*(np.ones(max_stance_len - stance_lens[trial_i][step_i]))
            swing_pad = np.nan*(np.ones(max_swing_len - swing_lens[trial_i][step_i]))
            padded_step = list(swing_pad) + list(step[stat]) + list(stance_pad)

            if len(padded_step) != steps_arr.shape[1]:
                raise ValueError(f"Length of padded_step ({len(padded_step)}) does not match the number of columns in steps_arr ({steps_arr.shape[1]})")
            steps_arr[abs_step_i] = padded_step 
            abs_step_i += 1 #need to have this so that it doesn't overwrite previous steps instead of adding to them
            
            #printing statements for figuring out if we are zeroing correctly
            # print(f'max_stance_len: {max_stance_len}')
            # print(f'max_swing_len: {max_swing_len}')
            # print(f'max_toe_off: {max_toe_off}')
            # print(f'max_step_combined_len: {max_step_combined_len}') 
            # print(f'swing_len: {swing_lens[trial_i][step_i]}')
            # print(f'swing_pad: {len(swing_pad)}')
            # print(f'stance_len: {stance_lens[trial_i][step_i]}')
            # print(f'stance_pad: {len(stance_pad)}')
            # print(f'step_len: {len(step[stat])}')
            # print(f'padded_step: {len(padded_step)}')
            # print(f'toe_off_step: {step['abs-toe-off-idx'].iloc[0] - step['abs-idx'].iloc[0]}')
            # print()
    avg_line = np.mean(steps_arr, axis=0)
    stdv_line = np.std(steps_arr, axis=0)

        
    return steps_arr, avg_line, stdv_line, max_toe_off, max_step_combined_len

def graph_stats(mouse_id, mouse_data, steps_arr, avg_line, stdv_line, stat, max_toe_off, max_length, main_dir, trial_colors = False):
    """graphs the average line for the mouse; also graphs individual steps for all trials; each trial is a color if you want"""

    #get colors for trial
    trial_grouped = mouse_data.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])
    if trial_colors:
        colors = plt.cm.viridis(np.linspace(0, 1, len(trial_grouped))) #ncolors = ntrials
    else:
        colors = ['black']*len(trial_grouped) #if not coloring by trial, all lines are black

    #get x-axis for trial
    sampling_freq = get_sampling_freq()
    max_toe_off_time = max_toe_off/sampling_freq
    time_vec = np.linspace(0.0, (max_length - 1)/sampling_freq, max_length) - max_toe_off_time

    #plot steps
    abs_step_i = 0
    labels = []
    for trial_i, (trial_id, trial_data) in enumerate(trial_grouped):
        for step_i, step in trial_data[:-1].iterrows():
            label = f'trial_{trial_id[3]}'
            if label not in labels:
                labels.append(label)
                plt.plot(time_vec, steps_arr[abs_step_i], color= colors[trial_i], alpha=0.5, label = label)
            else:
                plt.plot(time_vec, steps_arr[abs_step_i], color= colors[trial_i], alpha=0.5)
            abs_step_i += 1
    
    #plot toe off & avg step
    plt.plot(time_vec, avg_line, color='black', linewidth=2, label='average')
    upper = avg_line + stdv_line
    lower = avg_line - stdv_line
    plt.fill_between(time_vec, lower, upper, color = 'black', alpha = 0.2)
    plt.axvline(time_vec[max_toe_off], color = 'black', linestyle = '--')
    
    if trial_colors:
        plt.legend()
    plt.ylabel(stat)
    plt.ylim([0, 180])
    plt.yticks(np.arange(0, 181, 30))
    if stat in ['Shank_angle', 'Crest_angle']:
        plt.ylim([-30, 150])
        plt.yticks(np.arange(-30, 151, 30))
    plt.xlabel('time (s)')
    mouse_group = '_'.join(mouse_id[0:2])
    save_folder = os.path.join(main_dir, 'angle_graphs', 'toe_off_aligned', mouse_group)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_name = f'{'_'.join(mouse_id)}_{stat}_aligned_at_toe_off.png'
    plt.savefig(os.path.join(save_folder, save_name))
    #plt.show()
    plt.clf()

    return save_folder

def main(main_dir):
    """creates continuous stats for joint & sement angles aligned at toe off and toe off"""
    step_table_unfiltered = pd.read_csv(os.path.join(main_dir, 'step_table.csv'))
    step_table, dropped_trials = exclude_trials(step_table_unfiltered)
    stats = get_continuous_stats()
    rc_params = get_rc_params()
    plt.rcParams.update(rc_params)

    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id'])
    save_folders = []
    for mouse_id, mouse_data in step_table_grouped:
        printed_errors = []
        for stat in stats:
                try:
                    mouse_steps_arr, mouse_avg_line, mouse_stdv, max_toe_off, max_length = get_stepwise_stats(mouse_id, mouse_data, stat)
                    save_folder = graph_stats(mouse_id, mouse_data, mouse_steps_arr, mouse_avg_line, mouse_stdv, stat, max_toe_off, max_length, main_dir, True)
                    if save_folder not in save_folders:
                        save_folders.append(save_folder)
                except KeyError:
                    if (mouse_id, stat) not in printed_errors:
                        printed_errors.append((mouse_id, stat))
                        print(f'KeyError: {mouse_id} {stat}')
    print(f'saved_to: {save_folders}')
    
    return

if __name__ == '__main__':
    main('Full_data')