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


def plot_amg_large_ensemble_end_to_end_runtime():
    fig, ax = plt.subplots(figsize=(5, 4))

    run_mode = ['S8', 'S16', 'S32', 'S64', 'F', 'W']
    timings = [10950.55, 5474.91, 2745.27, 1405.6, 10891.5, 2045.3]
    timings = [x / 60 for x in timings]
    barplot = sns.barplot(x=run_mode, y=timings, width=0.5, color='#084C61')

    barplot.set_xticklabels(run_mode, size=22)
    barplot.set(xlabel="Autoscaling Strategies")
    barplot.set(ylabel='Time (m)')
    plt.ylim(0, 200)
    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("amg_large_ensemble_end_to_end_comparison.pdf", bbox_inches='tight')
    plt.show()


# plot_amg_large_ensemble_end_to_end_runtime()
