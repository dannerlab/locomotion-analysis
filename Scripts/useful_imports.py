"""
function for importing kinematics
"""
import pandas as pd
import os

def import_kinematics(file):
    #imports the kinematics portion of the hdf
    if not os.path.exists(file):
        print(f"File not found: {file}")
        return None
    key = 'df_kinematics'
    kinematics_df = pd.read_hdf(file, key)
    return kinematics_df

def get_numeric_col_names():
    selected_col_names = ['stance-duration',
                    'swing-duration',
                    "step-ToeTip_x-min",
                    "step-ToeTip_x-max",
                    "step-ToeTip_x-end",
                    "step-ToeTip_x-excursion",
                    "step-ToeTip_y-min",
                    "step-ToeTip_y-max",
                    "step-ToeTip_y-end",
                    "step-ToeTip_y-excursion",
                    "step-IliacCrest_y-min",
                    "step-IliacCrest_y-max",
                    "step-IliacCrest_y-end",
                    "step-IliacCrest_y-excursion",
                    "swing-ToeTip_x-min",
                    "swing-ToeTip_x-max",
                    "swing-ToeTip_x-end",
                    "swing-ToeTip_x-excursion",
                    "swing-ToeTip_y-min",
                    "swing-ToeTip_y-max",
                    "swing-ToeTip_y-end",
                    "swing-ToeTip_y-excursion",
                    "swing-IliacCrest_y-min",
                    "swing-IliacCrest_y-max",
                    "swing-IliacCrest_y-end",
                    "swing-IliacCrest_y-excursion",
                    "stance-ToeTip_x-min",
                    "stance-ToeTip_x-max",
                    "stance-ToeTip_x-end",
                    "stance-ToeTip_x-excursion",
                    "stance-ToeTip_y-min",
                    "stance-ToeTip_y-max",
                    "stance-ToeTip_y-end",
                    "stance-ToeTip_y-excursion",
                    "stance-IliacCrest_y-min",
                    "stance-IliacCrest_y-max",
                    "stance-IliacCrest_y-end",
                    "stance-IliacCrest_y-excursion",
                    "step-duration",
                    "cycle-velocity",
                    "duty-factor",
                    "stride-length",
                    "step-Hip_angle-min",
                    "step-Hip_angle-max",
                    "step-Hip_angle-excursion",
                    "step-Knee_angle-min",
                    "step-Knee_angle-max",
                    "step-Knee_angle-excursion",
                    "step-Ankle_angle-min",
                    "step-Ankle_angle-max",
                    "step-Ankle_angle-excursion",
                    "step-MTP_angle-min",
                    "step-MTP_angle-max",
                    "step-MTP_angle-excursion",
                    "swing-Hip_angle-min",
                    "swing-Hip_angle-max",
                    "swing-Hip_angle-excursion",
                    "swing-Knee_angle-min",
                    "swing-Knee_angle-max",
                    "swing-Knee_angle-excursion",
                    "swing-Ankle_angle-min",
                    "swing-Ankle_angle-max",
                    "swing-Ankle_angle-excursion",
                    "swing-MTP_angle-min",
                    "swing-MTP_angle-max",
                    "swing-MTP_angle-excursion",
                    "stance-Hip_angle-min",
                    "stance-Hip_angle-max",
                    "stance-Hip_angle-excursion",
                    "stance-Knee_angle-min",
                    "stance-Knee_angle-max",
                    "stance-Knee_angle-excursion",
                    "stance-Ankle_angle-min",
                    "stance-Ankle_angle-max",
                    "stance-Ankle_angle-excursion",
                    "stance-MTP_angle-min",
                    "stance-MTP_angle-max",
                    "stance-MTP_angle-excursion",
                    "step-Crest-min",
                    "step-Crest-max",
                    "step-Crest-excursion",
                    "step-Thigh-min",
                    "step-Thigh-max",
                    "step-Thigh-excursion",
                    "step-Shank-min",
                    "step-Shank-max",
                    "step-Shank-excursion",
                    "swing-Crest-min",
                    "swing-Crest-max",
                    "swing-Crest-excursion",
                    "swing-Thigh-min",
                    "swing-Thigh-max",
                    "swing-Thigh-excursion",
                    "swing-Shank-min",
                    "swing-Shank-max",
                    "swing-Shank-excursion",
                    "stance-Crest-min",
                    "stance-Crest-max",
                    "stance-Crest-excursion",
                    "stance-Thigh-min",
                    "stance-Thigh-max",
                    "stance-Thigh-excursion",
                    "stance-Shank-min",
                    "stance-Shank-max",
                    "stance-Shank-excursion"]
    return(selected_col_names)