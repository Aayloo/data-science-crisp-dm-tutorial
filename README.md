# Data Science Workflow: A Reproducible CRISP-DM Tutorial

**从问题到决策，而不是从模型开始。**

A compact, hands-on Data Science tutorial for readers who already know basic
Python. It follows the six phases of **CRISP-DM** and applies the same workflow
to three small, reproducible cases:

- customer churn classification;
- house-price regression;
- monthly demand forecasting.

The tutorial takes roughly **4–6 hours** and deliberately keeps the model set
small. The goal is to demonstrate the process: asking a useful question,
understanding data, preventing leakage, establishing a baseline, evaluating
honestly, and communicating a result.

## Open the tutorial

- Tutorial: https://aayloo.github.io/data-science-crisp-dm-tutorial/
- Repository: https://github.com/Aayloo/data-science-crisp-dm-tutorial

## What this project demonstrates

- how to translate a vague idea into a testable decision problem;
- how to audit a dataset before modelling;
- how to keep preprocessing inside a scikit-learn pipeline;
- why a simple baseline must come before a more complex model;
- how to evaluate classification, regression, and time-series results;
- how to package notebooks, tests, figures, and communication together.

This is a teaching project. The synthetic datasets make the examples fast,
portable, and reproducible; they are not evidence about real customers,
property prices, or demand.

## Contents

The single-page course contains six teaching sections and three cases:

1. Business Understanding
2. Data Understanding
3. Data Preparation
4. Modeling
5. Evaluation
6. Deployment and Communication
7. Customer churn case
8. House-price case
9. Demand-forecasting case
10. Project review checklist

Every teaching section includes learning objectives, conceptual guidance,
executable code, a checkpoint, and a concrete deliverable.

## Run locally

Requirements: Python 3.10+ and the packages declared in `pyproject.toml`.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/build_examples.py
python -m http.server 8000
```

Then open <http://localhost:8000>.

For a local layout and interaction check with Chrome or Edge installed:

```bash
node scripts/qa_layout.mjs
```

It checks 1440 px, 768 px, and 390 px layouts, broken images, unresolved
metrics, missing anchors, browser errors, and the mobile navigation.

The build script regenerates:

- synthetic datasets under `data/`;
- charts under `assets/img/`;
- metrics under `assets/data/results.json`;
- browser-ready metrics under `assets/data/results.js`.

Generated datasets are intentionally excluded from Git. The fixed random seeds
make them reproducible.

## Project structure

```text
.
├── index.html                  # complete tutorial website
├── assets/
│   ├── css/style.css           # visual system and responsive layout
│   ├── js/site.js              # navigation, progress, copy, metrics
│   ├── img/                    # generated figures
│   └── data/                   # generated results used by the page
├── src/tutorial/
│   ├── data.py                 # deterministic synthetic data
│   ├── examples.py             # three executable cases
│   └── plots.py                # publication-style figures
├── notebooks/                  # executed, learner-facing notebooks
├── scripts/build_examples.py   # regenerate all case artifacts
├── tests/                      # reproducibility and metric checks
└── references/                 # sources and further reading
```

## Design and accessibility

The site uses a university-tutorial layout with a visible chapter structure,
keyboard-accessible navigation, visible focus states, reduced-motion support,
responsive tables, descriptive figure captions, and no external frontend
dependencies.

## References

See [references/sources.md](references/sources.md) for the CRISP-DM source,
library documentation, and related open educational projects.

## License

Released under the [MIT License](LICENSE).
