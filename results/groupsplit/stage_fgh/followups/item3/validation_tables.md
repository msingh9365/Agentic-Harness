### Item 3 budget grid: validation numbers of all candidates (5 seeds; group-split slice, 8,718 reports; the cell numbers are descriptive)

| lr | epochs | score = mean over the 4 cells of val pAUC@1e-2 | SE | min val AUC (all cells, seeds) | fn | ab | an | fb | note |
|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 1 | 0.5094 | 0.0197 | 0.9171 | 0.5610 | 0.4783 | 0.6099 | 0.3884 | **CHOSEN** |
| 0.001 | 2 | 0.4950 | 0.0138 | 0.9273 | 0.5324 | 0.4656 | 0.5860 | 0.3961 | tied |
| 0.001 | 3 | 0.4978 | 0.0124 | 0.9203 | 0.5265 | 0.4647 | 0.5638 | 0.4362 | tied |
| 0.002 | 1 | 0.5012 | 0.0122 | 0.9326 | 0.5194 | 0.4618 | 0.5610 | 0.4625 | tied |
| 0.002 | 2 | 0.5129 | 0.0207 | 0.9022 | 0.4774 | 0.5013 | 0.5983 | 0.4748 | best |
| 0.002 | 3 | 0.4990 | 0.0105 | 0.8815 | 0.4982 | 0.4538 | 0.5650 | 0.4789 | tied |

**Chosen budget for all four cells: lr 0.001, 1 epoch(s)** (best by score: lr 0.002, 2 epoch(s), 0.5129, SE 0.0207; tied with best: lr 0.001/1, lr 0.001/2, lr 0.001/3, lr 0.002/1, lr 0.002/2, lr 0.002/3)

