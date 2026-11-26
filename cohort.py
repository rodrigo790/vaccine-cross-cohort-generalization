"""Read the pinned IS2 ExpressionSet, aligning assay columns to metadata by UID."""

import hashlib
import json
import zipfile
import shutil
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
import rdata
from inputs import CACHE

URL = "https://ndownloader.figshare.com/files/31615370"
MEMBER = "data/all_noNorm_withResponse_eset.rds"
EXPECTED = "850eb1275d9092c495ad152545f5cfea5d5c77edb1733e48f62e2321a09d8d45"


def cohort():
    CACHE.mkdir(exist_ok=True, parents=True)
    path = CACHE / Path(MEMBER).name
    if not path.exists():
        from remotezip import RemoteZip

        bundle = CACHE / "immunesignatures.zip"
        if bundle.exists():
            with bundle.open("rb") as stream:
                if (
                    hashlib.file_digest(stream, "md5").hexdigest()
                    != "6e29a2091e137003917e4558285d0f9b"
                ):
                    raise ValueError("Figshare archive checksum mismatch")
        archive_context = (
            zipfile.ZipFile(bundle) if bundle.exists() else RemoteZip(URL, timeout=180)
        )
        with (
            archive_context as archive,
            archive.open(MEMBER) as src,
            path.with_suffix(".tmp").open("wb") as out,
        ):
            shutil.copyfileobj(src, out)
        path.with_suffix(".tmp").replace(path)
    with path.open("rb") as f:
        digest = hashlib.file_digest(f, "sha256").hexdigest()
    if digest != EXPECTED:
        raise ValueError("Unexpected IS2 archive member SHA-256")
    Path("data/sources.json").write_text(
        json.dumps(
            dict(
                article=17096978,
                version=1,
                url=URL,
                member=MEMBER,
                sha256=digest,
                verified=str(date.today()),
            ),
            indent=2,
        )
    )
    obj = rdata.read_rds(path)
    frame = obj.phenoData.data.copy()
    assay = obj.assayData["exprs"]
    cols = pd.Index(assay.coords[assay.dims[1]].values)
    if not cols.is_unique or not frame.uid.is_unique:
        raise ValueError("Duplicate sample identifiers")
    keep = (
        (frame.cell_type == "PBMC")
        & (frame.study_time_collected == 0)
        & (frame.study_time_collected_unit == "Days")
        & (frame.assay == "hai")
        & (~frame.failedYchromQC)
        & frame.ImmResp_postVax_timepoint_MFC.between(21, 35)
        & (frame.MFC > 0)
    )
    d = (
        frame.loc[keep]
        .sort_values("uid")
        .drop_duplicates("participant_id")
        .reset_index(drop=True)
    )
    idx = cols.get_indexer(d.uid)
    if min(idx) < 0:
        raise ValueError("Unmatched biosample")
    return (
        d,
        np.asarray(assay.values[:, idx].T, dtype=float),
        np.log2(d.MFC.to_numpy(dtype=float)),
    )


def preprocess(x, train):
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import StandardScaler

    raw = x[train]
    valid = np.flatnonzero(np.isfinite(raw).mean(axis=0) >= 0.95)
    if not len(valid):
        raise ValueError("No adequately measured training features")
    selected = valid[np.argsort(np.nanvar(raw[:, valid], axis=0))[-64:]]
    imputer = SimpleImputer(strategy="median").fit(raw[:, selected])
    a = imputer.transform(x[:, selected])
    return StandardScaler().fit(a[train]).transform(a).clip(-8, 8)
