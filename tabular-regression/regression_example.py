import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np
import pandas as pd
# Load the data from the Excel file
file_path = os.environ.get('TABULAR_DATASET', 'data/input.xlsx')
data = pd.read_excel(file_path)
#data.head()
x = data.iloc[:, 0:8].values
y = data.iloc[:, 9].values
from sklearn.tree import DecisionTreeRegressor

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.15, random_state=42)
from sklearn.linear_model import LinearRegression

# Initialize the model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Calculate the mean squared error
mse = mean_squared_error(y_test, y_pred)
rf = mean_squared_error(y_test, y_pred)
rf_mae = mean_absolute_error(y_test, y_pred)
rf_r2 = r2_score(y_test, y_pred)
print(f'Mean Squared Error: {mse}')