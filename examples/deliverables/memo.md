# Decision Memo | Customer Churn

## Question

Which customers should receive the next limited retention campaign?

## Evidence

On a fixed synthetic holdout set, logistic regression achieved 77.8% recall and
62.8% precision at a 0.40 threshold. Its F1 and ROC AUC were higher than those
of the small decision tree. The comparison used the same split, preprocessing
protocol, and threshold.

## Recommendation

Use the logistic regression as the ranking baseline. Keep the 0.40 threshold
for this teaching case, communicate the expected false-positive volume, and
simulate the campaign budget before making an operational decision.

## Monitoring

Track contract mix, missing charge values, prediction score distribution, and
realised churn after each campaign. Re-evaluate if the realised churn rate or
campaign capacity changes materially.

## Reproduction

Run `python scripts/build_examples.py` and open the customer-churn notebook or
the rendered case-lab page.
