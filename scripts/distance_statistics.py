#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick
from tabulate import tabulate
import argparse

EXPERIMENTS = {
    "safety_areas": "safety_areas/Distance_Monitoring/hr_distance.csv",
    "velocity_scaling": "velocity_scaling/Distance_Monitoring/hr_distance.csv",
    "realworld_case_study": "hrc_case_study/hrc_case_study_results/Distance_Monitoring/hr_distance.csv"
}

def main():
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument('--zoom', action='store_true', help='Enable zoom in the plot')
    parser.add_argument('--latex', action='store_true', help='Add print of latex table')
    parser.add_argument("--experiment", choices=EXPERIMENTS.keys(), required=True, help="Select the experiment")

    args = parser.parse_args()
    zoom = args.zoom
    latex = args.latex
    experiment_path = EXPERIMENTS.get(args.experiment, "safety_areas")
    
    sns.set_theme()
    recipes_to_compare = ["COMPLETE_HA_SOLVER", "RELAXED_HA_SOLVER", "NOT_NEIGHBORING_SOLVER", "BASIC_SOLVER"]
    RENAME = {
        "COMPLETE_HA_SOLVER": "Synergistic TP",
        "RELAXED_HA_SOLVER": "Relaxed S. TP",
        "NOT_NEIGHBORING_SOLVER": "Not Neighboring TP",
        "BASIC_SOLVER": "Baseline TP"
    }
    RECIPE_NAME_COLUMN = "Recipe Name"
    RECIPE_TYPE_COLUMN = "Recipe Type"
    RECIPE_PERCENTAGE_COLUMN = "Percentage Under Safety Distance"
    RECIPE_S_D_TYPE_COLUMN = "Safety Distance Levels"

    risky_distances = [0.4, 0.5, 0.7, 0.8]
    distance_dataset = pd.read_csv(experiment_path)
    distance_dataset = distance_dataset.replace(np.inf, np.nan)
    distance_dataset = distance_dataset.dropna()

    max_val = 4
    fig, ax = plt.subplots(figsize=(16, 8))
    if zoom:
        ax2 = plt.axes([0.2, 0.6, .2, .2])
        ax2.set_title('Zoom in range 0-1.2 m')
        ax2.set_ylim([0, .04])
        ax2.set_xlim([0, 1.2])
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))

    percentage_under_risky_dataset = {
        RECIPE_NAME_COLUMN: [], RECIPE_TYPE_COLUMN: [], RECIPE_PERCENTAGE_COLUMN: [], RECIPE_S_D_TYPE_COLUMN: []
    }
    min_distances = dict.fromkeys(recipes_to_compare)


    for recipe_name in recipes_to_compare:
        single_recipe_type_data = distance_dataset[distance_dataset['Recipe'].str.contains(recipe_name)]
        single_recipe_type_data = single_recipe_type_data[single_recipe_type_data['Mean']<1000] # can be erased
        single_type_recipe_names = single_recipe_type_data.Recipe.unique()
        min_distances[recipe_name] = min(single_recipe_type_data["Mean"])

        cumulative_dist_recipes = []
        bin_edges_recipes = []

        min_distance = []
        max_distance = []
        delta_distance = []

        for single_recipe in single_type_recipe_names:
            single_recipe_distance_data = distance_dataset.loc[distance_dataset['Recipe'] == single_recipe]
            
            n_bins = len(single_recipe_distance_data["Mean"])
            hist, bin_edges = np.histogram(
                single_recipe_distance_data["Mean"],
                bins=n_bins,
                range=(np.nanmin(single_recipe_distance_data["Mean"]), np.nanmax(max_val))
            )

            cumulative_dist_recipes.append(np.cumsum(hist) / float(n_bins))
            bin_edges_recipes.append(bin_edges)
            min_distance.append(min(bin_edges))
            max_distance.append(max(bin_edges))
            delta_distance.append(bin_edges[1] - bin_edges[0])

            recipe_timestamp = np.array(single_recipe_distance_data["Timestamp"])
            time_intervals = recipe_timestamp[1:] - recipe_timestamp[:-1]
            for risky_distance in risky_distances:
                tot_time_under_risky = np.sum(time_intervals[single_recipe_distance_data["Mean"].iloc[:-1] < risky_distance])
                percentage_time_under_risky = tot_time_under_risky / (recipe_timestamp[-1] - recipe_timestamp[0]) * 100
                percentage_under_risky_dataset[RECIPE_NAME_COLUMN].append(single_recipe)
                percentage_under_risky_dataset[RECIPE_TYPE_COLUMN].append(recipe_name)
                percentage_under_risky_dataset[RECIPE_PERCENTAGE_COLUMN].append(percentage_time_under_risky)
                percentage_under_risky_dataset[RECIPE_S_D_TYPE_COLUMN].append(f"Under {risky_distance} m")

        min_distance_recipes = min(min_distance)
        max_distance_recipes = max(max_distance)
        delta_distance_recipes = 0.01

        maximum = max(max_distance_recipes, max_val) + delta_distance_recipes

        distances = np.arange(min_distance_recipes, maximum, delta_distance_recipes)
        x_axis = []
        cumulative_distribution = []
        cumulative_distribution_std = []

        for distance_single in distances:
            x_axis.append(distance_single)
            val_i = []
            for id_recipe, single_recipe in enumerate(single_type_recipe_names):
                recipe_bin_edges = bin_edges_recipes[id_recipe]
                if len(cumulative_dist_recipes[id_recipe][recipe_bin_edges[1:] <= distance_single]) > 0:
                    val_i.append(cumulative_dist_recipes[id_recipe][recipe_bin_edges[1:] <= distance_single][-1])
                else:
                    val_i.append(0)
            cumulative_distribution.append(np.mean(val_i))
            cumulative_distribution_std.append(np.std(val_i))

        lower_bound = np.array(cumulative_distribution) - 2 * np.array(cumulative_distribution_std)
        upper_bound = np.array(cumulative_distribution) + 2 * np.array(cumulative_distribution_std)
        upper_bound[upper_bound > 1] = 1
        lower_bound[lower_bound < 0] = 0

        ax.plot(x_axis, cumulative_distribution, '-', label=f"{RENAME[recipe_name]}")
        ax.fill_between(x_axis, lower_bound, upper_bound, alpha=.15, label="(Confidence 95 %)")

        if zoom:
            ax2.plot(x_axis, cumulative_distribution, '-', label=f"{RENAME[recipe_name]}")
            ax2.fill_between(x_axis, lower_bound, upper_bound, alpha=.15)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=[(h1, h2) for h1, h2 in zip(handles[::2], handles[1::2])],
              labels=[l1 + " " + l2 for l1, l2 in zip(labels[::2], labels[1::2])], loc='lower right', fontsize=20)
    ax.figure.set_size_inches(17, 10)
    for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
        item.set_fontsize(20)

    min_distances_pd = pd.DataFrame(min_distances.items(), columns=['Method', 'Min Distance (m)'])
    min_distances_pd["Method"] = min_distances_pd["Method"].replace(RENAME)

    baseline_distance = min_distances_pd[min_distances_pd['Method'] == 'Baseline TP']['Min Distance (m)'].values[0]
    min_distances_pd['Difference from Baseline (m)'] = min_distances_pd['Min Distance (m)'] - baseline_distance
    not_neigh_distance = min_distances_pd[min_distances_pd['Method'] == 'Not Neighboring TP']['Min Distance (m)'].values[0]
    min_distances_pd['Difference from Not Neighboring (m)'] = min_distances_pd['Min Distance (m)'] - not_neigh_distance

    if latex:
        latex_table = tabulate(min_distances_pd, headers="keys", tablefmt="latex_raw")
        print(latex_table)

    ax.set_xlabel("Minimum Human-Robot Distance (m)", labelpad=25)
    ax.set_ylabel("Cumulative Distribution Function")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))

    if zoom:
        for item in ([ax2.title, ax2.xaxis.label, ax2.yaxis.label] + ax2.get_xticklabels() + ax2.get_yticklabels()):
            item.set_fontsize(20)

    plt.savefig(f"{args.experiment}_cumulative_distance.png")

    percentage_under_risky_dataset = pd.DataFrame.from_dict(percentage_under_risky_dataset)
    percentage_under_risky_dataset[RECIPE_NAME_COLUMN] = percentage_under_risky_dataset[RECIPE_NAME_COLUMN].replace(
        RENAME)
    percentage_under_risky_dataset[RECIPE_TYPE_COLUMN] = percentage_under_risky_dataset[RECIPE_TYPE_COLUMN].replace(
        RENAME)
    # percentage_under_risky_dataset.to_csv(Path(file_path).stem + "_percentage.csv")
    sns.catplot(data=percentage_under_risky_dataset, kind="bar", x=RECIPE_S_D_TYPE_COLUMN,
                y=RECIPE_PERCENTAGE_COLUMN, hue=RECIPE_TYPE_COLUMN, height=8, aspect=1.5)
    plt.show()

if __name__ == '__main__':
    main()
