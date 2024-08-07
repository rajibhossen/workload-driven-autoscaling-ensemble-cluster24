import math

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
colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831"]
colors2 = ["#B7C4CF", "#DB504A"]
sns.set_palette(sns.color_palette(colors))


def plot_variable_hpa():
    fig, ax = plt.subplots(figsize=(10, 6))

    data = pd.read_csv('../../../datasets/horizontal-pod-autoscaling-simulation/hpa-simulation-data.csv')
    data['desired_replicas'] = data['desired_replicas'] - 8
    converged_data = data.groupby('desired_metric_value')['desired_replicas'].mean().apply(np.ceil)
    sns.scatterplot(data=converged_data, s=100)

    plt.xlabel('Desired Utilization Threshold')
    plt.ylabel('New Replica Count')
    plt.xlim(49.5, 101)
    plt.ylim(-0.2, 8.1)
    plt.yticks(np.arange(0, 8.1, 2))

    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("hpa_variable_metrics.pdf", bbox_inches='tight')
    plt.show()


plot_variable_hpa()
