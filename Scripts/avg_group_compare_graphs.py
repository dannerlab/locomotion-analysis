"""
Creates boxplots or bar charts to compare kinematic markers between groups based on averages like Han's data
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import IPython
from useful_imports import get_rc_params, color_dict

rc_params = get_rc_params()
plt.rcParams.update(rc_params)

def set_ylim(stat):

    ylims = { #name: (ymin_avg, ymax_avg, ymin_stdv, ymax_stdv)
        'duration': (0, 0.5, 0, 0.15),
        'duty-factor': (0, 1, 0, 0.1), #wants to be up to .75 for both
        'x-excursion': (0, 55, 0, 10),
        'y-excursion': (0, 20, 0, 3),
        'Hip_to_Toe_x-max': (0, 50, 0, 10),
        'Hip_to_Toe_x-min': (-50, 0, 0, 10),
        'Hip_to_Toe_x-excursion': (0, 50, 0, 10),
        'Hip_angle-excursion': (0, 60, 0, 20),
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

def set_ylabel(stat):
    stat_labels = {'stance-duration': 'Stance Duration (s)',
                   'swing-duration': 'Swing Duration (s)',
                     'step-duration': 'Step Duration (s)',
                        'step-ToeTip_x-excursion': 'ToeTip x Excursion (mm)',
                        'step-ToeTip_y-excursion': 'ToeTip y Excursion (mm)',
                        'step-IliacCrest_y-excursion': 'IliacCrest y Excursion (mm)',
                        'duty-factor': 'Duty Factor',
                        'step-Hip_to_Toe_x-max': 'Hip to Toe x Max (mm)',
                        'step-Hip_to_Toe_x-min': 'Hip to Toe x Min (mm)',
                        'step-Hip_to_Toe_x-excursion': 'Hip to Toe x Excursion (mm)',
                        'step-Hip_angle-excursion': 'Hip Angle Excursion (degrees)',
                        'stance-Hip_angle-excursion': 'Stance Hip Angle Excursion (degrees)',
                        'swing-Hip_angle-excursion': 'Swing Hip Angle Excursion (degrees)',}
    try:
        return stat_labels[stat]
    except KeyError:  
        print(f'please add label for {stat}')
        return ""

def graph_stat(avg_table_path, stat, stat_type, compare_table_path, compare_groups):
    #read in data
    avg_table = pd.read_csv(avg_table_path)
    avg_table_grouped = avg_table.groupby(['mouse-type', 'exp-type'])
    p_values = pd.read_csv(compare_table_path, index_col = 0)

    #make nice table for plotting from
    plot_data = []
    for group_name, group_df in avg_table_grouped:
        group_label = group_name[0] + '_' + group_name[1]
        for value in group_df[f'{stat_type}-{stat}']:
            plot_data.append({'Group': group_label, 'Value': value})
    plot_df = pd.DataFrame(plot_data)
    plot_df['Group'] = pd.Categorical(plot_df['Group'], categories = compare_groups, ordered = True) #alter for more groups

    #determine significance
    significance = ''
    if stat_type == 'avg':
        if stat in p_values.index:
            p_val = p_values.loc[stat, 'ANOVA_p_value']
            if p_val < 0.001:
                significance = '***'
            elif p_val < 0.01:
                significance = '**'
            elif p_val < 0.05:
                significance = '*'
            

    palette = color_dict
    plt.figure(figsize=(10, 6))
    #actually plot
    
    sns.boxplot(x = 'Group', y = 'Value', data = plot_df, hue = 'Group', palette = palette) #if this throws an error, check if you have the color of the group specified in useful_imports
    sns.stripplot(x = 'Group', y = 'Value', data = plot_df, color = 'black', jitter = 0.2, size = 2.5)
    ylim_dict = set_ylim(stat)
    ymin_type = ylim_dict[f'ymin_{stat_type}']
    ymax_type = ylim_dict[f'ymax_{stat_type}']
    plt.text(0.5, 0.7, significance, ha = 'center', va = 'center', transform = plt.gca().transAxes)
    plt.ylim(ymin_type, ymax_type)
    plt.ylabel(set_ylabel(stat))


    #save plot
    group_name = '_'.join(compare_groups)
    save_name = f'{stat}_boxplot_{stat_type}_{group_name}.png'
    save_path = os.path.join(os.path.dirname(avg_table_path), 'group_results', 'avg_graphs')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    plt.savefig(os.path.join(save_path, save_name))
    plt.clf()
    plt.close()

def main(main_dir, compare_groups):
    print('running avg_group_compare_graphs.py')
    avg_table_path = f'{main_dir}/animal_avg_&_stdv.csv'
    compare_table_path = f'{main_dir}/group_results/animal_ANOVA_results.csv'

    stats = ['stance-duration', 'swing-duration', 'step-duration',
            'step-ToeTip_x-excursion', 'step-ToeTip_y-excursion',
            #'step-ToeTip_x-max', 'step-ToeTip_x-min',
            'step-IliacCrest_y-excursion',
            'duty-factor',
            'step-Hip_to_Toe_x-max', 'step-Hip_to_Toe_x-min', 'step-Hip_to_Toe_x-excursion',
            'step-Hip_angle-excursion', 'stance-Hip_angle-excursion', 'swing-Hip_angle-excursion',] 
            #add more stats, should match column labels for animal_avg_and_stdv.csv without the 'avg'/ 'stdv' prefix
            #advised to augment the y limits dictionary at top of script when you add more stats
            #should also augment y labels dictionary when you add a stat
    stat_types = ['avg', 'stdv']

    for stat_type in stat_types:
        for stat in stats:
            graph_stat(avg_table_path, stat, stat_type, compare_table_path, compare_groups)
    print(f'saved to: {main_dir}/group_results/avg_graphs')
    return

if __name__ == "__main__":
    main('Full_data', ['WT_Incline', 'V3Off_Incline'])



#should figure out sem/error bars