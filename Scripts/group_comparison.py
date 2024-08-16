"""
uses animal_avg & stdv to compare 2 groups via ANOVA
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

def compare_groups(step_table_fp):
    step_table = pd.read_csv(step_table_fp)
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type'])
    selected_stats = get_numeric_col_names() #gets names of the columns that it makes sense to run these tests on

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

    combined_residuals = combine_dicts(*residuals.values())

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

    #calculate normalcy
    residuals_shapiro = pd.DataFrame()
    residuals_k = pd.DataFrame()
    for key in standardized_residuals:
        residuals_shapiro[key] = shapiro(standardized_residuals[key])[1]
        residuals_k[key] = stats.kstest(standardized_residuals[key], 'norm')[1]

    #homogeneity of variance: one way p
    list_of_selected_groups = []
    for group, data in step_table_grouped:
        selected_data = data[selected_stats]
        list_of_selected_groups.append(selected_data)

    one_way_p = pd.DataFrame()

    for key in standardized_residuals:
        one_way_p[key] = f_oneway(*(group for group in list_of_selected_groups))[1]


    IPython.embed()
    fjdkl


    return

def filter_significance(results_df, alpha=float):
    filtered_results = results_df.where(results_df['C(animal_stats[independent_vars[0]])']['PR(>F)'] < alpha).dropna()
    return filtered_results

def main():
    animal_stats_fp = 'Sample_data/animal_avg_&_stdv.csv' #should use step_table.csv
    mean_results = compare_groups_means(animal_stats_fp)
    step_table_fp = 'Sample_data/step_table.csv'
    compare_groups(step_table_fp)

    sig_results = filter_significance(results, alpha=0.05)


    save_name = os.path.join(os.path.split(animal_stats_fp)[0],'ANOVA_results.csv')
    sig_results.to_csv(save_name)
    print(f'saved to: {save_name}')

    return

if __name__ == "__main__":
    main()