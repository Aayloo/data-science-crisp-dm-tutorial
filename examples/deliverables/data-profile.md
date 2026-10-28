# Data Profile | Customer Churn

## Source and scope

- Source: deterministic synthetic generator in `src/tutorial/data.py`
- Extraction date: generated from the repository commit
- Population: 1,200 teaching customers
- Observation period: one cross-sectional snapshot
- Update frequency: not applicable

## Data dictionary

| Field | Meaning | Unit | Type | Available before decision? | Quality note |
| --- | --- | --- | --- | --- | --- |
| `tenure_months` | Time with provider | months | integer | Yes | No missing values |
| `monthly_charge` | Current monthly charge | currency units | float | Yes | 1.5% missing |
| `support_calls` | Recent support contacts | count | integer | Yes | No missing values |
| `usage_hours` | Recent usage | hours | float | Yes | No missing values |
| `contract` | Contract type | category | string | Yes | Month-to-month is most common |
| `autopay` | Autopayment status | category | string | Yes | 0.75% missing |
| `region` | Broad region | category | string | Yes | Four categories |
| `churned` | Churn outcome | binary | integer | No | 42.2% churn rate |

## Quality checks

- Rows: 1,200
- Columns: 8
- Duplicate records: none by construction
- Missing values: 18 in `monthly_charge`, 9 in `autopay`
- Target distribution: 42.2% churn
- Leakage review: `churned` is unavailable before the campaign; it must never be an input

## Done when

Every field has a documented meaning, type, timing, and quality decision.
