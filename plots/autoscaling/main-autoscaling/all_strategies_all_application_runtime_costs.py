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


def plot_combined_all_costs_stacked():
    fig, ax = plt.subplots(figsize=(6.5, 5))

    lammps_runtime_no_hpa = 8.62
    lammps_runtime_staic_16 = 7.85
    lammps_runtime_staic_32 = 8.32
    lammps_runtime_staic_64 = 9.96
    lammps_runtime_hpa_80 = 10.68
    lammps_runtime_semi_auto = 15.32

    amg_runtime_no_hpa = 8.15
    amg_runtime_staic_16 = 8.29
    amg_runtime_staic_32 = 8.32
    amg_runtime_staic_64 = 9.9
    amg_runtime_hpa_80 = 10.2
    amg_runtime_semi_auto = 11.55

    kripke_runtime_no_hpa = 9.59
    kripke_runtime_staic_16 = 9.6
    kripke_runtime_staic_32 = 9.65
    kripke_runtime_staic_64 = 11.54
    kripke_runtime_hpa_80 = 11.92
    kripke_runtime_semi_auto = 13.8

    laghos_runtime_no_hpa = 13.42
    laghos_runtime_staic_16 = 11.23
    laghos_runtime_staic_32 = 12.75
    laghos_runtime_staic_64 = 13.00
    laghos_runtime_hpa_80 = 18.05
    laghos_runtime_semi_auto = 17.9

    app_setup_no_hpa = 4.07
    app_setup_staic_16 = 8.62
    app_setup_staic_32 = 15.75
    app_setup_staic_64 = 33.12
    app_setup_hpa_80 = 4.07
    app_setup_semi_auto = 4.07

    modes = ['S8',
             'S16',
             'S32',
             'S64',
             'F',
             'W']

    lammps_runtime = [lammps_runtime_no_hpa,
                      lammps_runtime_staic_16,
                      lammps_runtime_staic_32,
                      lammps_runtime_staic_64,
                      lammps_runtime_hpa_80,
                      lammps_runtime_semi_auto]
    amg_runtime = [amg_runtime_no_hpa,
                   amg_runtime_staic_16,
                   amg_runtime_staic_32,
                   amg_runtime_staic_64,
                   amg_runtime_hpa_80,
                   amg_runtime_semi_auto]
    kripke_runtime = [kripke_runtime_no_hpa,
                   kripke_runtime_staic_16,
                   kripke_runtime_staic_32,
                   kripke_runtime_staic_64,
                   kripke_runtime_hpa_80,
                   kripke_runtime_semi_auto]
    laghos_runtime = [laghos_runtime_no_hpa,
                   laghos_runtime_staic_16,
                   laghos_runtime_staic_32,
                   laghos_runtime_staic_64,
                   laghos_runtime_hpa_80,
                   laghos_runtime_semi_auto]
    app_setup = [app_setup_no_hpa,
                    app_setup_staic_16,
                    app_setup_staic_32,
                    app_setup_staic_64,
                    app_setup_hpa_80,
                    app_setup_semi_auto]

    bar_width = 0.2
    epsilon = 0.015
    line_width = 1
    opacity = 0.7
    lammps_bar_positions = np.arange(6)
    amg_bar_positions = lammps_bar_positions + bar_width
    kripke_bar_positions = amg_bar_positions + bar_width
    laghos_bar_positions = kripke_bar_positions + bar_width

    # colors = ["#DB504A", "#084C61", "#E3B505", "#4F6D7A", "#AD2831", "#B7C4CF"]
    plt.bar(lammps_bar_positions, lammps_runtime, bar_width, label="LAMMPS Runtime", color='#DB504A')
    plt.bar(lammps_bar_positions, app_setup, bar_width - epsilon, bottom=lammps_runtime,
            hatch='//', label='LAMMPS Non-Runtime')

    plt.bar(amg_bar_positions, amg_runtime, bar_width, label='AMG Runtime', color="#084C61")
    plt.bar(amg_bar_positions, app_setup, bar_width - epsilon, bottom=amg_runtime, hatch='//', label='AMG Non-Runtime')

    plt.bar(kripke_bar_positions, kripke_runtime, bar_width, label='Kripke Runtime', color="#E3B505")
    plt.bar(kripke_bar_positions, app_setup, bar_width - epsilon, bottom=kripke_runtime, hatch='//', label='Kripke Non-Runtime')

    plt.bar(laghos_bar_positions, laghos_runtime, bar_width, label='Laghos Runtime', color="#4F6D7A")
    plt.bar(laghos_bar_positions, app_setup, bar_width - epsilon, bottom=laghos_runtime, hatch='//', label='Laghos Non-Runtime')

    plt.xticks((lammps_bar_positions + amg_bar_positions + kripke_bar_positions + laghos_bar_positions) / 4, modes)
    plt.xlabel("Autoscaling Strategies")
    plt.ylabel('Cost ($)')
    plt.legend(frameon=False)
    plt.ylim(0, 61)
    plt.yticks(np.arange(0, 61, 10))
    plt.legend(loc='upper left', frameon=False, handlelength=1, handletextpad=0.3, labelspacing=0.1,
               borderaxespad=0.1, prop={'size': 16})
    # sns.despine()
    plt.tight_layout(pad=0.0, h_pad=0.0, w_pad=0.0)
    plt.savefig("combined_apps_fixed_ensemble_total_costs_in_modes_stacked.pdf", bbox_inches='tight')
    plt.show()


plot_combined_all_costs_stacked()
