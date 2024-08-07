import json
import datetime
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
colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831", "#B7C4CF"]
colors2 = ["#B7C4CF", "#DB504A"]
sns.set_palette(sns.color_palette(colors))


def plot_experiment_setup_costs():
    fig, ax = plt.subplots(figsize=(6.5, 5))

    s8_non_runtime = 4.07
    s16_non_runtime = 8.62
    s32_non_runtime = 15.75
    s64_non_runtime = 33.12
    fully_automatic_non_runtime = 4.07
    workload_driven_non_runtime = 4.07

    modes = ['S8', 'S16', 'S32', 'S64', 'F', 'W']
    costs = [s8_non_runtime,s16_non_runtime, s32_non_runtime, s64_non_runtime, fully_automatic_non_runtime , workload_driven_non_runtime]

    barplot = sns.barplot(x=modes, y=costs, width=0.5, color='#8856a7')

    barplot.set(xlabel="Autoscaling Strategies")
    barplot.set(ylabel='Cost ($)')
    plt.ylim(0, 40)
    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("total_cost_of_creating_and_setting_up_experiment.pdf", bbox_inches='tight')
    plt.show()


plot_experiment_setup_costs()
