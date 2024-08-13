"""Takes step_table.csv and adds x statistics"""

import pandas as pd
import IPython

#import step_table.csv
step_table_fn = 'Sample_data/step_table.csv'
step_table = pd.read_csv(step_table_fn)
step_table_grouped = step_table.groupby(['exp-type', 'mouse-id', 'trial-number'])

key = 'df_kinematics'

modified_trials = []

for name, trial in step_table_grouped:
    h5_path = trial['source-data-h5-path'].iloc[0]
    h5_df = pd.read_hdf(h5_path, key)

    step_x_maxes = []
    step_x_mins = []
    step_x_ends = []

    for step_i in range(len(trial)):
        step_start = trial['swing-start-idx'].iloc[step_i]
        step_stop = trial['stance-stop-idx'].iloc[step_i]
        step_slice = h5_df[step_start:step_stop]
        step_slice_x = step_slice['ToeTip_x'] - step_slice['Hip_x']
        step_x_max = max(step_slice_x)
        step_x_maxes.append(step_x_max)
        step_x_min = min(step_slice_x)
        step_x_mins.append(step_x_min)
        step_x_end = step_slice_x.iloc[-1]
        step_x_ends.append(step_x_end)

    trial['ToeTip_x_max'] = step_x_maxes
    trial['ToeTip_x_min'] = step_x_mins
    trial['ToeTip_x_end'] = step_x_ends
    trial['ToeTip_x_excursion'] = trial['ToeTip_x_max'] - trial['ToeTip_x_min']

    modified_trials.append(trial)

step_table_with_x = pd.concat(modified_trials)

#save
step_table_with_x.to_csv(step_table_fn, index = False)
