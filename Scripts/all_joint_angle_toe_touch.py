
#for one group, aligned at toe touch

import os, glob
from matplotlib import pyplot as plt
import pandas as pd
import IPython
import numpy as np
from useful_imports import import_kinematics, get_joints_and_segments, get_sampling_freq, get_rc_params, exclude_trials, get_color
def get_steps(stepcycle_df, h5_df):
    steps = []
    for idx in range(len(stepcycle_df)):
        step = h5_df.loc[stepcycle_df['swing-start-idx'].iloc[idx] : stepcycle_df['stance-stop-idx'].iloc[idx]].copy()
        step['abs-toe-touch-idx'] = stepcycle_df['stance-start-idx'].iloc[idx] #abs_toe_touch_idx is the index where toe touch occurs
        steps.append(step)
    return steps

def get_swings(stepcycle_df, h5_df):
    swings = []
    for idx in range(len(stepcycle_df)):
        swing = h5_df.loc[stepcycle_df['swing-start-idx'].iloc[idx] : stepcycle_df['swing-stop-idx'].iloc[idx]].copy()
        swings.append(swing)
    return swings

def get_stances(stepcycle_df, h5_df):
    stances = []
    for idx in range(len(stepcycle_df)):
        stance = h5_df.loc[stepcycle_df['stance-start-idx'].iloc[idx] : stepcycle_df['stance-stop-idx'].iloc[idx]].copy()
        stances.append(stance)
    return stances

