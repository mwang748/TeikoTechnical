import sqlite3
from contextlib import closing
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

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


# Part 3

POPULATIONS = ("b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte")
DAYS = (0, 7, 14)
SIGNIFICANCE_CUTOFF = 0.05 / (len(POPULATIONS) * len(DAYS))

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
        p = ttest_ind(yes, no, equal_var=False).pvalue
        results.append({
            "population": population,
            "yes_n": len(yes),
            "no_n": len(no),
            "yes_mean": mean(yes),
            "no_mean": mean(no),
            "p_value": float(p),
            "significant": bool(p < SIGNIFICANCE_CUTOFF),
        })

    return results

# Part 4:

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

def main():
    print(avg_b_cells)

if __name__ == "__main__":
    main()