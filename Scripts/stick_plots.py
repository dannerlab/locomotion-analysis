'''
plots kinematics from H5 files as stick diagrams
saves them  as pngs
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import os
import IPython
from useful_imports import import_kinematics

rc_params = {
        "figure.constrained_layout.use": False,
        "figure.figsize": (6.75, 1.0),
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
plt.rcParams.update(rc_params)

def plot_diagram(trial, main_dir):
    """generates stick diagram figure (one trial)"""
    fig, axs = plt.subplots()

    stance_start_indices = trial['stance-start-idx']
    stance_stop_indices = trial['stance-stop-idx']
    start_index = stance_start_indices.iloc[0]
    stop_index = stance_stop_indices.iloc[-1]
    
    #import h5 details
    h5_table = import_kinematics(trial['source-data-h5-path'].iloc[0])
    
    #x calculations
    treadmil_speed = 150#trial['belt-speed'].iloc[0] * 10             # mm/s
    sampling_freq = 200               # Hz
    nsamples = len(h5_table)
    time_vec = np.linspace(0.0, nsamples/sampling_freq, nsamples)
    distance_x = time_vec*treadmil_speed

    xpos = np.vstack(
        (
            h5_table['IliacCrest_x'].T,
            h5_table['Hip_x'].T,
            h5_table['Knee_x'].T,
            h5_table['Ankle_x'].T,
            h5_table['Metatarsal_x'].T,
            h5_table['ToeTip_x'].T,
        )
    ) + distance_x
    
    ypos = np.vstack(
        (
            h5_table['IliacCrest_y'].T,
            h5_table['Hip_y'].T,
            h5_table['Knee_y'].T,
            h5_table['Ankle_y'].T,
            h5_table['Metatarsal_y'].T,
            h5_table['ToeTip_y'].T,
        )
    )

    n_skips = 2 # skip every n_skips frames
    
    xpos = xpos[:, start_index:stop_index:n_skips]
    ypos = ypos[:, start_index:stop_index:n_skips]

    # determine color
    if trial['mouse-type'].iloc[0] == 'WT':
        stance_color = 'blue'
    elif trial['mouse-type'].iloc[0] == 'V3Off':
        stance_color = 'red'
    else:
        stance_color = (0.00784313725490196, 0.6196078431372549, 0.45098039215686275)

    #Plots lines
    lines = axs.plot(xpos, ypos, linewidth=0.5, alpha=0.75, color = 'black')

    # Change colors for stance phase
    for start, end in zip(stance_start_indices, stance_stop_indices):
        for num in range(start, end):
            lines[(num//n_skips) - ((start_index//n_skips) + 1)].set_color(stance_color)

    #Plots joints
    axs.scatter(
        xpos, ypos,
        s=0.1, marker='o', alpha=0.25, color='black', facecolor='black'
    )
    trajectory_color = (0.8352941176470589, 0.3686274509803922, 0.0)
    axs.plot(
        xpos[-1, :],
        ypos[-1, :],
        "--",
        color=trajectory_color,
        linewidth=0.75,
    )

    axs.set_xticklabels([])
    axs.set_xticks([])
    axs.set_yticklabels([])
    axs.set_yticks([])
    axs.spines["left"].set_visible(False)
    axs.spines["bottom"].set_visible(True)
    axs.set_aspect("equal", "box")

    scalebar_h = AnchoredSizeBar(
        axs.transData,
        50,
        r"50 mm",
        loc="lower left",
        pad=0.0,
        borderpad=0.0,
        sep=5,
        frameon=False,
        fontproperties={'size': 'small', 'style': 'italic'},
        bbox_transform=axs.transAxes,  # Use axes coordinates for positioning
        bbox_to_anchor=(0.05, -0.5),  # Adjust the position relative to axes max(distance_x)*-1e-3
    )
    axs.add_artist(scalebar_h)
    save_location = f'{main_dir}/stick_diagrams'
    if not os.path.exists(save_location):
        os.makedirs(save_location)
    save_name = f"stick_diagram_{trial['mouse-type'].iloc[0]}_{trial['exp-type'].iloc[0]}_{trial['mouse-id'].iloc[0]}_{trial['trial-number'].iloc[0]}.png"
    plt.savefig(os.path.join(save_location, save_name))
    plt.close()

def main(main_dir):
    print('running stick_plots.py')
    step_table = pd.read_csv(f"{main_dir}/step_table.csv")
    step_table_grouped = step_table.groupby(['mouse-type', 'exp-type', 'mouse-id', 'trial-number'])
    for trial_i, (name, trial) in enumerate(step_table_grouped):
        trial_name = "_".join(str(item) for item in name)
        plot_diagram(trial, main_dir)
    print(f'saved to: {main_dir}/stick_diagrams')



if __name__ == "__main__":
    main('Full_data')
