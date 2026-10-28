# Evaluation | Customer Churn

## Protocol

- Data split: 75% training, 25% holdout, stratified by churn
- Selection data: not separated from the demonstration split in this small case
- Confirmation data: the 25% holdout set
- Random seed: 42
- Metrics: accuracy, precision, recall, F1, ROC AUC
- Threshold: 0.40

## Results

| Model | Recall | Precision | F1 | ROC AUC |
| --- | --- | --- | --- | --- |
| Logistic regression | **77.8%** | 62.8% | **0.695** | **0.771** |
| Decision tree | 67.5% | 54.1% | 0.601 | 0.676 |

## Error analysis

The logistic model missed 28 churners and flagged 58 customers who stayed.
That trade-off is consistent with the lower-threshold decision rule, which
prefers additional recall when the campaign can absorb some wasted contacts.

## Decision

Use logistic regression as the baseline for this teaching case. Retain the
tree as a comparison, not as the selected model. Re-evaluate with a separate
tuning period and campaign-capacity simulation before any operational use.

## Done when

The report connects metrics to campaign errors and states what the evidence
does not establish.
