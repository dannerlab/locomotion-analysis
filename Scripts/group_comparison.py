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
from useful_imports import get_numeric_col_names, exclude_trials
import IPython

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
                normal_stats[key] = [shapiro_non_normal[key], k_normal[key]]
        else:
            normal_stats[key] = [shapiro_normal[key], k_normal[key]]

    #convert to dict
    rows = normal_stats.keys()
    columns = ['stat', 'shapiro_p', 'kolmogorov-smirnov_p']
    normal_stats_dict = {columns[0]: rows,
            columns[1]: [normal_stats[row][0] for row in rows],
            columns[2]: [normal_stats[row][1] for row in rows]}
    normal_stats_df = pd.DataFrame(normal_stats_dict)

    rows = non_normal_stats.keys()
    non_normal_stats_dict = {columns[0]: rows,
            columns[1]: [non_normal_stats[row][0] for row in rows],
            columns[2]: [non_normal_stats[row][1] for row in rows]}
    non_normal_stats_df = pd.DataFrame(non_normal_stats_dict)

    return normal_stats_df, non_normal_stats_df


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

def calc_ttest(step_table_grouped, selected_stats, alpha): 
    '''Runs t-test on all stats passed to it (only pass normal), returns df of p-values'''

    t_test_p = {}

    for key in selected_stats['stat']:#iterate through list of stats that we have chosen to run these tests on
        group_stats = [] #list of selected columns (via key) for each group
        for group_name, group in step_table_grouped:
            group_stats.append(group[key])
        
        # #test for variance, comment out to match Han's but should optimally implement to run Welch's test instead of Ttest where appropriate
        # levene_stat, levene_p = stats.levene(*(group_stats))
        equal_var = True
        # if levene_p <= alpha: #variances are significantly different
        #     equal_var = False
        
        #run t-test
        t_stat, p_val = stats.ttest_ind(group_stats[0], group_stats[1], equal_var=equal_var)
        if p_val <= alpha: #filter for significance
            t_test_p[key] = p_val
        

    #format for nicer saving
    t_test_p = pd.Series(t_test_p.values(),index=t_test_p.keys()).to_frame()
    t_test_p = t_test_p.rename(columns = {0: 't_test_p_value'})
    
    return t_test_p

def calc_wilcoxon(step_table_grouped, selected_stats, alpha):
    '''Runs wilcoxon on all stats passed to it (only pass non-normal), returns df of p-values'''

    wilcoxon_p = {}

    for key in selected_stats['stat']:
        group_stats = [] #list of selected columns (via key) for each group
        for group_name, group in step_table_grouped:
            group_stats.append(group[key])
        wilcoxon_stat, p_val = stats.wilcoxon((group_stats[0], group_stats[1]))
        if p_val <= alpha: #filter for significance
            wilcoxon_p[key] = p_val

    #format for nicer saving
    wilcoxon_p = pd.Series(wilcoxon_p.values(),index=wilcoxon_p.keys()).to_frame()
    wilcoxon_p = wilcoxon_p.rename(columns = {0: 'wilcoxon_p_value'})
    
    return wilcoxon_p

def compare_animal_means(animal_stats_fp, alpha, compare_groups):
    '''Runs stats on avgs of each animal (Han style)'''
    animal_stats_unfiltered = pd.read_csv(animal_stats_fp)

    animal_stats_list = []
    for group in compare_groups: #create list containing 2 dfs, 1 for each group
        animal_stats_group =  animal_stats_unfiltered[
            (animal_stats_unfiltered['mouse-type'] == group[0]) &
            (animal_stats_unfiltered['exp-type'] == group[1])]
        animal_stats_list.append(animal_stats_group)
    
    animal_stats = pd.concat(animal_stats_list)
    
    animal_stats_grouped = animal_stats.groupby(['mouse-type', 'exp-type'])
    list_of_stats = animal_stats_unfiltered.filter(like='avg-').columns
    #since col names for avgs all begin with avg, cannot use get_numeric_col_names()
    #that is ok because get_numeric_col_names() is used to generate this table so re-running will update here also

    standardized_animal_grouped = standardize_residuals(animal_stats_grouped, list_of_stats)
    normal, non_normal = shapiro_and_k(standardized_animal_grouped, alpha)

    one_way_p_animal = calc_anova(animal_stats_grouped, list_of_stats, alpha)
    ttest_vals = calc_ttest(animal_stats_grouped, normal, alpha)
    wilcoxon_vals = calc_wilcoxon(animal_stats_grouped, non_normal, alpha)

    return normal, non_normal, one_way_p_animal, ttest_vals, wilcoxon_vals


def save(fp, normal, non_normal, anova, ttest_vals, wilcoxon_vals, name, compare_groups):
    if name != "":
        name += "_"

    save_location = os.path.join(os.path.split(fp)[0], 'group_results')
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    groups_name = '_'.join([f'{group[0]}_{group[1]}' for group in compare_groups])
    normal_save_name = os.path.join(save_location, f'{name}normal_stats_{groups_name}.csv')
    non_normal_save_name = os.path.join(save_location, f'{name}non_normal_stats_{groups_name}.csv')
    anova_save_name = os.path.join(save_location, f'{name}ANOVA_results_{groups_name}.csv')
    ttest_save_name = os.path.join(save_location, f'{name}ttest_results_{groups_name}.csv')
    wilcoxon_save_name = os.path.join(save_location, f'{name}wilcoxon_results_{groups_name}.csv')

    normal.to_csv(normal_save_name)
    non_normal.to_csv(non_normal_save_name)
    anova.to_csv(anova_save_name)
    ttest_vals.to_csv(ttest_save_name)
    wilcoxon_vals.to_csv(wilcoxon_save_name)

    print(f'saved to: {save_location}')


def main(main_dir, compare_groups):
    print('running group_comparison.py')
    alpha = 0.05

    #by animal
    animal_stats_fp = f'{main_dir}/animal_avg_&_stdv.csv' #already filtered by whatever was used in animal_avgs.py
    normal_animal, non_normal_animal, anova_animal, ttest_vals, wilcoxon_vals = compare_animal_means(animal_stats_fp, alpha, compare_groups)
    save(animal_stats_fp, normal_animal, non_normal_animal, anova_animal, ttest_vals, wilcoxon_vals, "animal", compare_groups)

    return

if __name__ == "__main__":
    main(main_dir="Selected_data", compare_groups=[('WT', 'Incline'), ('V3Off', 'Incline')])