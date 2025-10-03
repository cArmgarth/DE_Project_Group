import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# --- Load dataset ---
df = pd.read_csv("data/local_copy.csv")

# Features and targets
X = df.drop(columns=["date", "reddit_count", "twitter_count"])
y = df[["reddit_count", "twitter_count"]]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- Define pipeline ---
# StandardScaler → MultiOutputRegressor(Lasso)
lasso = MultiOutputRegressor(Lasso(max_iter=10000))
pipe = Pipeline([("scaler", StandardScaler()), ("model", lasso)])

# --- Parameter grid ---
# Note: parameters must be prefixed with "model__estimator__"
# because MultiOutputRegressor wraps Lasso
param_grid = {
    "model__estimator__alpha": [0.0001, 0.001, 0.01, 0.1, 1, 10],
    "model__estimator__fit_intercept": [True, False],
}

# --- Grid search ---
grid = GridSearchCV(pipe, param_grid, cv=3, scoring="neg_mean_squared_error")
grid.fit(X_train, y_train)

print("Best parameters:", grid.best_params_)
print("Best CV score (neg MSE):", grid.best_score_)

# --- Evaluate on test set ---
best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print("Test set MSE:", mse)

# --- Extract coefficients ---
# Each Lasso is accessible in best_model.named_steps["model"].estimators_
estimators = best_model.named_steps["model"].estimators_
for i, target in enumerate(y.columns):
    print(f"\nTarget: {target}")
    print("  Coefficients:", estimators[i].coef_)
    print("  Intercept:", estimators[i].intercept_)

# --- Visualization: true vs predicted scatter ---
fig, axes = plt.subplots(1, y.shape[1], figsize=(10, 4))

for i, col in enumerate(y.columns):
    true_vals = y_test[col].values
    pred_vals = y_pred[:, i]

    axes[i].scatter(true_vals, pred_vals, alpha=0.7, color="blue")
    axes[i].plot(
        [true_vals.min(), true_vals.max()],
        [true_vals.min(), true_vals.max()],
        "k--",
        lw=2,
    )
    axes[i].set_xlabel("True " + col)
    axes[i].set_ylabel("Predicted " + col)
    axes[i].set_title(col)

plt.tight_layout()
plt.show()
