# Immune cell analysis

This repo is for the Teiko Technical assessment,

## Run in GitHub Codespaces

From the repository root, run:

```bash
make setup
make pipeline
make dashboard
```

Open the [dashboard](http://localhost:8501). In Codespaces, open the **Ports** tab and follow the forwarded link for port **8501** if `localhost` does not open the app in your browser. Keep `make dashboard` running while viewing it. `make pipeline` creates `cell-count.db` in the repository root and writes derived tables to `outputs/`. Both are generated files; the dashboard reads the database created by the pipeline.