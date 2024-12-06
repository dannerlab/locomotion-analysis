"""
calculate segmental angles throughout step cycle & add this data to h5 file
for one trial
"""

import pandas as pd
import numpy as np
from useful_imports import import_kinematics
import os

def calculate_segmental_angles(h5_path, segment_dict):
    h5_df = import_kinematics(h5_path)
    for segment in segment_dict:
        upper_joint = segment_dict[segment][0]
        lower_joint = segment_dict[segment][1]
        upper_x = h5_df[f'{upper_joint}_x']
        upper_y = h5_df[f'{upper_joint}_y']
        lower_x = h5_df[f'{lower_joint}_x']
        lower_y = h5_df[f'{lower_joint}_y']
        radians_angle = np.arctan2((upper_y - lower_y), (upper_x - lower_x))
        if segment == 'Thigh':
            radians_angle = np.mod(radians_angle, 2 * np.pi) # Ensure the angle is within the range [0, 2π]
        degrees_angle = np.degrees(radians_angle)
        h5_df[f'{segment}_angle'] = degrees_angle

    #save new h5
    base_dir = os.path.dirname(os.path.dirname(h5_path))
    save_dir = os.path.join(base_dir, 'h5_with_stats')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_h5_path = os.path.join(save_dir, os.path.basename(h5_path))
    h5_df.to_hdf(save_h5_path, key='df_kinematics', mode='a',complevel=9)

    return save_h5_path

def main():
    #for testing, normally run through step_table_initialize
    #formatting of segment dict = {"Segment": ["UpperJoint", "LowerJoint"]}
    segment_dict = {"Crest": ["IliacCrest", "Hip"],
                    "Thigh": ["Hip", "Knee"],
                    "Shank": ["Knee", "Ankle"]}

    og_h5_path = 'Full_data/V3Off_Levelwalk/h5_knee_fixed/gp15m2_left_1.h5'

    save_path = calculate_segmental_angles(og_h5_path, segment_dict)
    print(save_path)


if __name__ == "__main__":
    main()