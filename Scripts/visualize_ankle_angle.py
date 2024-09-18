"""
Graph ankle angle
"""
import pandas as pd
import numpy as np
from Scripts.useful_imports import import_kinematics
import seaborn as sns
import matplotlib.pyplot as plt


def graph_ankle(step_table):

    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number',])
    colors = sns.color_palette("husl", len(step_table_grouped))

    for trial_i, (name, trial) in enumerate(step_table_grouped):
        trial_name = "_".join(str(item) for item in name)
        h5_df = import_kinematics(trial['source-data-h5-path'].iloc[0])
        print(trial_name)#, len(trial), len(h5_df))
        for step_i, step in trial.iterrows():
            start = step['swing-start-idx']
            stop = step['stance-stop-idx']
            step_h5 = h5_df.iloc[start:stop].copy()
            step_h5.loc[:, 'aligned-time'] = step_h5['time'] - step['swing-start']
            sns.lineplot(step_h5, x='aligned-time', y='ToeTip_y', color = colors[trial_i])
        sns.lineplot(step_h5, x='aligned-time', y='ToeTip_y', color=colors[trial_i], label=trial_name)
    plt.legend()
    plt.show()

    return

#graph them so I can see

def main():
    step_table = pd.read_csv("Sample_data/step_table.csv")
    graph_ankle(step_table)
    return

if __name__ == "__main__":
    main()
