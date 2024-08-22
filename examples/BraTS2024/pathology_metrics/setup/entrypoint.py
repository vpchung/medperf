"""If the predictions and labels inputs to the MLCube should come from different
mount points and can't be referred to in a single csv, a custom entrypoint is
needed to create a temporary csv file before calling GaNDLF's generate metrics command.
This script should expect the same arguments passed to the command `mlcube run --task evaluate`,
i.e. it should expect the inputs and outputs defined in `mlcube.yaml` in the `evaluate` task"""

import argparse
import logging
import os
from glob import glob

import pandas as pd
from cnb_tools import validation_toolkit as vtk


def _extract_value_by_pattern(col, pattern_to_extract):
    """Return specific content from column, specified by pattern."""
    return col.str.extract(pattern_to_extract)


def create_csv(predictions, labels, parent):
    """A function that creates a ./data.csv file from input folders."""
    pattern = r"BraTSPath_Test_\d{7}\.png$"
    penalty_label = 6

    # Read in predictions file and validate it.
    pred_file = glob(os.path.join(predictions, "*.csv"))
    assert len(pred_file) == 1, "There should only be one predictions CSV file"
    try:
        pred = pd.read_csv(pred_file[0], usecols=["SubjectID", "Prediction"])
        pred["SubjectID"] = _extract_value_by_pattern(
            pred.loc[:, "SubjectID"], pattern
        )
    except ValueError as exc:
        raise ValueError(
            "Predictions file missing two required columns: `SubjectID` "
            "and `Prediction` (case-sensitive)"
        ) from exc
    assert (
        vtk.check_duplicate_keys(pred["SubjectID"]) == ""
    ), "Duplicate SubjectIDs found"
    assert (
        vtk.check_values_range(pred["Prediction"], min_val=0, max_val=5) == ""
    ), "'Prediction' should be integers between 0 and 5"

    # Read in labels file and combine it with the predictions file.
    gold = pd.read_csv(os.path.join(labels, "BraTS-PATH-Test-Labels.csv"))
    gold["SubjectID"] = _extract_value_by_pattern(
        gold.loc[:, "SubjectID"], pattern
    )
    res = gold.merge(pred, how="left", on="SubjectID").fillna(penalty_label)

    # Reassign coltype to int, since NaN values will convert coltype to float
    # before outputting to 3-col CSV.
    res["Prediction"] = res["Prediction"].astype(int)
    res.to_csv(os.path.join(parent, "data.csv"), index=False)


def run_gandlf(output_file, config, parent):
    """
    A function that calls GaNDLF's generate metrics command with the previously created csv.

    Args:
        output_file (str): The path to the output file/folder
        config (str): The path to the parameters file
    """
    exit_status = os.system(
        f"gandlf generate-metrics -c {config} -i " +
        os.path.join(parent, "data.csv") +
        f" -o {os.path.join(parent, 'results.json')}"
    )
    exit_code = os.WEXITSTATUS(exit_status)
    logging.info(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", metavar="", type=str, required=True)
    parser.add_argument("--predictions", metavar="", type=str, required=True)
    parser.add_argument("--output_path", metavar="", type=str, default=None)
    parser.add_argument("--labels", metavar="", type=str, required=True)

    args = parser.parse_args()
    parent_dir = "/mlcube_io2"

    create_csv(args.predictions, args.labels, parent_dir)
    run_gandlf(args.output_file, args.config, parent_dir)

    # Convert results from JSON to YAML.
    with open(os.path.join(parent_dir, 'results.json')) as f, \
         open(args.output_path, "w") as out:
        results = json.load(f)
        yaml.dump(results, out)
