
#for each step in mousex:
#    graph each step an angle
# aligned at toe off

#import mousex
import pandas as pd
import matplotlib.pyplot as plt
from useful_imports import import_kinematics
import numpy as np
import os

trial_type = 'WT_Levelwalk'
mouse = 'gp11m1'
side = 'n/a' #left, right, or n/a
trial_n = 1
segment = "Knee" #segment or joint works here

if side == 'n/a':
    h5 = import_kinematics(f'Full_data/{trial_type}/h5_with_stats/{mouse}_{trial_n}.h5')
else:
    h5 = import_kinematics(f'Full_data/{trial_type}/h5_with_stats/{mouse}_{side}_{trial_n}.h5') #if left or right
step_table = pd.read_csv('Full_data/step_table.csv')
step_table_mouse_all = step_table[step_table['mouse-id'] == mouse] #all trials for the mouse
step_table_mouse = step_table_mouse_all[step_table_mouse_all['trial-number'] == trial_n] #specific trial for the mouse
print(step_table_mouse)

#####stuff for viewing segmental angle
lens = []
for step_i, step in step_table_mouse[:-1].iterrows():
   seg_angle = h5[f'{segment}_angle']
   seg_angle_step = seg_angle[int(step['stance-start-idx']):int(step['second-swing-stop-idx'])]
   lens.append(len(seg_angle_step))

arr = np.nan * np.ones((len(step_table_mouse), max(lens)))

first_step_i = step_table_mouse.index[0]
for step_i, step in step_table_mouse[:-1].iterrows():
    seg_angle = h5[f'{segment}_angle']
    seg_angle_step = seg_angle[int(step['stance-start-idx']):int(step['second-swing-stop-idx'])]
    pad_width = max(lens) - len(seg_angle_step)
    seg_angle_step_padded = np.pad(seg_angle_step, (0, pad_width), mode='constant', constant_values=np.nan)
    arr[step_i - first_step_i] = seg_angle_step_padded

for step in arr:
    plt.plot(step)

plt.show()

#toe_off works