def get_steps_array(group, joint_or_seg):
    #calculations
    ##min/max step length for trial
    all_steps_in_group = []
    all_swings_in_group = []
    all_stances_in_group = []

    max_step_lengths = []
    max_swing_lengths = []
    max_stance_lengths = []

    nums_steps = []
    max_step_indices = []
    max_swing_indices = []
    max_stance_indices = []

    mouse_wise_grouped = group.groupby('mouse-id')
    
    #for each mouse in the group
    for id, mouse_data in mouse_wise_grouped: #things inside this loop done for all steps of a given mouse, but only for one mouse at a time

        mouse_stepcycles = []
        mouse_h5s = []
        trial_grouped = mouse_data.groupby('trial-number')
        for trial, trial_data in trial_grouped:
            stepcycle = trial_data
            h5 = import_kinematics(trial_data['source-data-h5-path'].iloc[0])
            h5['abs-idx'] = range(len(h5))
            mouse_stepcycles.append(stepcycle)
            mouse_h5s.append(h5)
        
        step_lengths = []
        swing_lengths = []
        stance_lengths = []
        mouse_steps = [] # trialwise list of all steps for this mouse
        mouse_swings = []
        mouse_stances = []
        
        for stepcycle, h5 in zip(mouse_stepcycles, mouse_h5s): # for each trial in this mouse
            steps = get_steps(stepcycle, h5)
            mouse_steps.append(steps) #add it to this mouse
            swings = get_swings(stepcycle, h5)
            mouse_swings.append(swings)
            stances = get_stances(stepcycle, h5)
            mouse_stances.append(stances)
            all_steps_in_group.append(steps) #add it to the whole group
            all_swings_in_group.append(swings) 
            all_stances_in_group.append(stances)

        max_step_length = 0
        max_stance_length = 0
        max_swing_length = 0
        max_step_index = 0
        max_swing_index = 0
        max_stance_index = 0

        for steps in mouse_steps: #for each trial in this mouse
            num_steps = 0
            for step_i, step in enumerate(steps): #things in these loops done for each step of the mouse, across trials
                step_length = len(step['time'])
                step_lengths.append(step_length)
                num_steps +=1
                if step_length > max_step_length:
                    max_step_length = step_length
                    max_step_index = step_i
            nums_steps.append(num_steps)

        for swings in mouse_swings:
            for swing_i, swing in enumerate(swings):
                swing_length = len(swing['time'])
                swing_lengths.append(swing_length)
                if swing_length > max_swing_length:
                    max_swing_length = swing_length
                    max_swing_index = swing_i

        for stances in mouse_stances:
            for stance_i, stance in enumerate(stances):
                stance_length = len(stance['time'])
                stance_lengths.append(stance_length)
                if stance_length > max_stance_length:
                    max_stance_length = stance_length
                    max_stance_index = stance_i
            
            

        max_step_lengths.append(max(step_lengths))
        max_step_indices.append(max_step_index)

        max_swing_lengths.append(max(swing_lengths))
        max_swing_indices.append(max_swing_index)

        max_stance_lengths.append(max(stance_lengths))
        max_stance_indices.append(max_stance_index)



    ##make nice tables: length is number of steps, width is max length of any step

    max_swing = max(max_swing_lengths) #max for whole group (of each mouse's max)
    max_stance = max(max_stance_lengths)
    max_length = max_swing + max_stance - 1 
    max_toe_touch_idx = max_swing

    mouse_avg_steps = [] #list of avg lists for each trial
    trial_counter = 0 #to allow iteration through all_steps_in_group by absolute trial index regardless of mouse grouping
    for id, mouse in mouse_wise_grouped: #for each mouse in the group
        errors_printed = []
        mouse_trials_list = [] #list to be filled with all trial arrays for this mouse
        for trial_i in mouse['trial-number'].unique(): #for each trial in the mouse
            trial_steps_array = np.nan * np.ones((nums_steps[trial_counter], max_length)) #array to be fileld with all steps for this trial
            trial = all_steps_in_group[trial_counter] #all steps for this trial
            trial_counter += 1
            for step_i, step in enumerate(trial): #the problem is that it is overwriting because step_i re-sets.. maybe? for some reason trial arrays after the first trial seem to be blank
                #get indices aligned at toe touch
                step['toe-touch-adjusted-idx'] = step['abs-idx'] - step['abs-toe-touch-idx']    #abs_idx is index for each segment of the step,
                                                                                                    #abs_toe_touch_idx is index where toe touch occurs,
                                                                                                    #so toe_touch_adjusted idx allows alignment at toe touch

                #establish stats about this particular step
                step_toe_touch = step['abs-toe-touch-idx'].tolist()[0]
                step_swing_length = step_toe_touch - step['abs-idx'].tolist()[0]
                step_stance_length = step['abs-idx'].tolist()[-1] - step_toe_touch

                #pad relative to longest phase of steps in the group
                #np.empty(np.nan(max_length, 1))
                swing_zeros = np.nan*(np.ones(max_swing - step_swing_length - 1))
                stance_zeros = np.nan*(np.ones(max_stance - step_stance_length - 1))
                try:
                    zeroed_joint_angle = list(swing_zeros) + list(step[f'{joint_or_seg}']) + list(stance_zeros)
                    trial_steps_array[step_i] = zeroed_joint_angle #add this step to the array of all steps for this trial
                except KeyError:
                    mouse_name = mouse['mouse-id'].iloc[0]
                    if (mouse_name, joint_or_seg) not in errors_printed:
                        print(f'{joint_or_seg} not found in {mouse_name}')
                        errors_printed.append((mouse_name, joint_or_seg))
                    trial_steps_array = trial_steps_array[:-1]
            if len(trial_steps_array) > 0:
                mouse_trials_list.append(trial_steps_array) #add this array to the list of all arrays for all trials in the group
        
        #combine all trials into one array for the mouse that contains all steps (think concat; eliminate trial data)
        mouse_trials_arr = np.nan * np.ones((len(mouse), max_length))
        step_i = 0
        trial_i = 0
        for trial in mouse_trials_list: #remember each trial is a list of arrays
            trial_i += 1
            for step in trial:
                mouse_trials_arr[step_i] = step
                step_i += 1
        
        #find avg step for the mouse
        avg_mouse_step = np.mean(mouse_trials_arr, axis = 0)

        #list of avg steps by mouse
        mouse_avg_steps.append(avg_mouse_step)
        
    #find avg step for the group
    group_avg_step = np.mean(mouse_avg_steps, axis=0)
    group_stdv = np.std(mouse_avg_steps, axis=0)


    return mouse_avg_steps, group_avg_step, max_toe_touch_idx, max_length, group_stdv

