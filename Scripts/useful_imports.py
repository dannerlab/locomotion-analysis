"""
function for importing kinematics, column names, 
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
                    #x and y positions & excursion of joints for step, swing, and stance
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
                    # hip to toe x position stats
                    "step-Hip_to_Toe_x-min",
                    "step-Hip_to_Toe_x-max",
                    "step-Hip_to_Toe_x-end",
                    "step-Hip_to_Toe_x-excursion",
                    "swing-Hip_to_Toe_x-min",
                    "swing-Hip_to_Toe_x-max",
                    "swing-Hip_to_Toe_x-end",
                    "swing-Hip_to_Toe_x-excursion",
                    "stance-Hip_to_Toe_x-min",
                    "stance-Hip_to_Toe_x-max",
                    "stance-Hip_to_Toe_x-end",
                    "stance-Hip_to_Toe_x-excursion",
                    # interesting stats for full step cycle
                    "step-duration",
                    "cycle-velocity",
                    "duty-factor",
                    "stride-length",
                    #joint angle max, min, excursion for step, swing, and stance
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

def get_rc_params(): #these should be just the params for stick figures
    rc_params = {
        "figure.constrained_layout.use": False,
        "figure.figsize": (5, 4),
        "axes.linewidth": 1,
        "grid.linewidth": 1,
        # Axes
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.formatter.useoffset": False,
        # Font sizes
        "axes.labelsize": 12,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "font.size": 12,
        "lines.markersize": 1.0,
        'xtick.major.pad': 1,
        'ytick.major.pad': 1,
        # save
        "savefig.transparent": True,
        "savefig.bbox": "tight",
        "savefig.dpi": 200,
    }
    return rc_params

#should implement rc_params for the other graphs that are not stick figures

def get_position_stats():
    position_stats = ['ToeTip_x', 'ToeTip_y', 
                      'Ankle_x', 'Ankle_y',
                      'Knee_x', 'Knee_y',
                      'Hip_x', 'Hip_y', 
                      'IliacCrest_x', 'IliacCrest_y',
                      'Hip_to_Toe_x']
    return position_stats

def get_continuous_stats():
    continuous_stats = ['Hip_angle', 'Knee_angle', 'Ankle_angle', 'MTP_angle', 
                        'Crest_angle', 'Thigh_angle', 'Shank_angle']
    return continuous_stats

def get_joints():
    joints = ['Hip', 'Knee', 'Ankle', 'MTP']
    return joints

def get_segments():
    segments = ['Crest', 'Thigh', 'Shank']
    return segments

def get_joints_and_segments():
    joints_and_segments = get_joints() + get_segments()
    return joints_and_segments

def get_sampling_freq():
    sampling_freq = 200
    return sampling_freq

def get_excluded_trials():
    #each tuple is a trial, format is group, condition, trial
    excluded_trials = [('WT', 'Levelwalk', 'gp18m2_1'), ('WT', 'Levelwalk', 'gp17m1')] #need to figure out how many gp17m1 have weird MTP angle for exclusion, currently the avg is all weird
    return excluded_trials