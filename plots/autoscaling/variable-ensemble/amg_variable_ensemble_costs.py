import json
import datetime
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import seaborn.objects as so

font = {'family': 'Palatino Linotype',
        'weight': 'bold',
        'size': 24}

matplotlib.rc('font', **font)
sns.set_style('darkgrid')
colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831", "#B7C4CF"]
colors2 = ["#B7C4CF", "#DB504A"]
sns.set_palette(sns.color_palette(colors))


def plot_variable_ensemble_combines_all_costs_stacked():
    plt.figure(figsize=(10, 6))

    s8_cost = 4.9
    s16_cost = 4.84
    s32_cost = 5.09
    s64_cost = 5.95
    full_auto_cost = 6.05
    workload_driven_cost = 8.05

    s8_non_runtime_cost = 4.07
    s16_non_runtime_cost = 8.62
    s32_non_runtime_cost = 15.74
    s64_non_runtime_cost = 33.12
    fully_auto_non_runtime_cost = 4.07
    workload_driven_non_runtime_cost = 4.07

    df = pd.DataFrame({
        'modes': ['S8', 'S16', 'S32', 'S64', 'F', 'W'],
        'Runtime': [s8_cost, s16_cost, s32_cost, s64_cost, full_auto_cost, workload_driven_cost],
        'Non-Runtime': [s8_non_runtime_cost, s16_non_runtime_cost, s32_non_runtime_cost, s64_non_runtime_cost,
                        fully_auto_non_runtime_cost,
                        workload_driven_non_runtime_cost]
    })
    df.set_index('modes').plot(kind='bar', stacked=True, rot=0,
                               color=["#084C61", "#8856a7", "#E3B505", "#4F6D7A", "#AD2831", "#B7C4CF"],
                               figsize=(5, 4), fontsize=22)
    plt.xlabel("Autoscaling Strategies")
    plt.ylabel("Cost ($)")

    plt.ylim(0, 50)
    plt.yticks(np.arange(0, 51, 10))

    plt.legend(loc='upper left', prop={'size': 20}, frameon=False, handlelength=1, handletextpad=0.2, labelspacing=0.2,
               borderaxespad=0.2)
    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("amg_variable_ensemble_runtime_costs_in_modes_stacked.pdf", bbox_inches='tight')
    plt.show()


plot_variable_ensemble_combines_all_costs_stacked()
