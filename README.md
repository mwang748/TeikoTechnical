# Immune cell analysis

This project loads `data/cell-count.csv` into SQLite and explores immune-cell frequencies, response to miraclib, and the baseline melanoma PBMC subset.

## Run in GitHub Codespaces

From the repository root, run:

```bash
make setup
make pipeline
make dashboard
```

Open the [dashboard](http://localhost:8501). In Codespaces, open the **Ports** tab and follow the forwarded link for port **8501** if `localhost` does not open the app in your browser. Keep `make dashboard` running while viewing it.

## Project layout

```text
.
├── data/
│   ├── cell-count.csv           # source data
│   └── database_schema.sql     # SQLite tables
├── docs/
│   └── Instructions.md         # assignment brief
├── analysis.py                 # Parts 2–4 queries and statistics
├── dashboard.py                # interactive dashboard
├── load_data.py                # required root-level database loader
├── run_pipeline.py             # exports analysis results
├── Makefile                    # setup, pipeline, dashboard targets
├── requirements.txt
└── README.md
```

`make pipeline` creates `cell-count.db` in the repository root and writes derived tables to `outputs/`. Both are generated files; the dashboard reads the database created by the pipeline.
