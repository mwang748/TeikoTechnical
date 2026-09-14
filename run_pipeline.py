"""Write reproducible Parts 2–4 outputs from the loaded database."""

import csv
import json
from pathlib import Path

from analysis import DAYS, DATABASE, get_baseline_summary, get_diff_stats, get_diffs, get_frequencies


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def write_csv(path, rows, columns):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if not DATABASE.exists():
        raise SystemExit("Database not found. Run python load_data.py first.")
    OUTPUT_DIR.mkdir(exist_ok=True)

    frequencies = get_frequencies()
    write_csv(
        OUTPUT_DIR / "frequencies.csv",
        frequencies,
        ["sample", "total_count", "population", "count", "percentage"],
    )

    comparisons = []
    for day in DAYS:
        for row in get_diff_stats(get_diffs(day)):
            comparisons.append({"day": day, **row})
    write_csv(
        OUTPUT_DIR / "response_comparison.csv",
        comparisons,
        ["day", "population", "yes_n", "no_n", "yes_mean", "no_mean",
         "p_value", "significant"],
    )

    sample_ids, projects, responses, sexes = get_baseline_summary()
    write_csv(
        OUTPUT_DIR / "baseline_samples.csv",
        ({"sample": sample} for sample in sample_ids),
        ["sample"],
    )
    (OUTPUT_DIR / "baseline_summary.json").write_text(
        json.dumps({
            "sample_count": len(sample_ids),
            "samples_by_project": projects,
            "subjects_by_response": responses,
            "subjects_by_sex": sexes,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    print("Pipeline Done.")


if __name__ == "__main__":
    main()
