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

def get_median():
    df = pd.read_csv("../../../datasets/autoscaling-studies/variable-ensemble/all-strategies-amg-runtime.csv")
    print(df.groupby('strategy')['runtime'].median())


def plot_amg_variable_ensemble_end_to_end_runtime():
    fig, ax = plt.subplots(figsize=(5, 4))

    run_mode = ['S8', 'S16', 'S32', 'S64', 'F', 'W']
    timings = [1310.63, 646.80, 340.38, 198.87, 1303, 383.97]

    barplot = sns.barplot(x=run_mode, y=timings, width=0.5, color='#084C61')

    barplot.set_xticklabels(run_mode, size=22)
    barplot.set(xlabel="Autoscaling Strategies")
    barplot.set(ylabel='Time (s)')
    plt.ylim(0, 1501)
    plt.yticks(np.arange(0, 1501, 300))

    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("figures/amg_variable_ensemble_end_to_end_comparison.pdf", bbox_inches='tight')
    plt.show()

get_median()
#plot_amg_variable_ensemble_end_to_end_runtime()
