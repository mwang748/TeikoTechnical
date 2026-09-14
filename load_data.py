# Part 1
import sqlite3
import csv
from pathlib import Path

root = Path(__file__).resolve().parent
conn = sqlite3.connect(root / "cell-count.db")

try:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((root / "data" / "database_schema.sql").read_text())

    with (root / "data" / "cell-count.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            conn.execute(
                """
                INSERT OR IGNORE INTO subjects
                    (subject, project, condition, age, sex, treatment, response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["subject"], row["project"], row["condition"],
                    int(row["age"]), row["sex"], row["treatment"],
                    row["response"] or None,
                ),
            )

            conn.execute(
                """
                INSERT OR IGNORE INTO samples
                    (sample, subject, sample_type, time_from_treatment_start,
                     b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["sample"], row["subject"], row["sample_type"],
                    int(row["time_from_treatment_start"]),
                    int(row["b_cell"]), int(row["cd8_t_cell"]),
                    int(row["cd4_t_cell"]), int(row["nk_cell"]),
                    int(row["monocyte"]),
                ),
            )

    conn.commit()
finally:
    conn.close()
