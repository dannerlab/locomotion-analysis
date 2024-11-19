"""
calculate segmental angles throughout step cycle & add this data to h5 file
"""

import pandas as pd
import numpy as np
from useful_imports import import_kinematics

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
        degrees_angle = np.degrees(radians_angle)
        h5_df[f'{segment}_angle'] = degrees_angle
        #adds column & calculates angles for shank
        #radians by default

    #save new h5
    h5_df.to_hdf(h5_path, key='df_kinematics', mode='a',complevel=9)

    return

def main():
    #for testing, normally run through step_table_initialize
    #formatting of segment dict = {"Segment": ["UpperJoint", "LowerJoint"]}
    segment_dict = {"Crest": ["IliacCrest", "Hip"],
                    "Thigh": ["Hip", "Knee"],
                    "Shank": ["Knee", "Ankle"]}

    calculate_segmental_angles('Sample_data/WT_Levelwalk/h5/gp3m3_1.h5', segment_dict)

    #h5_paths
    #modify h5s


if __name__ == "__main__":
    main()