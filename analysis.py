import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor
from cohort import cohort, preprocess
from inputs import OUT


def folds(d):
    for vaccine in sorted(d.vaccine.unique()):
        test = d.vaccine == vaccine
        train = (
            ~test
            & ~d.study_accession.isin(d.loc[test, "study_accession"])
            & ~d.participant_id.isin(d.loc[test, "participant_id"])
        )
        if train.sum() >= 20 and test.sum() >= 5:
            yield vaccine, train, test


def select_alpha(d, x, y, tr):
    from sklearn.model_selection import GroupKFold

    ix = np.flatnonzero(tr)
    groups = d.study_accession.iloc[ix].to_numpy()
    alphas = (10, 100, 1000)
    losses = {a: [] for a in alphas}
    for a, b in GroupKFold(n_splits=min(3, len(set(groups)))).split(ix, groups=groups):
        train, val = ix[a], ix[b]
        z = preprocess(x, train)
        for alpha in alphas:
            pred = Ridge(alpha=alpha).fit(z[train], y[train]).predict(z[val])
            losses[alpha].append(np.mean(abs(pred - y[val])))
    return min(alphas, key=lambda a: np.mean(losses[a]))


def main():
    d, x, y = cohort()
    d.groupby(["study_accession", "vaccine"], observed=True).size().rename(
        "participants"
    ).to_csv(OUT / "cohort_audit.csv")
    rows = []
    for name, tr, te in folds(d):
        z = preprocess(x, tr)
        alpha = select_alpha(d, x, y, tr)
        scores = {
            "median": np.full(te.sum(), np.median(y[tr])),
            "ridge": Ridge(alpha=alpha).fit(z[tr], y[tr]).predict(z[te]),
            "trees": ExtraTreesRegressor(
                n_estimators=120, min_samples_leaf=5, random_state=42, n_jobs=2
            )
            .fit(z[tr], y[tr])
            .predict(z[te]),
        }
        for model, pred in scores.items():
            corr = spearmanr(y[te], pred).statistic if np.std(pred) > 1e-12 else np.nan
            rows.append(
                [
                    name,
                    model,
                    tr.sum(),
                    te.sum(),
                    d.loc[tr, "study_accession"].nunique(),
                    corr,
                    np.mean(abs(pred - y[te])),
                ]
            )
    df = pd.DataFrame(
        rows,
        columns=[
            "held_out_formulation",
            "model",
            "training_people",
            "test_people",
            "training_studies",
            "spearman",
            "MAE_log2_MFC",
        ],
    )
    df.to_csv(OUT / "fold_metrics.csv", index=False)
    df.pivot(
        index="held_out_formulation", columns="model", values="MAE_log2_MFC"
    ).plot.bar()
    plt.ylabel("Held-out MAE (log2 maximum fold change)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(OUT / "generalization.png", dpi=160)


if __name__ == "__main__":
    main()
