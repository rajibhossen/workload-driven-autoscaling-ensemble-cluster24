import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

font = {'family': 'Palatino Linotype',
        'weight': 'bold',
        'size': 24}

matplotlib.rc('font', **font)
sns.set_style('darkgrid')
colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831", '#B7C4CF']
colors2 = ["#B7C4CF", "#DB504A"]
sns.set_palette(sns.color_palette(colors))


def plot_applications_end_to_end_overall():
    fig, ax = plt.subplots(figsize=(6.5, 5))

    raw_data = {
        'x': ['S8', 'S8', 'S8', 'S8',
              'S16', 'S16', 'S16', 'S16',
              'S32', 'S32', 'S32', 'S32',
              'S64', 'S64', 'S64', 'S64',
              'F', 'F', 'F', 'F',
              'W', 'W', 'W', 'W'],
        'y': [2302.84, 2186.12, 2563.31, 3587.63,
              1050, 1108.43, 1282.96, 1500.62,
              556, 556.03, 645.02, 852.32,
              333, 330.75, 385.77, 434.53,
              2295.29, 2189.13, 2559.71, 3870.25,
              707.97, 539.58, 640.3, 823.03],
        'category': ['LAMMPS', 'AMG', 'Kripke', 'Laghos'] * 6
    }
    barplot = sns.barplot(x='x', y='y', hue='category', data=raw_data)

    barplot.set(xlabel="Autoscaling Strategies")
    barplot.set(ylabel='Time (s)')
    # plt.xlim(49, 101)
    plt.ylim(0, 4001)
    plt.yticks(np.arange(0, 4001, 500))
    plt.legend(loc='upper center', frameon=False, handlelength=1, handletextpad=0.3, labelspacing=0.1,
               borderaxespad=0.1)

    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("combined_apps_fixed_ensemble_runtime_in_modes.pdf", bbox_inches='tight')
    plt.show()


plot_applications_end_to_end_overall()
