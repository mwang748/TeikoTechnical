import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from analysis import (
    DATABASE,
    DAYS,
    POPULATIONS,
    SIGNIFICANCE_CUTOFF,
    get_baseline_summary,
    get_diff_stats,
    get_diffs,
    get_frequencies,
)


st.set_page_config(page_title="Immune cell analysis", layout="wide")
st.title("Immune cell analysis")

if not DATABASE.exists():
    st.error("Database not found. Run `make pipeline` first.")
    st.stop()

overview_tab, response_tab, baseline_tab = st.tabs(
    ["Cell frequencies", "Treatment response", "Baseline subset"]
)

with overview_tab:
    st.subheader("Cell population frequencies by sample")
    frequencies = pd.DataFrame(get_frequencies())
    sample = st.selectbox("Choose a sample", sorted(frequencies["sample"].unique()))
    sample_rows = frequencies.loc[frequencies["sample"] == sample]
    st.metric("Total cells", f"{int(sample_rows['total_count'].iloc[0]):,}")
    st.dataframe(sample_rows, hide_index=True, width="stretch")
    with st.expander("View the complete frequency table"):
        st.dataframe(frequencies, hide_index=True, width="stretch")

with response_tab:
    st.subheader("Melanoma PBMC samples from miraclib recipients")
    day = st.selectbox("Days from treatment start", DAYS)
    if day == 0:
        st.caption("Day 0 is the primary comparison for exploring response prediction.")
    else:
        st.caption("On-treatment comparisons are exploratory and use one sample per subject at this day.")

    groups = get_diffs(day)
    stats = get_diff_stats(groups)
    st.dataframe(
        pd.DataFrame(stats).rename(columns={
            "population": "Population",
            "yes_n": "Responders",
            "no_n": "Non-responders",
            "yes_mean": "Responder mean (%)",
            "no_mean": "Non-responder mean (%)",
            "p_value": "p-value",
            "significant": f"Significant (p < {SIGNIFICANCE_CUTOFF:.4f})",
        }).round(4),
        hide_index=True,
        width="stretch",
    )
    if not any(row["significant"] for row in stats):
        st.info(f"No cell population has a p-value below {SIGNIFICANCE_CUTOFF:.4f}.")

    fig, axes = plt.subplots(1, len(POPULATIONS), figsize=(17, 4), sharey=True)
    for ax, population in zip(axes, POPULATIONS):
        ax.boxplot([groups[population]["yes"], groups[population]["no"]])
        ax.set_xticks([1, 2])
        ax.set_xticklabels(["Yes", "No"])
        ax.set_title(population)
    axes[0].set_ylabel("Relative frequency (%)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption(f"The table compares group means. We use p < {SIGNIFICANCE_CUTOFF:.4f} because five cell populations are checked at three days; the boxplots show the spread of individual samples.")

with baseline_tab:
    st.subheader("Baseline melanoma PBMC samples from miraclib recipients")
    sample_ids, projects, responses, sexes = get_baseline_summary()
    st.metric("Matching samples", len(sample_ids))

    project_col, response_col, sex_col = st.columns(3)
    with project_col:
        st.write("Samples by project")
        st.dataframe(pd.DataFrame(projects.items(), columns=["Project", "Samples"]),
                     hide_index=True, width="stretch")
    with response_col:
        st.write("Subjects by response")
        st.dataframe(pd.DataFrame(responses.items(), columns=["Response", "Subjects"]),
                     hide_index=True, width="stretch")
    with sex_col:
        st.write("Subjects by sex")
        st.dataframe(pd.DataFrame(sexes.items(), columns=["Sex", "Subjects"]),
                     hide_index=True, width="stretch")

    with st.expander("View all matching sample IDs"):
        st.dataframe(pd.DataFrame({"sample": sample_ids}),
                     hide_index=True, width="stretch")
