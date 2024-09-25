"""
Graph ankle angle
"""
import pandas as pd
from useful_imports import import_kinematics
import seaborn as sns
import matplotlib.pyplot as plt
import os

def get_color(name, step_table_grouped, trial_i):
    #for a different color for each trial, use these settings
    #colors = sns.color_palette("husl", len(step_table_grouped))
    #color = colors[trial_i]

    #for color dependent on group, modify these:
    color_dict = {
        'WT_Levelwalk': 'blue',
        'V3Off_Levelwalk': 'red',
        'WT_Incline' : 'green',
        'V3Off_Incline': 'orange',
    }

    mouse_type = f'{name[0]}_{name[1]}'
    color = color_dict[mouse_type]

    return color

def graph_stat(step_table_path):

    #load table
    step_table = pd.read_csv(step_table_path)
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])

    #get save paths
    save_location_toe_off = os.path.join(os.path.dirname(step_table_path), 'trialwise_joint_graphs_toe_off')
    if not os.path.exists(save_location_toe_off):
        os.makedirs(save_location_toe_off)
    save_location_toe_touch = os.path.join(os.path.dirname(step_table_path), 'trialwise_joint_graphs_toe_touch')
    if not os.path.exists(save_location_toe_touch):
        os.makedirs(save_location_toe_touch)

    #select stats
    stats_unfiltered = import_kinematics(step_table['source-data-h5-path'].iloc[0]).columns.tolist()
    not_graph_columns = ['time', 'Toe_off', 'Toe_touch']
    stats = []
    for col in stats_unfiltered:
        if col not in not_graph_columns:
            stats.append(col)

    for stat in stats:
        ###align at toe touch
        for trial_i, (name, trial) in enumerate(step_table_grouped):
            trial_name = "_".join(str(item) for item in name)
            h5_df = import_kinematics(trial['source-data-h5-path'].iloc[0])
            color = get_color(name, step_table_grouped, trial_i)
            for step_i, step in trial.iterrows():
                start = step['swing-start-idx']
                stop = step['stance-stop-idx']
                step_h5 = h5_df.iloc[start:stop].copy()
                step_h5.loc[:, 'aligned-time'] = step_h5['time'] - step['stance-start']
                sns.lineplot(step_h5, x='aligned-time', y= stat, color = color, alpha = 0.5)
            sns.lineplot(step_h5, x='aligned-time', y=stat, color=color, alpha=0, label=trial_name) #this is here to generate the legend
        plt.axvline(x = 0, color = 'black', linestyle='--') #line at toe touch
        plt.xlabel('Toe Touch Aligned Time (s)')
        plt.legend()
        save_name = f'{stat}_toe_touch.png'
        plt.savefig(os.path.join(save_location_toe_touch, save_name))
        plt.clf()

        ###align at toe off
        for trial_i, (name, trial) in enumerate (step_table_grouped):
            trial_name = "_".join(str(item) for item in name)
            h5_df = import_kinematics(trial['source-data-h5-path'].iloc[0])
            color = get_color(name, step_table_grouped, trial_i)
            for step_i, step in trial[:-1].iterrows():
                start = int(step['stance-start-idx'])
                stop = int(step['second-swing-stop-idx'])
                step_h5 = h5_df.iloc[start:stop].copy()
                step_h5.loc[:, 'aligned-time'] = step_h5['time'] - step['second-swing-start']
                sns.lineplot(step_h5, x='aligned-time', y= stat, color = color, alpha = 0.5)
            sns.lineplot(step_h5, x='aligned-time', y=stat, color=color, label=trial_name)
        plt.axvline(x = 0, color = 'black', linestyle='--') #line at toe off
        plt.xlabel('Toe Off Aligned Time (s)')
        plt.legend()
        save_name = f'{stat}_toe_off.png'
        plt.savefig(os.path.join(save_location_toe_off, save_name))
        plt.clf()

    return

def main():
    step_table_path = "Sample_data/step_table.csv"
    graph_stat(step_table_path)

    return

if __name__ == "__main__":
    main()
