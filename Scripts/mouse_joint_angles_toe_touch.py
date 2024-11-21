"""
plots continuous stats: joint angle, segment angle
aligned at toe touch
aligned at toe off
per mouse (each line is a step, each trial gets a color if you want, and avg line is avg of all steps)
"""

import os
from useful_imports import *
import pandas as pd
import matplotlib.pyplot as plt
import IPython
import numpy as np
from all_joint_angle_toe_touch import get_steps, get_stances, get_swings

rc_params = get_rc_params()
plt.rcParams.update(rc_params)

def get_max_lengths(trial_grouped):
    all_stances_len = []
    all_swings_len = []
    max_swings = []
    max_stances = []
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

def get_max_toe_touch(trial_grouped):
    toe_touches = [] #filled with toe touch idx for each step in each trial
    for trial_id, trial in trial_grouped:
        h5_df = import_kinematics(trial['source-data-h5-path'].iloc[0])
        h5_df['abs-idx'] = range(len(h5_df))
        steps = get_steps(trial, h5_df)
        for step in steps:
            abs_toe_touch = step['abs-toe-touch-idx'].iloc[0]
            rel_toe_touch = abs_toe_touch - step['abs-idx'].iloc[0]
            toe_touches.append(rel_toe_touch)
    max_toe_touch = max(toe_touches)

    return max_toe_touch
        

def get_stepwise_stats(mouse_id, mouse_data, stat):
    """calculates the average line for a group of trials"""
    stats = get_continuous_stats()
 
    trial_grouped = mouse_data.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])
    max_stance_len, max_swing_len, stance_lens, swing_lens = get_max_lengths(trial_grouped)
    max_step_combined_len = max_stance_len + max_swing_len - 1 #subtract 1 because toe touch is included in swing
    max_toe_touch = get_max_toe_touch(trial_grouped) #max toe touch across all trials
    

    steps_arr = np.empty((len(mouse_data), max_step_combined_len))
    for trial_i, (trial_id, trial_data) in enumerate(trial_grouped):
        h5_df = import_kinematics(trial_data['source-data-h5-path'].iloc[0])
        h5_df['abs-idx'] = range(len(h5_df))
        steps_list = get_steps(trial_data, h5_df) #simply called steps in other scripts, here called steps_list to differentiate from steps_arr
        for step_i, step in enumerate(steps_list):
            step['toe-touch-adjusted-idx'] = step['abs-idx'] - step['abs-toe-touch-idx']

            swing_zeros = np.nan*(np.ones(max_swing_len - swing_lens[trial_i][step_i])) #add one for toe touch
            stance_zeros = np.nan*(np.ones(max_stance_len - stance_lens[trial_i][step_i]))
            zeroed_step = list(swing_zeros) + list(step[stat]) + list(stance_zeros)
            steps_arr[step_i] = zeroed_step
            
            #printing statements for figuring out if we are zeroing correctly
            # print(f'max_stance_len: {max_stance_len}')
            # print(f'max_swing_len: {max_swing_len}')
            # print(f'max_toe_touch: {max_toe_touch}')
            # print(f'max_step_combined_len: {max_step_combined_len}') 
            # print(f'swing_len: {swing_lens[trial_i][step_i]}')
            # print(f'swing_zeros: {len(swing_zeros)}')
            # print(f'stance_len: {stance_lens[trial_i][step_i]}')
            # print(f'stance_zeros: {len(stance_zeros)}')
            # print(f'step_len: {len(step[stat])}')
            # print(f'zeroed_step: {len(zeroed_step)}')
            # print(f'toe_touch_step: {step['abs-toe-touch-idx'].iloc[0] - step['abs-idx'].iloc[0]}')
            # print()
    avg_line = np.nanmean(steps_arr, axis=0)
    stdv_line = np.nanstd(steps_arr, axis=0)
        
    return steps_arr, avg_line, stdv_line, max_toe_touch, max_step_combined_len

def graph_stats(mouse_id, mouse_data, steps_arr, avg_line, stdv_line, stat, max_toe_touch, max_length, main_dir, trial_colors = False):
    """graphs the average line for the mouse; also graphs individual steps for all trials; each trial is a color if you want"""
    fig, ax = plt.subplots()
    #get colors for trial
    trial_grouped = mouse_data.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])
    if trial_colors:      
        colors = plt.cm.viridis(np.linspace(0, 1, len(trial_grouped))) #ncolors = ntrials
    else:
        colors = ['black']*len(trial_grouped) #if not coloring by trial, all lines are black

    #get x-axis for trial
    sampling_freq = get_sampling_freq()
    max_toe_touch_time = max_toe_touch/sampling_freq
    time_vec = np.linspace(0.0, max_length/sampling_freq, max_length) - max_toe_touch_time

    #plot steps
    abs_step_i = 0
    for trial_i, (trial_id, trial) in enumerate(trial_grouped):
        for step_i, step in trial.iterrows():
            if step_i == 0:
                ax.plot(time_vec, steps_arr[abs_step_i], color= colors[trial_i], alpha=0.5, label= f'{trial_id[3]}')
                abs_step_i += 1
            else:
                ax.plot(time_vec, steps_arr[abs_step_i], color= colors[trial_i], alpha=0.5)
                abs_step_i += 1
    
    #plot toe touch & avg step
    ax.plot(avg_line, color='black', linewidth=2, label='average')
    plt.axvline(time_vec[max_toe_touch], color = 'black', linestyle = '--')
    
    if trial_colors:
        ax.legend()
    ax.set_ylabel(stat)
    ax.set_xlabel('time (ms)')
    mouse_group = '_'.join(mouse_id[0:2])
    save_folder = os.path.join(main_dir, 'angle_graphs', 'toe_touch_aligned', mouse_group)
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_name = f'{'_'.join(mouse_id)}_{stat}_aligned_at_toe_touch.png'
    plt.savefig(os.path.join(save_folder, save_name))
    #plt.show()
    plt.clf()

    return

def main(main_dir):
    """creates continuous stats for joint & sement angles aligned at toe touch and toe off"""
    step_table_unfiltered = pd.read_csv(os.path.join(main_dir, 'step_table.csv'))
    step_table, dropped_trials = exclude_trials(step_table_unfiltered)
    stats = get_continuous_stats()

    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id'])
    for stat in stats:
        for mouse_id, mouse_data in step_table_grouped:
            mouse_steps_arr, mouse_avg_line, mouse_stdv, max_toe_touch, max_length = get_stepwise_stats(mouse_id, mouse_data, stat)
            graph_stats(mouse_id, mouse_data, mouse_steps_arr, mouse_avg_line, mouse_stdv, stat, max_toe_touch, max_length, main_dir, True)
    
    #something
    return

if __name__ == '__main__':
    main('Full_data')