def graph_one_group(mouse_avg_steps, group_avg_step, group_name, max_toe_touch_idx, joint_or_seg, save_directory, max_length, group, group_stdv):
    plt.clf()
    #colors for multicolor
    num_colors = len(mouse_avg_steps)
    cmap = plt.get_cmap('turbo')
    colors = [cmap(i/num_colors) for i in range(num_colors)]

    #colors for groupwise for comparison
    group_color = get_color(group_name)
        
    #x axis values
    #x calculations
    sampling_freq = get_sampling_freq()
    max_toe_touch_time = max_toe_touch_idx/sampling_freq
    time_vec = np.linspace(0.0, (max_length - 1)/sampling_freq, max_length) - max_toe_touch_time

    #plot avg for each mouse within group + group avg line
    mouse_wise_grouped = group.groupby('mouse-id')
    mouse_ids = list(mouse_wise_grouped.groups.keys())
    for mouse_i, mouse in enumerate(mouse_avg_steps):
        #plt.plot(time_vec, mouse, color = colors[mouse_i], alpha = .75, label = mouse_ids[mouse_i]) #uncomment for color for each mouse, comment next line
        plt.plot(time_vec, mouse, color = 'grey', alpha = 0.25) #uncomment for grey for each mouse, comment above line
    plt.axvline(time_vec[max_toe_touch_idx], color = 'black', linestyle = '--')
    plt.plot(time_vec, group_avg_step, color = group_color, linewidth = 2)
    upper = group_avg_step + group_stdv
    lower = group_avg_step - group_stdv
    plt.fill_between(time_vec, lower, upper, color = group_color, alpha = 0.2)
    plt.xlabel('Time of step (s)')
    plt.ylabel(f'{joint_or_seg} (\u00B0)')
    #plt.legend() #uncomment for mousewise colors
    plt.xlim([-0.2, 0.35])
    plt.ylim([0, 180])
    plt.yticks(np.arange(0, 181, 30), labels=None)
    if joint_or_seg == "Shank_angle" or joint_or_seg == "Crest_angle":
        plt.ylim([-30, 150])
        plt.yticks(np.arange(-30, 151, 30), labels=None)
    if joint_or_seg == "Thigh_angle":
        plt.ylim([30, 210])
        plt.yticks(np.arange(30, 211, 30), labels=None)

    #save & display
    save_name = os.path.join(save_directory, f'{group_name}_{joint_or_seg}_all_trials')
    plt.savefig(f'{save_name}.png')
    #plt.show()
    return save_directory

