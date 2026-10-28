"""Reproducible data-preparation plan.

Complete the TODOs without fitting transformations on the test set.
"""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# TODO: load the dataset.
frame = ...
X = ...
y = ...

# TODO: define whether a random, stratified, or chronological split is valid.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

numeric_columns = [...]
categorical_columns = [...]

preprocess = ColumnTransformer(
    [
        (
            "numeric",
            Pipeline(
                [
                    ("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                ]
            ),
            numeric_columns,
        ),
        (
            "categorical",
            Pipeline(
                [
                    ("impute", SimpleImputer(strategy="most_frequent")),
                    ("encode", OneHotEncoder(handle_unknown="ignore")),
                ]
            ),
            categorical_columns,
        ),
    ]
)

# TODO: fit the complete Pipeline on training data only.
# TODO: preserve random seeds, data snapshot rules, and row counts.
