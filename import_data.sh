#!/bin/bash

# Safety areas and velocity scaling as requested
SIMULATIONS=("safety_areas" "velocity_scaling")

# Collection names
COLLECTIONS=("task_results_online" "task_synergies")

# Base directory for file paths
BASE_FILE_PATH="Mongodb_Collections"

# Create a virtual environment in the 'venv' directory and install requirements
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment directory already exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Check if requirements.txt exists and install the required packages
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing requirements..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "Requirements file $REQUIREMENTS_FILE does not exist."
    exit 1
fi

# Options for the Python file
PYTHON_EXECUTABLE="python3"
PYTHON_SCRIPT="import_data_to_mongodb.py"

# Iterate over each simulation
for simulation_name in "${SIMULATIONS[@]}"
do
    # Set database name (using the element as requested)
    DATABASE_NAME="$simulation_name"
    # Iterate over each collection
    for collection_name in "${COLLECTIONS[@]}"
    do
        # Compose the file path
        FILE_PATH="$simulation_name/$BASE_FILE_PATH/$collection_name"
        echo "$FILE_PATH"

        # Check if the specified file exists
        if [ ! -f "$FILE_PATH" ]; then
            echo "File $FILE_PATH does not exist."
            exit 1
        fi


        # Execute the Python script with the provided arguments
        echo "Running Python script to import data into MongoDB for database '$DATABASE_NAME' and collection '$collection_name'..."
        $PYTHON_EXECUTABLE $PYTHON_SCRIPT $DATABASE_NAME $collection_name $FILE_PATH

        echo "Operation completed for database '$DATABASE_NAME' and collection '$collection_name'."
    done
done

# Experiments
DATABASE_NAME="hrc_case_study"
for collection_name in "${COLLECTIONS[@]}"
do
    FILE_PATH="hrc_case_study/hrc_case_study_results/Mongodb_Collections/$collection_name"
    echo "Running Python script to import data into MongoDB for database '$DATABASE_NAME' and collection '$collection_name'..."
    $PYTHON_EXECUTABLE $PYTHON_SCRIPT $DATABASE_NAME $collection_name $FILE_PATH
    echo "Operation completed for database '$DATABASE_NAME' and collection '$collection_name'."
done