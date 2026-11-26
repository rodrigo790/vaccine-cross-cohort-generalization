# Execution record

Execution date: 2026-11-26. Analysis completed with public research inputs. The exact input bytes are recorded in [the data manifest](data/sources.json). The reproduction commands are in [README.md](README.md).

Seven formulation-year groups supplied 365 PBMC participants. Mean held-out Spearman correlation was 0.065 for ridge and 0.013 for extra trees. The formulation-level table shows the variation hidden by these averages.

Some held-out formulations have only eight or nine people. Seasonal formulations share antigenic backgrounds. The design addresses transfer across represented formulations; extension to other vaccine platforms remains open.

[Repository and current commit history](https://github.com/rodrigo790/vaccine-cross-cohort-generalization/commits/main) · [Continuous integration](https://github.com/rodrigo790/vaccine-cross-cohort-generalization/actions)


The random split places participants from ten studies on both sides. Paired error intervals resample held-out studies and people. A fold with one study estimates within-study variability only. See [paired intervals](results/paired_error_intervals.csv).
