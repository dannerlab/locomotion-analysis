"""
Creates boxplots or bar charts to compare kinematic markers between groups based on averages like Han's data
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import IPython

def graph_stat(avg_table_path, stat):
    avg_table = pd.read_csv(avg_table_path)
    avg_table_grouped = avg_table.groupby(['mouse-type', 'exp-type'])
    
    #make nice table for plotting from
    plot_data = []
    for group_name, group_df in avg_table_grouped:
        group_label = group_name[0] + '_' + group_name[1]
        for value in group_df[f'avg-{stat}']:
            plot_data.append({'Group': group_label, 'Value': value})
    plot_df = pd.DataFrame(plot_data)

    palette = {'WT_Levelwalk': 'blue', 'V3Off_Levelwalk': 'red'}
    #actually plot
    sns.boxplot(x = 'Group', y = 'Value', data = plot_df, hue = 'Group', palette = palette)
    sns.stripplot(x = 'Group', y = 'Value', data = plot_df, color = 'black', jitter = 0.2, size = 2.5)
    plt.title(f'{stat}')


    #save plot
    save_name = f'{stat}_boxplot_avg.png'
    save_path = os.path.join(os.path.dirname(avg_table_path), 'group_results', 'avg_graphs')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    plt.savefig(os.path.join(save_path, save_name))
    plt.clf()

def main():
    avg_table_path = 'Sample_data/animal_avg_&_stdv.csv'
    #step_table = pd.read_csv('step_table.csv')
    stats = ['stance-duration', 'swing-duration', 
            'step-ToeTip_x-excursion', 'step-ToeTip_y-excursion', 
            'step-IliacCrest_y-excursion', 'duty-factor'] #add more stats, should match column labels for animal_avg_and_stdv.csv without the 'avg'/ 'stdv' prefix
    for stat in stats:
        graph_stat(avg_table_path, stat)
    return

if __name__ == "__main__":
    main()


#need labels
#need to set axis limits
#need title
#should figure out sem/error bars