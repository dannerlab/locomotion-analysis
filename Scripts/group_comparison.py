"""
uses animal_avg & stdv to compare 2 groups
"""
import pandas as pd
from statsmodels.formula.api import ols
import statsmodels.api as sm
import os
import IPython

def compare_groups(animal_stats_fp):
    animal_stats = pd.read_csv(animal_stats_fp)
    animal_stats_grouped = animal_stats.groupby(['mouse-type', 'exp-type'])
    stats = animal_stats.filter(like='avg-').columns
    group_names = list(animal_stats_grouped.groups.keys())

    results_df = pd.DataFrame()
    for stat in stats:
        independent_vars = ['mouse-type', 'exp-type']
        dependent_var = stat
        model = ols(f"animal_stats['{stat}'] ~ C(animal_stats[independent_vars[0]])", data=animal_stats).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        anova_series = anova_table.stack()
        anova_series.name = stat
        results_df = results_df._append(anova_series)
        #print(f"ANOVA results for {stat}:\n", anova_table)

    return results_df

def filter_significance(results_df, alpha=float):
    filtered_results = results_df.where(results_df['C(animal_stats[independent_vars[0]])']['PR(>F)'] < alpha).dropna()
    return filtered_results

def main():
    animal_stats_fp = 'Sample_data/animal_avg_&_stdv.csv'
    results = compare_groups(animal_stats_fp)
    sig_results = filter_significance(results, alpha=0.05)
    save_name = os.path.join(os.path.split(animal_stats_fp)[0],'ANOVA_results.csv')
    sig_results.to_csv(save_name)
    print(f'saved to: {save_name}')

    return

if __name__ == "__main__":
    main()