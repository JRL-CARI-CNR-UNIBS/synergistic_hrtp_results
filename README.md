# Paper results and analysis

This repository contains all the data (from simulations and real experiments) and all the scripts to reproduce the graphs of the paper "Learning and planning for optimal synergistic human-robot coordination in manufacturing contexts". In addition, it contains the results of the questionnaire carried out on the pool of users who performed the experiments and the corresponding statistical analysis. The data of the simulations are in the [safety_areas](https://github.com/JRL-CARI-CNR-UNIBS/synergistic_hrtp_results/tree/main/safety_areas) and [velocity_scaling](https://github.com/JRL-CARI-CNR-UNIBS/synergistic_hrtp_results/tree/main/velocity_scaling) folder (the two safety scenarios in which the methods were tested). Simulation data are in the [hrc_case_study_results](https://github.com/JRL-CARI-CNR-UNIBS/hrc_case_study/tree/ae6d9065e5835210ef4257ea7cc402bd322ca50a/hrc_case_study_results) folder of the hrc_case_study submodule.

## Installation

Prerequisites:

- Python 3.x
- [Docker](https://docs.docker.com/engine/install/)

### Steps

1. **Clone the repository**: Take care to use this command to clone the repo since there is a submodule inside this repo with the experiments results.

  ```bash
   git clone --recurse-submodules https://github.com/SamueleSandrini/synergistic_hrtp_results
   cd synergistic_hrtp_results
  ```
2. **Install MongoDB using Docker**: To install and run MongoDB using Docker, execute the following commands (note that if you already installed that MongoDB docker the first command will fail but you can skip and go on):

  ```bash
  docker pull mongodb/mongodb-community-server:latest
  docker run -p 27017:27017 -d mongodb/mongodb-community-server:latest
  ```
3. **Source the import_data.sh script**: The `import_data.sh` script will create a virtual environment, source it, install the necessary requirements, create the MongoDB database with the required collections, and import the data.

  ```bash
  source import_data.sh
  ```

## Usage

### Human-Robot Distance Comparison
To run the Human-Robot Distance Comparison analysis, use the following command:

```
python3 scripts/distance_statistics.py --latex --zoom --experiment safety_areas
```
args:
* `--zoom`: Activate the window zoomed for low distances
* `--latex`: Activate the LaTeX table print
* `--experiment`: Experiment name for selecting the results of that test. Possible values:
  * `safety_areas`: Safety Areas experiment (simulation)
  * `velocity_scaling`: Velocity Scaling experiment (simulation)
  * `realworld_case_study`: Real-World Case Study experiment

## Human-Robot Duration Comparison
To plot the comparison of TPs durations, it is necessary to install mongodb and create a database with the collections in the various folders.

```
python3 scripts/duration_statistics.py --latex --plotly --experiment safety_areas
```
args:
* `--latex`: Activate the LaTeX table print
* `--plotly`: Activate the Plotly plot
* `--experiment`: Database name for selecting the results of that test. Possible values:
  * `safety_areas`: Safety Areas experiment (simulation)
  * `velocity_scaling`: Velocity Scaling experiment (simulation)
  * `realworld_case_study`: Real-World Case Study experiment

## Human-Robot Synergies matrix

```
python3 scripts/synergies.py --experiment safety_areas
```
args:
* `--experiment`: Experiment name for selecting the results of that test. Possible values:
  * `safety_areas`: Safety Areas experiment (simulation)
  * `velocity_scaling`: Velocity Scaling experiment (simulation)
  * `realworld_case_study`: Real-World Case Study experiment

## Statistical analysis of the questionnaire
| Path  | Notebook |
| ----- | -------- |
| <a href="https://github.com/JRL-CARI-CNR-UNIBS/hrc_case_study/blob/e_waste_case_study/hrc_case_study_results/Questionnaire/Mann_Whitney_Wilcoxon_Test_Online.ipynb">Mann_Whitney_Wilcoxon_Test</a> | <a href="https://colab.research.google.com/github/JRL-CARI-CNR-UNIBS/hrc_case_study/blob/e_waste_case_study/hrc_case_study_results/Questionnaire/Mann_Whitney_Wilcoxon_Test_Online.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>                  |

## Contact
If you have any problems with installation, reproduction, or doubts, please do not hesitate to contact me by email:

* Samuele Sandrini: [samuele.sandrini@polito.it](mailto:samuele.sandrini@polito.it)
