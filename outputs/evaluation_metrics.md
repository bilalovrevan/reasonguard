# ReasonGuard Evaluation Metrics

- Sample count: 200
- Accuracy: 0.3000
- Macro precision: 0.2736
- Macro recall: 0.2401
- Macro F1: 0.1871
- Cohen's Kappa: 0.1602

## Per-class metrics

| Class | Precision | Recall | F1 | Support | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NONE | 0.2625 | 0.4286 | 0.3256 | 49 | 21 | 59 | 28 |
| V1 | 0.9000 | 0.0918 | 0.1667 | 98 | 9 | 1 | 89 |
| V2 | 0.0000 | 0.0000 | 0.0000 | 17 | 0 | 0 | 17 |
| V3 | 0.0000 | 0.0000 | 0.0000 | 2 | 0 | 0 | 2 |
| V4 | 0.4792 | 0.9200 | 0.6301 | 25 | 23 | 25 | 2 |
| V5 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | 0 |

## Confusion matrix (rows = human label, columns = machine label)

| true \ predicted | MIXED | NONE | V1 | V2 | V3 | V4 | V5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MIXED | 7 | 0 | 0 | 0 | 0 | 2 | 0 |
| NONE | 21 | 21 | 0 | 0 | 0 | 7 | 0 |
| V1 | 22 | 54 | 9 | 0 | 0 | 13 | 0 |
| V2 | 10 | 3 | 1 | 0 | 0 | 3 | 0 |
| V3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| V4 | 0 | 2 | 0 | 0 | 0 | 23 | 0 |
| V5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
