

import os
import pandas as pd

def import_kinematics(file):
    #imports the kinematics portion of the hdf
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return None
    key = 'df_kinematics'
    kinematics_df = pd.read_hdf(file, key)
    return kinematics_df

def add_discrete_stats(step_table):

    toe_tip_x_max = []
    toe_tip_x_min = []
    toe_tip_x_end = []
    toe_tip_x_excursion = []
    toe_tip_y_max = []
    iliac_crest_y_max = []
    iliac_crest_y_min = []
    iliac_crest_y_excursion = []

    for step_i, trial in step_table.iterrows():
        h5_path = trial['source-data-h5-path']
        h5_df = import_kinematics(h5_path)

        # Get step slice
        start = trial['swing-start-idx']
        stop = trial['stance-stop-idx']
        step_slice = h5_df[start:stop]

        # Calculate x toe statistics normalized to hip x
        slice_toe_x = step_slice['ToeTip_x'] - step_slice['Hip_x']
        toe_tip_x_max.append(slice_toe_x.max())
        toe_tip_x_min.append(slice_toe_x.min())
        toe_tip_x_end.append(slice_toe_x.iloc[-1])
        toe_tip_x_excursion.append(slice_toe_x.max() - slice_toe_x.min())

        # Calculate y toe & crest statistics
        toe_tip_y_max.append(step_slice['ToeTip_y'].max())
        iliac_crest_y_max.append(step_slice['IliacCrest_y'].max())
        iliac_crest_y_min.append(step_slice['IliacCrest_y'].min())
        iliac_crest_y_excursion.append(step_slice['IliacCrest_y'].max() - step_slice['IliacCrest_y'].min())

    # Assign the calculated statistics back to the DataFrame
    step_table['ToeTip_x_max'] = toe_tip_x_max
    step_table['ToeTip_x_min'] = toe_tip_x_min
    step_table['ToeTip_x_end'] = toe_tip_x_end
    step_table['ToeTip_x_excursion'] = toe_tip_x_excursion
    step_table['ToeTip_y_max'] = toe_tip_y_max
    step_table['IliacCrest_y_max'] = iliac_crest_y_max
    step_table['IliacCrest_y_min'] = iliac_crest_y_min
    step_table['IliacCrest_y_excursion'] = iliac_crest_y_excursion

    return step_table