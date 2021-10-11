import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score
from pmdarima.arima import auto_arima

# Read in data, and do minor transformations on data frame
sales_data = pd.read_csv("ChampagneSales.csv")
sales_data['Month'] = pd.to_datetime(sales_data['Month'])
sales_data.set_index('Month',inplace=True)

# Slice data into training and testing data sets
train = sales_data[:85]
test = sales_data[-20:]

# Create a model using auto_arima, using a seasonal fit, and noting that we're using monthly data (m=12)
arima_model = auto_arima(train, m=12, seasonal=True, trace=True)

# Predict 20 new values
predicted_data = arima_model.predict(n_periods = 20)

print(test.index)

# Create a new data frame using the predicted data
prediction = pd.DataFrame(predicted_data, index=test.index)
prediction.columns = ['predicted_sales']

# Compute an r2_score value for the prediction
test_data_for_rscore = test.copy()
test_data_for_rscore['predicted_sales'] = prediction
print(r2_score(test_data_for_rscore['Champagne sales'], test_data_for_rscore['predicted_sales']))

# Plot on a graph
plt.figure(figsize=(8,5))
plt.plot(train,label="Training")
plt.plot(test,label="Test")
plt.plot(prediction,label="Predicted")
plt.legend(loc = 'best')
plt.show()