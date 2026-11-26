import pandas as pd, unittest
from analysis import folds


class LeakTest(unittest.TestCase):
    def test_shared_study_excluded(self):
        d = pd.DataFrame(
            {
                "vaccine": ["a"] * 6 + ["b"] * 30,
                "study_accession": ["x"] * 8 + ["y"] * 28,
                "participant_id": range(36),
            }
        )
        _, tr, te = next(folds(d))
        self.assertFalse(set(d.study_accession[tr]) & set(d.study_accession[te]))
        self.assertEqual(tr.sum(), 28)
