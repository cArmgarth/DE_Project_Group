import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV, train_test_split

df = pd.read_csv("data/local_copy.csv")

X = df.drop(columns=["date", "reddit_count", "twitter_count"])
y = df[["reddit_count", "twitter_count"]]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

param_grid = {
    "alpha": [0.01, 0.05, 0.1, 0.5, 1],
    "fit_intercept": [True, False],
    "solver": ["auto", "svd", "lsqr", "saga"],
}

model = Ridge()

grid = GridSearchCV(model, param_grid, cv=3, scoring="neg_mean_squared_error")
grid.fit(X_train, y_train)

print("Best parameters:", grid.best_params_)
print("Best CV score (negative MSE):", grid.best_score_)

best_model = grid.best_estimator_
# Predictions
y_pred = best_model.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
print("Mean Squared Error:", mse)
print("Coefficients:", best_model.coef_)
print("Intercept:", best_model.intercept_)

fig, axes = plt.subplots(1, y.shape[1], figsize=(10, 4))

for i, col in enumerate(y.columns):
    true_vals = y_test[col].values
    pred_vals = y_pred[:, i]

    axes[i].scatter(true_vals, pred_vals, alpha=0.7)
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
