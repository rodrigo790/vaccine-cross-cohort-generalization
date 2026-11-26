# Analysis protocol

## Question

Can baseline blood expression rank antibody responses to a held-out influenza formulation?

## Population, analysis and validation

Keep one day-zero sample per participant, HAI fold change measured 21–35 days later, and passing sex-chromosome QC. Exclude every test study from development. Rank genes by training variance after requiring 95% coverage. Impute and scale within each fold. Tune ridge across three grouped development folds. Evaluate fixed-seed trees and training medians against the same people.

## Interpretation and scope

Some held-out formulations have only eight or nine people. Seasonal formulations share antigenic backgrounds. The design addresses transfer across represented formulations; extension to other vaccine platforms remains open.

## Primary output

[fold_metrics.csv](../results/fold_metrics.csv)

## Source

[Study or method](https://doi.org/10.6084/m9.figshare.17096978)
