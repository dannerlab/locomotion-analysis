
"""
# This script reads EMG data from HDF5 files, stores them in a dictionary, and plots the EMG traces for specified trials.
# motivated by inability to open spike2 viewer
# first pass at visualizing EMG data
"""
import os, glob
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

directory = "Full_data/WT_Levelwalk/h5_knee_fixed"
h5_paths = glob.glob(os.path.join(directory, '*'))

emg_channels = {}
for h5_path in h5_paths:
    name = os.path.splitext((os.path.basename(h5_path)))[0]
    emg_df = pd.read_hdf(h5_path, key='df_emg')
    emg_channels[name] = emg_df

# 'gp5m3_left_1'
# 'gp5m3_right_2'

# print(emg_channels['gp5m3_left_1'].head())
trials = ['gp5m3_left_1', 'gp5m3_right_2']
for trial in trials:
    color = 'blue' if 'left' in trial else 'red'
    for key_i, key in enumerate(emg_channels[trial].keys()[1:]):
        sns.lineplot(data=emg_channels[trial], x='time', y= key, label = key) 
        
        #alpha = key_i*0.1, color = color)
    plt.legend()
    plt.ylabel('EMG_raw')
    plt.xlabel('time(s)')

    plt.savefig(f'scratch/EMG_{trial}.png')
    plt.show()