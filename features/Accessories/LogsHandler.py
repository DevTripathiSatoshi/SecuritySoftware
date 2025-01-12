import json


def logs(pathx,data):
    """
    Save log data to a JSON file.
    """
    try:
        # Read existing logs
        with open(pathx, "r") as file:
            log_data = json.load(file)
    except FileNotFoundError:
        # If file doesn't exist, initialize log_data
        log_data = []

    # Append new data
    log_data.append(data)

    # Write back to file
    with open(pathx, "w") as file:
        json.dump(log_data, file, indent=4)