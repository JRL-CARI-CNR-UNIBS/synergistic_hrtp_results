#!/bin/bash

# Safety areas and velocity scaling as requested
SIMULATIONS=("safety_areas" "velocity_scaling")

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

# Iterate over each element
for simulation_name in "${SIMULATIONS[@]}"
do
    # Set database name (using the element as requested)
    DATABASE_NAME="$simulation_name"

    # Set collection name
    COLLECTION_NAME="task_results_online"

    # Set file path (using the element and file name)
    FILE_PATH="$simulation_name/Mongodb_Collections/task_results_online"

    # Check if the specified file exists
    if [ ! -f "$FILE_PATH" ]; then
        echo "File $FILE_PATH does not exist."
        exit 1
    fi

    # Options for the Python file
    PYTHON_EXECUTABLE="python3"
    PYTHON_SCRIPT="import_data_to_mongodb.py"

    # Execute the Python script with the provided arguments
    echo "Running Python script to import data into MongoDB for database '$DATABASE_NAME' and collection '$COLLECTION_NAME'..."
    $PYTHON_EXECUTABLE $PYTHON_SCRIPT $DATABASE_NAME $COLLECTION_NAME $FILE_PATH

    echo "Operation completed for database '$DATABASE_NAME' and collection '$COLLECTION_NAME'."
done

# Deactivate the virtual environment
deactivate
