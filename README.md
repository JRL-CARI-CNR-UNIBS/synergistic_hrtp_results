# Paper results and analysis

## Installation


## Human-Robot Distance Comparison

```
python3 distance_statistics.py --zoom --latex --experiment "safety_areas"
```
args:
* `--zoom`: activate the window zoomed for low distances  
* `--latex`: activate the latex table print
* `--experiment`: experiment name for selecting the results of that test. Possible values:
  * `safety_areas`: Safety Areas experiment (simulation)
  * `velocity_scaling`: Velocity Scaling experiment (simulation)
  * `realworld_case_study`: Real-World Case Study experiment

## Human-Robot Duration Comparison
```
python3 duration_statistics.py --latex --plotly --db
```
args:
* `--latex`: activate the latex table print
* `--plotly`: activate the plotly plot  
* `--db`: database name for selecting the results of that test. Possible values:
  * `safety_areas`: Safety Areas experiment (simulation)
  * `velocity_scaling`: Velocity Scaling experiment (simulation)
  * `realworld_case_study`: Real-World Case Study experiment

## Synergies