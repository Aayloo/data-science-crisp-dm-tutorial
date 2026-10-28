# Research Brief | Customer Churn

## Decision

- Decision owner: retention campaign manager
- Decision: which customers receive a limited retention offer
- Action: rank customers for the monthly campaign
- Decision date: month-end, before the next campaign

## Prediction target

- Target: `churned`
- Definition: customer leaves within the next 30 days
- Horizon: 30 days
- Information available: tenure, current monthly charge, support calls,
  usage hours, contract type, autopay status, and region

## Success criteria

- Baseline: contact customers ranked only by tenure
- Primary metric: recall at an acceptable campaign size
- Required improvement: more churned customers identified than the baseline
- Operational constraint: the campaign can contact 20% of customers
- False-positive cost: unnecessary discount or outreach
- False-negative cost: lost customer and future revenue

## Evidence boundary

- Training and validation: fixed synthetic teaching dataset
- Confirmation: one held-out 25% split
- Limitation: the result is pedagogical and not evidence about real customers

## Done when

The manager can state the decision, the deadline, the budget, and the metric.
