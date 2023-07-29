import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

# Step 1: Read the data from the CSV file
data = pd.read_csv('nic_data.csv', parse_dates=['EntryDate'])

# Step 2: Preprocess the dataset
data['ModalPrice'] = pd.to_numeric(data['ModalPrice'], errors='coerce')

# Step 3: Filter the dataset by commodity name
def get_prices_by_commodity(commodity_name):
    return data[data['CommodityName'] == commodity_name]

# Step 4: Perform SARIMA modeling and prediction
def perform_sarima_prediction(commodity_name):
    commodity_data = get_prices_by_commodity(commodity_name)
    if len(commodity_data) > 0:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            
            model = SARIMAX(commodity_data['ModalPrice'], order=(1, 1, 1), seasonal_order=(1, 0, 0, 12))
            model_fit = model.fit(disp=False)
    
            # Forecast the prices for the next year
            next_year_forecast = model_fit.get_forecast(steps=12)
            forecasted_prices = next_year_forecast.predicted_mean
        
        market = commodity_data.iloc[-1]['MarketName']
        current_price_mean = commodity_data['ModalPrice'].mean()
        next_year_price = forecasted_prices.iloc[-1]
        
        return market, current_price_mean, next_year_price
    else:
        return None, None, None

