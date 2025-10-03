import joblib
import pandas as pd
from sklearn.linear_model import ElasticNet
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
    X, y, test_size=0.2, random_state=4333
)

# --- Define pipeline ---
enet = MultiOutputRegressor(ElasticNet(max_iter=10000))
pipe = Pipeline([("scaler", StandardScaler()), ("model", enet)])

# --- Parameter grid ---
# Parameters for the base estimator inside MultiOutputRegressor
param_grid = {
    "model__estimator__alpha": [0.001, 0.01, 0.1, 1, 10],
    # 0=ridge-like, 1=lasso-like
    "model__estimator__l1_ratio": [0.2, 0.5, 0.8],
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

joblib.dump(best_model, "model.joblib")
