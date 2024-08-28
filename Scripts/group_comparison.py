"""
uses animal_avg & stdv to compare 2 groups via ANOVA
needs filtering still
"""

import pandas as pd
from statsmodels.formula.api import ols
import statsmodels.api as sm
import os
import IPython
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

def compare_groups_means(animal_stats_fp):
    animal_stats = pd.read_csv(animal_stats_fp)
    animal_stats_grouped = animal_stats.groupby(['mouse-type', 'exp-type'])
    stats = animal_stats.filter(like='avg-').columns
    group_names = list(animal_stats_grouped.groups.keys())

    results_df = pd.DataFrame()
    for stat in stats:
        independent_vars = ['mouse-type', 'exp-type']
        dependent_var = stat
        #test normal distribution (shapiro-wilkes & KGsmirnov)

        #if fail that run other tests
        model = ols(f"animal_stats['{stat}'] ~ C(animal_stats[independent_vars[0]])", data=animal_stats).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        anova_series = anova_table.stack()
        anova_series.name = stat
        results_df = results_df._append(anova_series)
        #print(f"ANOVA results for {stat}:\n", anova_table)

    return results_df

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

def compare_groups(step_table_fp, alpha):
    step_table = pd.read_csv(step_table_fp)
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type'])
    selected_stats = get_numeric_col_names() #gets names of the columns that it makes sense to run these tests on

    standardized_residuals = standardize_residuals(step_table_grouped, selected_stats)

    #calculate normalcy of residuals
    normal_stats, non_normal_stats = shapiro_and_k(standardized_residuals, alpha)

    #homogeneity of variance: one way p
    one_way_p = calc_anova(step_table_grouped, selected_stats, alpha)

    return normal_stats, non_normal_stats, one_way_p


def main():
    animal_stats_fp = 'Sample_data/animal_avg_&_stdv.csv' #should use step_table.csv
    mean_results = compare_groups_means(animal_stats_fp)
    step_table_fp = 'Sample_data/step_table.csv'
    alpha = 0.05

    normal_stats, non_normal_stats, one_way_p = compare_groups(step_table_fp, alpha)

    save_location = os.path.split(animal_stats_fp)[0]

    normal_save_name = os.path.join(save_location, 'normal_stats.csv')
    normal_stats.to_csv(normal_save_name)
    non_normal_save_name = os.path.join(save_location, 'non_normal_stats.csv')
    non_normal_stats.to_csv(non_normal_save_name)

    anova_save_name = os.path.join(save_location,'ANOVA_results.csv')
    one_way_p.to_csv(anova_save_name)

    print(f'saved to: {save_location}')

    return

if __name__ == "__main__":
    main()