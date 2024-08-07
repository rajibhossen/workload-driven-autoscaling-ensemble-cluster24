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


def hpc6a_scale_up_overall_median_lineplot():

    fig, axes = plt.subplots(ncols=2, width_ratios=[2, 1], figsize=(20, 6))

    data_by_4 = pd.read_csv('../../datasets/scaling/scale_out_by_increments_4.csv')
    data_by_8 = pd.read_csv('../../datasets/scaling/scale_out_by_increments_8.csv')
    data_by_16 = pd.read_csv('../../datasets/scaling/scale_out_by_increments_16.csv')

    sns.lineplot(ax=axes[0], x="scale_up", y="time", data=data_by_4, color="#084C61", marker='o', label='Scale out by 4', lw=3, ms=10)
    sns.lineplot(ax=axes[0], x="scale_up", y="time", data=data_by_8, color="#E3B505", marker='d', label='Scale out by 8', lw=3, ms=10)
    sns.lineplot(ax=axes[0], x="scale_up", y="time", data=data_by_16, color="#DB504A", marker='^', label='Scale out by 16', lw=3, ms=10)

    data_by_4_cumsum = pd.read_csv('../../datasets/scaling/scale_out_by_increments_4_median_cumulative.csv', index_col='scale_up').cumsum()
    data_by_8_cumsum = pd.read_csv('../../datasets/scaling/scale_out_by_increments_8_median_cumulative.csv', index_col='scale_up').cumsum()
    data_by_16_cumsum = pd.read_csv('../../datasets/scaling/scale_out_by_increments_16_median_cumulative.csv', index_col='scale_up').cumsum()

    sns.lineplot(ax=axes[1], x="scale_up", y="time", data=data_by_4_cumsum, color="#084C61", marker='o', label='Scale out by 4', lw=3, ms=10)
    sns.lineplot(ax=axes[1], x="scale_up", y="time", data=data_by_8_cumsum, color="#E3B505", marker='d', label='Scale out by 8', lw=3, ms=10)
    sns.lineplot(ax=axes[1], x="scale_up", y="time", data=data_by_16_cumsum, color="#DB504A", marker='^', label='Scale out by 16', lw=3, ms=10)

    axes[0].set(xlabel='Scaling Out Increments', ylabel='Time (s)')
    axes[1].set(xlabel='Scaling Out Increments', ylabel='Cumulative Time (s)')
    axes[0].set_xticks(np.arange(4, 65, 4))
    axes[1].set_xticks(np.arange(0, 65, 8))
    axes[0].set_yticks(np.arange(40, 101, 10))
    axes[1].set_yticks(np.arange(0, 801, 100))
    axes[0].set_xlim(left=3.5,right=64.5)
    axes[1].set_xlim(left=0, right=64.5)

    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("hpc6a_scale_up_overall_median_cumsum.pdf", bbox_inches='tight')
    plt.show()


hpc6a_scale_up_overall_median_lineplot()