def graph_many_groups(steps_arrays_dicts_list, joint_or_seg, save_directory):
    plt.clf()

    #color, plot, & label each group
    for group_i, group_dict in enumerate(steps_arrays_dicts_list):
        #x axis values
        sampling_freq = get_sampling_freq()
        max_length = steps_arrays_dicts_list[group_i]['max_length'] 
        max_toe_touch_idx = steps_arrays_dicts_list[group_i]['max_toe_touch_idx']
        max_toe_touch_time = max_toe_touch_idx/sampling_freq
        time_vec = np.linspace(0.0, (max_length - 1)/sampling_freq, max_length) - max_toe_touch_time

        #colors for groups if it is WT vs V3Off
        group_avg_step = group_dict['group_avg_step']
        group = group_dict['group']
        group_name = '_'.join(group)
        group_color = get_color(group_name)

        #name & plot
        group_name = group_dict['group_name']
        for mouse_i, mouse in enumerate(group_dict['mouse_avg_steps']): #plot mice avg in group, may or may not be useful
            plt.plot(time_vec, mouse, color = group_color, alpha = 0.25)
        plt.plot(time_vec, group_avg_step, color = group_color, label = group_name) #plot group avg
        group_stdv = group_dict['group_stdv']
        upper = group_avg_step + group_stdv
        lower = group_avg_step - group_stdv
        plt.fill_between(time_vec, lower, upper, color = group_color, alpha = 0.2)

    plt.axvline(time_vec[max_toe_touch_idx], color = 'black', linestyle = '--') #plot toe touch line
    plt.xlabel('Time of step (s)')
    plt.ylabel(f'{joint_or_seg} (\u00B0)')
    plt.legend()
    plt.xlim([-0.2, 0.35])
    plt.ylim([0, 180])
    plt.yticks(np.arange(0, 181, 30), labels=None)
    if joint_or_seg == "Shank_angle" or joint_or_seg == "Crest_angle":
        plt.ylim([-30, 150])
        plt.yticks(np.arange(-30, 151, 30), labels=None)
    if joint_or_seg == "Thigh_angle":
        plt.ylim([30, 210])
        plt.yticks(np.arange(30, 211, 30), labels=None)

    #save & display
    group_names = '_'.join([group_dict['group_name'] for group_dict in steps_arrays_dicts_list])
    save_name = os.path.join(save_directory, f'{joint_or_seg}_{group_names}')
    plt.savefig(f'{save_name}.png')
    #plt.show()

def main(main_dir, selected_groups):
    #set up statistics names & rc params
    joints_and_segments = get_joints_and_segments()
    joint_seg_names = [None] * len(joints_and_segments)
    for idx, joint_or_seg in enumerate(joints_and_segments):
        joint_seg_names[idx] = f'{joint_or_seg}_angle'
    rc_params = get_rc_params()
    plt.rcParams.update(rc_params)

    ##directories
    step_table_unfiltered = pd.read_csv(f'{main_dir}/step_table.csv')
    step_table, excluded_trials = exclude_trials(step_table_unfiltered)
    step_table_grouped_all_groups = step_table.groupby(['mouse-type', 'exp-type'])
    
    if selected_groups != step_table_grouped_all_groups.groups.keys():
        step_table_selected = [step_table_grouped_all_groups.get_group(group) for group in selected_groups]
        step_table_grouped = pd.concat(step_table_selected).groupby(['mouse-type', 'exp-type'])
    save_directory = f'{main_dir}/angle_graphs/toe_touch_aligned'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory, exist_ok = True)

    #actually make the graphs
    save_dirs = []
    for joint_or_seg in joint_seg_names:
        steps_arrays_dicts_list = []
        for group, group_data in step_table_grouped:
            group_name = '_'.join(group) #should be something like WT_Levelwalk
            mouse_avg_steps, group_avg_step, max_toe_touch_idx, max_length, group_stdv = get_steps_array(group_data, joint_or_seg)
            #graph just the one group for this stat
            save_dir = graph_one_group(mouse_avg_steps, group_avg_step, group_name, max_toe_touch_idx, joint_or_seg, save_directory, max_length, group_data, group_stdv)
            if save_dir not in save_dirs:
                save_dirs.append(save_dir)
            #add to array so we can graph both groups for this stat
            steps_arrays_dict = {'group': group,
                                'group_data': group_data,
                                'group_name': group_name,
                                'mouse_avg_steps': mouse_avg_steps,
                                'group_avg_step': group_avg_step,
                                'max_toe_touch_idx': max_toe_touch_idx,
                                'max_length': max_length,
                                'group_stdv': group_stdv,
                                }       
            steps_arrays_dicts_list.append(steps_arrays_dict)

        #graph group avgs for this stat
        graph_many_groups(steps_arrays_dicts_list, joint_or_seg, save_directory)

    for save_dir in save_dirs:
        print(f'saved to: {save_dir}')

if __name__ == "__main__":
    selected_groups = [('WT', 'Incline'), ('V3Off', 'Incline')]
    main('Full_data', selected_groups)