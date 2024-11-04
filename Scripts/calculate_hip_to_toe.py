import pandas as pd
from useful_imports import import_kinematics

def calculate_hip_to_toe_x(h5_path):
    h5_df = import_kinematics(h5_path)
    h5_df['Hip_to_Toe_x'] = h5_df['ToeTip_x'] - h5_df['Hip_x']
    h5_df.to_hdf(h5_path, key='df_kinematics', mode='a',complevel=9)
    return