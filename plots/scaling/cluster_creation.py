import json

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
import csv

font = {'family': 'Palatino Linotype',
        'weight': 'bold',
        'size': 24}

matplotlib.rc('font', **font)
sns.set_style('darkgrid')
colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831"]
colors2 = ["#B7C4CF", "#DB504A"]
sns.set_palette(sns.color_palette(colors))


def plot_cluster_creation_merged():
    fig, ax = plt.subplots(figsize=(5, 4))

    data = pd.read_csv('../../datasets/scaling/cluster_creation_components.csv')
    boxplot = sns.boxplot(x='components', y='time(s)', data=data)

    boxplot.set(xlabel='Creation Operations')
    boxplot.set(ylabel='Time (s)')
    boxplot.set(xticklabels=['VPC', 'W', 'C', 'Total'])
    plt.ylim(0, 1200)
    plt.yticks(np.arange(0, 1201, 200))
    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("kubescaler_cluster_creation_merged.pdf", bbox_inches='tight')
    plt.show()


plot_cluster_creation_merged()

