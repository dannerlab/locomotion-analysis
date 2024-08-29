"""
uses animal_avg & stdv to compare 2 groups via ANOVA
needs filtering still
"""

import pandas as pd
import os
from scipy.stats import shapiro
from scipy.stats import f_oneway
import scipy.stats as stats
import numpy as np
from useful_imports import get_numeric_col_names

def combine_dicts(*dicts): #GitHub Co-pilot assistance
    combined_dict = {}
    for key in dicts[0].keys():
        combined_dict[key] = []
        for d in dicts:
            combined_dict[key].extend(d[key])

    return combined_dict


def standardize_residuals(step_table_grouped, selected_stats):
    #combined residuals
    ##calculate residuals for each statistic and store in residuals dict
    residuals = {group: {} for group in step_table_grouped.groups.keys()}
    ##residuals dict is formatted as: {group: {stat: residuals col}}
    for group, data in step_table_grouped:
        selected_data = data[selected_stats]
        for col in selected_data:
            col_mean = np.mean(selected_data[col])
            col_residual = selected_data[col] - col_mean
            residuals[group][col] = list(col_residual)

    combined_residuals = combine_dicts(*residuals.values()) #extracts so they are no longer by group

    #standardized residuals
    ##find stdv of residuals for all stats
    stdv_residuals = pd.Series(index=combined_residuals.keys())
    for stat in combined_residuals:
        stat_stdv = np.nanstd(combined_residuals[stat]) #ignores NaN values
        stdv_residuals.loc[stat] = stat_stdv

    ##standardize the residuals
    standardized_residuals = pd.DataFrame(columns=combined_residuals.keys())
    for key in combined_residuals:
        standardized_residuals[key] = combined_residuals[key] / stdv_residuals[key]

    return standardized_residuals


def shapiro_and_k(standardized_residuals, alpha):
    #tests for normalcy
    shapiro_non_normal = {}
    shapiro_normal = {}
    k_non_normal = {}
    k_normal = {}

    for key in standardized_residuals:
        shapiro_residual = shapiro(standardized_residuals[key])[1]
        if shapiro_residual <= alpha: #add only non normal stats to the dictionary
            shapiro_non_normal[key] = shapiro_residual
        else:
            shapiro_normal[key] = shapiro_residual

        k_residual = stats.kstest(standardized_residuals[key], 'norm')[1]
        if k_residual <= alpha: #adds only non normal stats to the dictionary
            k_non_normal[key] = k_residual
        else:
            k_normal[key] = k_residual

    #combined filtered
    normal_stats = {}
    non_normal_stats = {}
    for key in standardized_residuals:
        if key in shapiro_non_normal.keys():
            if key in k_non_normal.keys():
                non_normal_stats[key] = [shapiro_non_normal[key], k_non_normal[key]]
            else:
                non_normal_stats[key] = [shapiro_non_normal[key], k_normal[key]]
        elif key in k_non_normal.keys():
            non_normal_stats[key] = [shapiro_normal[key], k_non_normal[key]]
        else:
            normal_stats[key] = [shapiro_normal[key], k_normal[key]]

    #convert to dict
    normal_stats = pd.DataFrame(normal_stats, index=['shapiro_p', 'kolmogorov-smirnov_p'])
    non_normal_stats = pd.DataFrame(non_normal_stats, index=['shapiro_p', 'kolmogorov-smirnov_p'])
    return normal_stats, non_normal_stats


def calc_anova(step_table_grouped, selected_stats, alpha):
    list_of_selected_groups = []
    for group, data in step_table_grouped:
        selected_data = data[selected_stats]
        list_of_selected_groups.append(selected_data)

    one_way_p = {}

    for key in selected_stats:
        group_stats = [] #list of selected columns (via key) for each group
        for group in list_of_selected_groups:
            group_stats.append(group[key])
        p_val = f_oneway(*(group_stats))[1]
        if p_val <= alpha: #filter for significance
            one_way_p[key] = p_val

    #format for nicer saving
    one_way_p = pd.Series(one_way_p.values(),index=one_way_p.keys()).to_frame()
    one_way_p = one_way_p.rename(columns = {0: 'ANOVA_p_value'})

    return one_way_p


def compare_animal_means(animal_stats_fp, alpha):
    '''Runs stats on avgs of each animal (Han style)'''
    animal_stats = pd.read_csv(animal_stats_fp)
    animal_stats_grouped = animal_stats.groupby(['mouse-type', 'exp-type'])
    stats = animal_stats.filter(like='avg-').columns
    #since col names for avgs all begin with avg, cannot use get_numeric_col_names()
    #that is ok because get_numeric_col_names() is used to generate this table so re-running will update here also

    standardized_animal_grouped = standardize_residuals(animal_stats_grouped, stats)
    normal, non_normal = shapiro_and_k(standardized_animal_grouped, alpha)
    one_way_p_animal = calc_anova(animal_stats_grouped, stats, alpha)

    return normal, non_normal, one_way_p_animal


def compare_step_cycles(step_table_fp, alpha):
    """ Compares 2+ groups based on step cycle level data """
    step_table = pd.read_csv(step_table_fp)
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type'])
    selected_stats = get_numeric_col_names() #gets names of the columns that it makes sense to run these tests on

    standardized_residuals = standardize_residuals(step_table_grouped, selected_stats)

    #calculate normalcy of residuals
    normal_stats, non_normal_stats = shapiro_and_k(standardized_residuals, alpha)

    #homogeneity of variance: one way p
    one_way_p = calc_anova(step_table_grouped, selected_stats, alpha)

    return normal_stats, non_normal_stats, one_way_p


def save(fp, normal, non_normal, anova, name):
    if name != "":
        name += "_"

    save_location = os.path.join(os.path.split(fp)[0], 'group_results')
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    normal_save_name = os.path.join(save_location, f'{name}normal_stats.csv')
    non_normal_save_name = os.path.join(save_location, f'{name}non_normal_stats.csv')
    anova_save_name = os.path.join(save_location, f'{name}ANOVA_results.csv')

    normal.to_csv(normal_save_name)
    non_normal.to_csv(non_normal_save_name)
    anova.to_csv(anova_save_name)

    print(f'saved to: {save_location}')


def main():
    alpha = 0.05

    #by animal
    animal_stats_fp = 'Sample_data/animal_avg_&_stdv.csv'
    normal_animal, non_normal_animal, anova_animal = compare_animal_means(animal_stats_fp, alpha)
    save(animal_stats_fp, normal_animal, non_normal_animal, anova_animal, "animal")

    #by step cycle
    step_table_fp = 'Sample_data/step_table.csv'
    normal_stats, non_normal_stats, one_way_p = compare_step_cycles(step_table_fp, alpha)
    save(step_table_fp, normal_stats, non_normal_stats, one_way_p, "")

    return

if __name__ == "__main__":
    main()