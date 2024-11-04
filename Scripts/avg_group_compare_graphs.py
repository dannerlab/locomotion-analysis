"""
Creates boxplots or bar charts to compare kinematic markers between groups based on averages like Han's data
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import IPython
from useful_imports import get_rc_params

rc_params = get_rc_params()
plt.rcParams.update(rc_params)

def set_ylim(stat):

    ylims = {
        'duration': (0, 0.5, 0, 0.15),
        'duty-factor': (0, 1, 0, 0.1), #wants to be up to .75 for both
        'x-excursion': (0, 55, 0, 10),
        'y-excursion': (0, 20, 0, 3),
         }

    specific_ylims = { #default values
                 'ymin_avg': None,
                 'ymax_avg': None,
                 'ymin_stdv': None,
                 'ymax_stdv': None}
    for key in ylims.keys():  #I only commented this whole section out for testing purposes
        if key in stat:#if the stat has specified ylims
            if len(ylims.get(key)) == 4: #if stdv and avg are both specified
                ymin_avg, ymax_avg, ymin_stdv, ymax_stdv = ylims.get(key)
                specific_ylims = {
                    'ymin_avg': ymin_avg,
                    'ymax_avg': ymax_avg,
                    'ymin_stdv': ymin_stdv,
                    'ymax_stdv': ymax_stdv
                }
                break
            elif len(ylims.get(key)) == 2: #if no stdv values are specified
                ymin_avg, ymax_avg = ylims.get(key)
                specific_ylims = {
                    'ymin_avg': ymin_avg,
                    'ymax_avg': ymax_avg,
                    'ymin_stdv': None,
                    'ymax_stdv': None
                }
                break

    return specific_ylims

def graph_stat(avg_table_path, stat, stat_type):
    avg_table = pd.read_csv(avg_table_path)
    avg_table_grouped = avg_table.groupby(['mouse-type', 'exp-type'])

    #make nice table for plotting from
    plot_data = []
    for group_name, group_df in avg_table_grouped:
        group_label = group_name[0] + '_' + group_name[1]
        for value in group_df[f'{stat_type}-{stat}']:
            plot_data.append({'Group': group_label, 'Value': value})
    plot_df = pd.DataFrame(plot_data)
    plot_df['Group'] = pd.Categorical(plot_df['Group'], categories = ['WT_Levelwalk', 'V3Off_Levelwalk'], ordered = True) #alter for more groups

    palette = {'WT_Levelwalk': 'blue', 'V3Off_Levelwalk': 'red'} #alter for more groups
    plt.figure(figsize=(10, 6))
    #actually plot
    sns.boxplot(x = 'Group', y = 'Value', data = plot_df, hue = 'Group', palette = palette)
    sns.stripplot(x = 'Group', y = 'Value', data = plot_df, color = 'black', jitter = 0.2, size = 2.5)
    plt.title(f'{stat}-{stat_type}')
    ylim_dict = set_ylim(stat)
    ymin_type = ylim_dict[f'ymin_{stat_type}']
    ymax_type = ylim_dict[f'ymax_{stat_type}']
    plt.ylim(ymin_type, ymax_type)


    #save plot
    save_name = f'{stat}_boxplot_{stat_type}.png'
    save_path = os.path.join(os.path.dirname(avg_table_path), 'group_results', 'avg_graphs')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    plt.savefig(os.path.join(save_path, save_name))
    plt.clf()

def main(main_dir):
    print('running avg_group_compare_graphs.py')
    avg_table_path = f'{main_dir}/animal_avg_&_stdv.csv'
    #step_table = pd.read_csv('step_table.csv')
    stats = ['stance-duration', 'swing-duration', 'step-duration',
            'step-ToeTip_x-excursion', 'step-ToeTip_y-excursion',
            'step-ToeTip_x-max', 'step-ToeTip_x-min',
            'step-IliacCrest_y-excursion',
            'duty-factor'] 
            #add more stats, should match column labels for animal_avg_and_stdv.csv without the 'avg'/ 'stdv' prefix
            #advised to augment the y limits dictionary at top of script when you add more stats
    stat_types = ['avg', 'stdv']

    for stat_type in stat_types:
        for stat in stats:
            graph_stat(avg_table_path, stat, stat_type)
    print(f'saved to: {main_dir}/group_results/avg_graphs')
    return

if __name__ == "__main__":
    main('Full_data')


#need labels
#need to set axis limits
#need title
#should figure out sem/error bars