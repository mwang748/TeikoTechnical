import sqlite3
from contextlib import closing
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt
from scipy.stats import false_discovery_control, mannwhitneyu

DATABASE = Path(__file__).resolve().parent / "cell-count.db"

# Part 2
def get_frequencies():
    # this query gets the total_counts per sample and cell count for each sample
    # and then finds the relative percentage of each cell wrt the total cells for that sample
    # each row corresponds to the cell amounts for that sample 
    GET_FREQUENCIES = """
    WITH sample_counts AS (
        SELECT sample,
            b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte,
            b_cell + cd8_t_cell + cd4_t_cell + nk_cell + monocyte AS total_count
        FROM samples
    ), populations AS (
        SELECT sample, total_count, 'b_cell' AS population, b_cell AS count
        FROM sample_counts
        UNION ALL
        SELECT sample, total_count, 'cd8_t_cell', cd8_t_cell FROM sample_counts
        UNION ALL
        SELECT sample, total_count, 'cd4_t_cell', cd4_t_cell FROM sample_counts
        UNION ALL
        SELECT sample, total_count, 'nk_cell', nk_cell FROM sample_counts
        UNION ALL
        SELECT sample, total_count, 'monocyte', monocyte FROM sample_counts
    )
    SELECT sample, total_count, population, count,
        100.0 * count / total_count AS percentage
    FROM populations
    ORDER BY sample, population
    """
    with closing(sqlite3.connect(DATABASE)) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute(GET_FREQUENCIES)]


def display_frequencies():
    print(f"{'sample':<14} {'total_count':>12} {'population':<12} {'count':>10} {'percentage':>12}")
    for row in get_frequencies():
        print(
            f"{row['sample']:<14} {row['total_count']:>12} "
            f"{row['population']:<12} {row['count']:>10} "
            f"{row['percentage']:>11.2f}%"
        )


# Part 3

POPULATIONS = ("b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte")

def get_diffs(day=0):
    GET_SAMPLES_QUERY = """
    SELECT samples.sample, subjects.response
    FROM samples
    JOIN subjects on samples.subject = subjects.subject
    WHERE subjects.condition = 'melanoma' 
    AND subjects.treatment = 'miraclib' 
    AND samples.sample_type = 'PBMC'
    AND samples.time_from_treatment_start = ?
    """

    with closing(sqlite3.connect(DATABASE)) as connection:
        # sample, subject, response
        # samples that fit the requirement (melanoma, miraclib, pbmc)
        samples = dict(connection.execute(GET_SAMPLES_QUERY, (day,)))
    # want 5 groups of 2 box plots/tables, each representing one cell population
    # each group shows yes vs no for that cell population
    groups = {
        population: {"yes": [], "no": []}
        for population in POPULATIONS
    }

    for row in get_frequencies():
        response = samples.get(row["sample"])
        if response is not None:
            groups[row["population"]][response].append(row["percentage"])

    return groups

def plot_diffs(groups):
    fig, axes = plt.subplots(1, 5, figsize=(17, 4), sharey=True)

    for ax, population in zip(axes, POPULATIONS):
        ax.boxplot([
            groups[population]["yes"],
            groups[population]["no"],
        ])
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["Yes", "No"])
        ax.set_title(population)
        ax.set_ylabel("Relative frequency (%)")

    fig.suptitle("Day-0 PBMC samples: response to miraclib")
    fig.tight_layout()
    plt.show()

def get_diff_stats(groups):
    results = []

    for population in POPULATIONS:
        yes = groups[population]["yes"]
        no = groups[population]["no"]
        p = mannwhitneyu(yes, no, alternative="two-sided").pvalue
        results.append({
            "population": population,
            "yes_n": len(yes),
            "no_n": len(no),
            "yes_median": median(yes),
            "no_median": median(no),
            "p_value": float(p),
        })

    adjusted_p_values = false_discovery_control(
        [result["p_value"] for result in results], method="bh"
    )

    for result, adjusted_p in zip(results, adjusted_p_values):
        result["adjusted_p"] = float(adjusted_p)
        result["significant"] = bool(adjusted_p < 0.05)

    return results


def report_diffs(groups):
    for result in get_diff_stats(groups):
        print(
            f"{result['population']}: yes median={result['yes_median']:.2f}%, "
            f"no median={result['no_median']:.2f}%, "
            f"p={result['p_value']:.4f}, adjusted p={result['adjusted_p']:.4f}, "
            f"significant={result['significant']}"
        )

# Part 4:

# Part 4
BASELINE_QUERY = """
WITH baseline AS (
    SELECT samples.sample, samples.subject, subjects.project, subjects.response, subjects.sex
    FROM samples
    JOIN subjects ON samples.subject = subjects.subject
    WHERE subjects.condition = 'melanoma'
      AND samples.sample_type = 'PBMC'
      AND subjects.treatment = 'miraclib'
      AND samples.time_from_treatment_start = 0
)
"""


def get_baseline_summary():
    with closing(sqlite3.connect(DATABASE)) as connection:
        sample_ids = [
            row[0] for row in connection.execute(
                BASELINE_QUERY + "SELECT sample FROM baseline ORDER BY sample"
            )
        ]
        projects = dict(connection.execute(
            BASELINE_QUERY
            + "SELECT project, COUNT(*) FROM baseline GROUP BY project"
        ))
        responses = dict(connection.execute(
            BASELINE_QUERY
            + "SELECT response, COUNT(DISTINCT subject) "
              "FROM baseline GROUP BY response"
        ))
        sexes = dict(connection.execute(
            BASELINE_QUERY
            + "SELECT sex, COUNT(DISTINCT subject) FROM baseline GROUP BY sex"
        ))

    return sample_ids, projects, responses, sexes

def display_baseline_summary():
    sample_ids, projects, responses, sexes = get_baseline_summary()
    print(f"Baseline samples ({len(sample_ids)}):", sample_ids)
    print("Samples by project:", projects)
    print("Subjects by response:", responses)
    print("Subjects by sex:", sexes)

def avg_b_cells():
    AVG_B_CELLS = """
    SELECT AVG(b_cell)
    FROM samples
    JOIN subjects on samples.subject = subjects.subject
    WHERE condition = 'melanoma'
    AND sex = 'M'
    AND time_from_treatment_start = 0
    AND response = 'yes'
    """

    with closing(sqlite3.connect(DATABASE)) as connection:
        return connection.execute(AVG_B_CELLS).fetchone()[0]
if __name__ == "__main__":
    # # Part 2:
    # display_frequencies()
    
    # # Part 3:
    # groups = get_diffs()
    # report_diffs(groups)
    # plot_diffs(groups)

    # # Part 4:
    # display_baseline_summary()

    # Avg b_cells
    b_cells = avg_b_cells()
    print(f"The average number of B cells for responder Melanoma males at time=0 is {b_cells:.2f}")
