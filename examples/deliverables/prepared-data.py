"""Completed preparation example for the synthetic churn case."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from tutorial.data import generate_churn_data

frame = generate_churn_data(seed=42)
X = frame.drop(columns="churned")
y = frame["churned"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

numeric_columns = [
    "tenure_months",
    "monthly_charge",
    "support_calls",
    "usage_hours",
]
categorical_columns = ["contract", "autopay", "region"]

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

# The downstream model Pipeline receives `preprocess` as its first step.
# Transformations are learned only when `.fit(X_train, y_train)` is called.
