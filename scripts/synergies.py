#!/usr/bin/env python3

import argparse
from MongoInterface import MongoInterface
from statistical_pipeline import StatisticalPipeline
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DATABASES = {
    "safety_areas": ("safety_areas", "task_synergies"),
    "velocity_scaling": ("velocity_scaling", "task_synergies"),
    "realworld_case_study": ("hrc_case_study", "task_synergies")
}

RECIPE_NAMES = {
    "TESTdsfds": "Safety Areas - HA",
    "SAFETY_AREA_NO_AWARE": "Safety Areas - Random",
    "NOT_NEIGHBORING_TASKS": "Not Neighboring TP",
    "TEST_WITH_GOHOME": "test",
    "ONELINE": "AWARE",
    "RELAXED_HA_SOLVER": "HA-TP (Relaxed)",
    "BASIC_SOLVER": "Baseline TP",
    "COMPLETE_SOLVER": "HA-TP",
    "COMPLETE_HA_SOLVER": "HA-TP",
    "TEST_COMPLETE": "Test",
    "TEST_RELAXED": "Test REL",
    "NEW": "New"
}

KNOWN_TASK_NAME = {
    "pick_blue_box_human_right_arm": "Pick Blue Box (H)",
    "place_blue_box_human_right_arm": "Place Blue Box (H)",
    "pick_blue_box_ur5_on_guide": "Pick Blue Box (R)",
    "place_blue_box_ur5_on_guide": "Place Blue Box (R)",
    "pick_white_box": "Pick White Box",
    "place_white_box": "Place White Box",
    "pick_orange_box": "Pick Orange Box",
    "place_orange_box": "Place Orange Box",
    "probe": "Probe_circuit"
}

AGENT_LABELS = {
    "ur5_on_guide": {"name": "Robot", "abbreviation": "R"},
    "manipulator": {"name": "Robot", "abbreviation": "R"},
    "human_right_arm": {"name": "Human", "abbreviation": "H"},
    "human": {"name": "Human", "abbreviation": "H"}
}

def get_task_name(raw_task_name):
    """Method for replacing task names (for charts inherent in the paper)

    Args:
        agent (str): task name in db

    Returns:
        str: Paper task name
    """
    task_name = KNOWN_TASK_NAME.get(raw_task_name, raw_task_name)
    task_name = task_name.split('_')
    task_name = ' '.join(singol_word.capitalize() for singol_word in task_name)
    return task_name

def append_agent_to_skill(skill, agent, skill_keyword="pick_blue_box"):
    """Append the agent to the skill name if the skill contains the specified keyword

    Args:
        skill (str): The skill name
        agent (str): The agent name to append
        skill_keyword (str): The keyword to check in the skill name

    Returns:
        str: Modified skill name
    """
    if skill_keyword in skill:
        return f"{skill}_{agent}"
    return skill

def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--experiment", choices=DATABASES.keys(), required=True, help="Select the database to use")

    args = parser.parse_args()

    database_name, synergies_collection_name = DATABASES[args.experiment]

    mongo_interface = MongoInterface(database_name)

    pipeline_grouped_synergies = StatisticalPipeline.grouped_synergies_pipeline()
    grouped_synergies = mongo_interface.query(synergies_collection_name, pipeline_grouped_synergies)
    
    dynamic_risk_list = []

    for index, dynamic_risk_single_agent in enumerate(grouped_synergies):
        dynamic_risk_list.append({})
        dynamic_risk_list[index][dynamic_risk_single_agent["_id"]] = []
        dynamic_risk_list[index]["dynamic_risk"] = []
        dynamic_risk_list[index]["main_agent"] = dynamic_risk_single_agent["_id"]

        for dynamic_risk_single_element in dynamic_risk_single_agent["grouped_task_agent"]:
            if dynamic_risk_single_element["concurrent_agent"] not in dynamic_risk_list[index]:
                dynamic_risk_list[index][dynamic_risk_single_element["concurrent_agent"]] = []
                dynamic_risk_list[index]["concurrent_agent"] = dynamic_risk_single_element["concurrent_agent"]

            agent_skill = append_agent_to_skill(dynamic_risk_single_element["agent_skill"], dynamic_risk_single_element["agent"])
            concurrent_agent_skill = append_agent_to_skill(dynamic_risk_single_element["concurrent_skill"], dynamic_risk_single_element["concurrent_agent"])

            dynamic_risk_list[index][dynamic_risk_single_agent["_id"]].append(agent_skill)
            dynamic_risk_list[index][dynamic_risk_single_element["concurrent_agent"]].append(concurrent_agent_skill)
            dynamic_risk_list[index]["dynamic_risk"].append(dynamic_risk_single_element["dynamic_risk"])

    for index, single_agent_dynamic_risk in enumerate(dynamic_risk_list):
        main_agent = single_agent_dynamic_risk["main_agent"]
        concurrent_agent = single_agent_dynamic_risk["concurrent_agent"]

        single_agent_dynamic_risk.pop("main_agent", None)
        single_agent_dynamic_risk.pop("concurrent_agent", None)

        data = pd.DataFrame(single_agent_dynamic_risk)

        if data.duplicated().any():
            print("There are duplicated tasks")
            print(data.duplicated())
            return False, "NOT_SUCCESSFUL"

        data_matrix = data.pivot(index=main_agent, columns=concurrent_agent, values='dynamic_risk')

        plot_title = "Synergy Matrix for agent: {}".format(main_agent)

        main_agent_label = AGENT_LABELS.get(main_agent, {"name": main_agent, "abbreviation": main_agent})
        concurrent_agent_label = AGENT_LABELS.get(concurrent_agent, {"name": concurrent_agent, "abbreviation": concurrent_agent})

        plot_title = "Synergy Matrix for agent: {} ($S^{}$)".format(main_agent_label["name"], main_agent_label["abbreviation"])
        
        for agent in [main_agent, concurrent_agent]:
            for k in data.index:
                data.at[k, agent] = get_task_name(data.at[k, agent])
        
        data = data.rename(columns={main_agent: main_agent_label["name"] + " Tasks", concurrent_agent: concurrent_agent_label["name"] + " Tasks"})
        data_matrix = data.pivot(index=main_agent_label["name"] + " Tasks", columns=concurrent_agent_label["name"] + " Tasks", values="dynamic_risk")

        sns.set_theme()

        plt.figure(index)
        sns.heatmap(data_matrix, annot=True, cmap="flare")
        plt.ylabel(main_agent_label["name"] + " Tasks", labelpad=25)
        plt.xticks(rotation=20, ha="right")
        plt.title(plot_title)
    plt.show()

if __name__ == "__main__":
    main()
