#!/usr/bin/env python3

import argparse
from MongoInterface import MongoInterface
from statistical_pipeline import StatisticalPipeline
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tabulate import tabulate
import plotly.express as px

RECIPE_NAMES = {
    "TESTdsfds": "Safety Areas - HA",
    "SAFETY_AREA_NO_AWARE": "Safety Areas - Random",
    "NOT_NEIGHBORING_TASKS": "Not Neighboring TP",
    "TEST_WITH_GOHOME": "test",
    "ONELINE": "AWARE",
    "RELAXED_HA_SOLVER": "Relaxed S. TP",
    "BASIC_SOLVER": "Baseline TP",
    "COMPLETE_SOLVER": "Synergistic TP",
    "COMPLETE_HA_SOLVER": "Synergistic TP",
    "TEST_COMPLETE": "Test",
    "TEST_RELAXED": "Test REL",
    "NEW": "New"
}

DATABASES = {
    "safety_areas": ("safety_areas", "task_results_online"),
    "velocity_scaling": ("velocity_scaling", "task_results_online"),
    "realworld_case_study": ("hrc_case_study", "task_results_online")
}

ORDER = ["Baseline TP", "Not Neighboring TP", "Relaxed S. TP", "Synergistic TP"]

def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--latex", action="store_true", help="Output results in LaTeX format")
    parser.add_argument("--plotly", action="store_true", help="Show results using Plotly")
    parser.add_argument("--experiment", choices=DATABASES.keys(), required=True, help="Select the database to use")

    args = parser.parse_args()

    database_name, results_collection_name = DATABASES[args.experiment]
    mongo_interface = MongoInterface(database_name)

    pipeline = StatisticalPipeline.recipes_duration_pipeline()
    results = mongo_interface.query(results_collection_name, pipeline)
    results_base_tp = []

    for recipe_result in results:
        if "recipe_name" not in recipe_result:
            return 0
        for recipe_name in RECIPE_NAMES:
            if recipe_name in recipe_result["recipe_name"]:
                if "TEST" in recipe_result["recipe_name"]:
                    recipe_result["recipe_name"] = "Test"
                    results_base_tp.append(recipe_result)
                    continue
                recipe_result["recipe_name"] = RECIPE_NAMES[recipe_name]
                # print(RECIPE_NAMES[recipe_name])
                results_base_tp.append(recipe_result)

    result_pd = pd.DataFrame(results_base_tp)
    sns.set_theme()

    result_pd.rename(columns={'recipe_duration': 'Plan Duration (s)', 'recipe_name': 'Task Planner Type'}, inplace=True)
    ax = sns.boxplot(data=result_pd, x="Plan Duration (s)", y="Task Planner Type", showfliers=False, 
                     order=["Baseline TP", "Not Neighboring TP", "HA-TP (Relaxed)", "HA-TP"])

    mean_duration = result_pd.groupby("Task Planner Type")["Plan Duration (s)"].mean().reset_index()
    mean_duration.rename(columns={"Plan Duration (s)": "Mean Duration (s)"}, inplace=True)

    baseline_duration = mean_duration[mean_duration["Task Planner Type"] == "Baseline TP"]["Mean Duration (s)"].values[0]
    not_neighboring_duration = mean_duration[mean_duration["Task Planner Type"] == "Not Neighboring TP"]["Mean Duration (s)"].values[0]

    mean_duration["Reduction from Baseline (%)"] = ((baseline_duration - mean_duration["Mean Duration (s)"]) / baseline_duration) * 100
    mean_duration["Reduction from Not Neighboring (%)"] = ((not_neighboring_duration - mean_duration["Mean Duration (s)"]) / not_neighboring_duration) * 100

    if args.latex:
        latex_table = tabulate(mean_duration, headers="keys", tablefmt="latex_raw")
        print(latex_table)

    if args.plotly:
        fig = px.box(result_pd, x="Plan Duration (s)", y="Task Planner Type", color="Task Planner Type", category_orders={"Task Planner Type": ORDER})
        # fig.update_layout(
        #     paper_bgcolor='rgba(0,0,0,0)',
        # )
        # fig.write_html(f"{database_name}_durations.html", full_html=False, include_plotlyjs='cdn')
        fig.show()

    plt.ylabel("")
    plt.savefig("duration_comparison.pdf", bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
