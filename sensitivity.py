"""Contrast an ordinary random holdout with external validation; bootstrap studies."""

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from cohort import cohort, preprocess
from analysis import folds, select_alpha
from inputs import OUT


def main():
    d, x, y = cohort()
    train, test = train_test_split(np.arange(len(d)), test_size=0.25, random_state=42)
    z = preprocess(x, train)
    alpha = select_alpha(d, x, y, np.isin(np.arange(len(d)), train))
    pred = Ridge(alpha=alpha).fit(z[train], y[train]).predict(z[test])
    pd.DataFrame(
        [
            dict(
                people=len(test),
                overlapping_studies=len(
                    set(d.study_accession[train]) & set(d.study_accession[test])
                ),
                ridge_MAE=np.mean(abs(pred - y[test])),
                median_MAE=np.mean(abs(np.median(y[train]) - y[test])),
            )
        ]
    ).to_csv(OUT / "random_holdout_diagnostic.csv", index=False)
    rng = np.random.default_rng(143)
    rows = []
    for name, tr, te in folds(d):
        alpha = select_alpha(d, x, y, tr)
        z = preprocess(x, tr)
        pred = Ridge(alpha=alpha).fit(z[tr], y[tr]).predict(z[te])
        difference = abs(pred - y[te]) - abs(np.median(y[tr]) - y[te])
        study = d.loc[te, "study_accession"].to_numpy()
        estimates = []
        for _ in range(500):
            # Resample study clusters, then participants within the selected studies.
            values = []
            for group in rng.choice(np.unique(study), len(set(study)), replace=True):
                a = difference[study == group]
                values.extend(rng.choice(a, len(a)))
            estimates.append(np.mean(values))
        rows.append(
            [
                name,
                te.sum(),
                len(set(study)),
                np.mean(difference),
                *np.quantile(estimates, [0.025, 0.975]),
            ]
        )
    pd.DataFrame(
        rows,
        columns=[
            "formulation",
            "people",
            "studies",
            "ridge_minus_median_MAE",
            "lower",
            "upper",
        ],
    ).to_csv(OUT / "paired_error_intervals.csv", index=False)


if __name__ == "__main__":
    main()
