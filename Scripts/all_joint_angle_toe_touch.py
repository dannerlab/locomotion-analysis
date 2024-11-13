
#for one group, aligned at toe touch

import os, glob
from matplotlib import pyplot as plt
import pandas as pd
import IPython
import numpy as np
from useful_imports import import_kinematics, get_joints_and_segments

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

def calc_avg_lines(steps_arrays, max_length):
    #calculate trialwise avg
    all_avg_lines = np.empty((len(steps_arrays), max_length))
    for trial_i, trial in enumerate(steps_arrays): #steps arrays is num steps * length of longest step
        trial_avg = np.mean(trial, axis = 0)
        all_avg_lines[trial_i] = trial_avg
    avg_avg_line = np.mean(all_avg_lines, axis = 0)
    print(avg_avg_line.shape)
    stdv_avg_line = np.std(all_avg_lines, axis = 0)
    return avg_avg_line, stdv_avg_line


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
        num_steps = 0

        for steps in mouse_steps: #for each trial in this mouse
            for step_i, step in enumerate(steps): #things in these loops done for each step of the mouse, across trials
                step_length = len(step['time'])
                step_lengths.append(step_length)
                num_steps +=1
                if step_length > max_step_length:
                    max_step_length = step_length
                    max_step_index = step_i

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
            
            nums_steps.append(num_steps)

        max_step_lengths.append(max(step_lengths))
        max_step_indices.append(max_step_index)

        max_swing_lengths.append(max(swing_lengths))
        max_swing_indices.append(max_swing_index)

        max_stance_lengths.append(max(stance_lengths))
        max_stance_indices.append(max_stance_index)



    ##make nice tables: length is number of steps, width is max length of any step

    max_swing = max(max_swing_lengths) #max for whole group (of each mouse's max)
    max_stance = max(max_stance_lengths)
    max_length = max_swing + max_stance + 1
    max_toe_touch_idx = max_swing + 1

    steps_arrays = [] #list of arrays for each trial

    for trial_i, trial in enumerate(all_steps_in_group): #for each trial in the group
        steps_array = np.empty((nums_steps[trial_i], max_length)) #array of all steps for this trial

        for step_i, step in enumerate(trial):
            #get indices aligned at toe touch
            step['toe-touch-adjusted-idx'] = step['abs-idx'] - step['abs-toe-touch-idx']    #abs_idx is index for each segment of the step,
                                                                                                #abs_toe_touch_idx is index where toe touch occurs,
                                                                                                #so toe_touch_adjusted idx allows alignment at toe touch

            #establish stats about this particular step
            step_toe_touch = step['abs-toe-touch-idx'].tolist()[0]
            step_swing_length = step_toe_touch - step['abs-idx'].tolist()[0]
            step_stance_length = step['abs-idx'].tolist()[-1] - step_toe_touch

            #pad relative to longest phase of steps in the group
            swing_zeros = np.nan*(np.ones(max_swing - step_swing_length)) #something is wrong because there is a swing that is length of 66 (trial 12, step 6)
            stance_zeros = np.nan*(np.ones(max_stance - step_stance_length))
            zeroed_joint_angle = list(swing_zeros) + list(step[f'{joint_or_seg}']) + list(stance_zeros)
            steps_array[step_i] = zeroed_joint_angle #add this step to the array of all steps for this trial

        steps_arrays.append(steps_array) #add this array to the list of all arrays for all trials in the group

    return steps_arrays, max_toe_touch_idx, max_length

def graph(steps_arrays, group_name, max_toe_touch_idx, joint_or_seg, save_directory, max_length):
        #colors for multicolor
        num_colors = len(steps_arrays)
        cmap = plt.get_cmap('turbo')
        colors = [cmap(i/num_colors) for i in range(num_colors)]

        #colors for groupwise for comparison
        if group_name == 'WT_Incline' or group_name == 'WT_Levelwalk':
            group_color = 'blue'
        elif group_name == 'V3Off_Incline' or group_name == 'V3Off_Levelwalk':
            group_color = 'red'
        else:
            group_color = 'orange'

        #plt.ylim([0, 180])
        for trial_i, trial in enumerate(steps_arrays):
            for step_i, step in enumerate(trial):
                #IPython.embed()
                #fedsakl
                plt.plot(step, color = colors[trial_i], alpha = 0.25)
                #plt.plot(step, color = 'gray', alpha = 0.5)
        #plt.axvline(x=max_toe_touch_idx, color = 'black', linestyle = '--')
        plt.xlabel('Index of step') ###should change code so that x label is time...
        plt.ylabel(f'{joint_or_seg} (\u00B0)')
        #plt.xlim([-0.2, 0.4])
        plt.ylim([30, 140])

        #save & display
        save_name = os.path.join(save_directory, f'{group_name}_{joint_or_seg}_all_trials')
        plt.savefig(f'{save_name}.png')

        #calc_avg_lines(steps_arrays, max_length)

        #graph avg line for each trial
        # plt.ylim([0, 180])
        # print(len(all_avg_lines), len(colors), len(mouse_grouped)) ####probably issues
        # for line_i, line in enumerate(all_avg_lines):
        #     #plt.plot(line, color = colors[line_i], alpha = 0.25, label = trial_names[line_i])
        #     plt.plot(line, color = 'black', alpha = 0.25)
        # plt.plot(avg_avg_line, color = group_color, linewidth = 2)
        # plt.axvline(max_toe_touch_idx)
        # upper = avg_avg_line + std_avg_line
        # lower = avg_avg_line - std_avg_line
        # plt.fill_between(range(len(avg_avg_line)), lower, upper, color = group_color, alpha = 0.2)
        # plt.xlabel('Index of step') ###should change code so that x label is time...
        # plt.ylabel(f'{joint_or_seg} (\u00B0)')


        #save & display
        # save_name = os.path.join(save_directory, f'{group_name}_{joint_or_seg}_AVERAGE_all_trials')
        # plt.savefig(f'{save_name}.png')
        # plt.show()

def main(main_dir):
    #set up statistics names
    joints_and_segments = get_joints_and_segments()
    joint_seg_names = [None] * len(joints_and_segments)
    for idx, joint_or_seg in enumerate(joints_and_segments):
        joint_seg_names[idx] = f'{joint_or_seg}_angle'

    ##directories
    step_table = pd.read_csv(f'{main_dir}/step_table.csv')
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type'])
    save_directory = f'{main_dir}/angle_graphs/toe_touch_aligned'
    if not os.path.exists(save_directory):
        os.makedirs(save_directory, exist_ok = True)

    #actually make the graphs
    for group, group_data in step_table_grouped:
        group_name = '_'.join(group) #should be something like WT_Levelwalk
        print(group_name)
        for joint_or_seg in joint_seg_names:
            if joint_or_seg == 'Hip_angle' or joint_or_seg == 'Ankle_angle':
                steps_arrays, max_toe_touch_idx, max_length = get_steps_array(group_data, joint_or_seg)
                graph(steps_arrays, group_name, max_toe_touch_idx, joint_or_seg, save_directory, max_length)

if __name__ == "__main__":
    main('Full_data')